# Jobs-Indexer

Python 3.12 AWS Lambda that consumes SQS messages, validates **Job** payloads using the
[`schemas/indexer/openapi.yaml`](schemas/indexer/openapi.yaml) contract, transforms them into
`JobIndex` documents, and upserts into OpenSearch. The same code can run locally (LocalStack +
OpenSearch) and in AWS.

## Architecture

```
SQS (from Jobs-API) -> Lambda (jobs_indexer.handler.lambda_handler) -> OpenSearch index
```

- Message envelopes supported:
  - body is a `Job` JSON object
  - body is `{ "job": { ... } }`
  - SNS fan-out: body is `{ "Message": "<stringified Job or {job: ...}>" }`
- Partial batch failures are returned in the Lambda response so only failing messages are retried.
- Validation and transformation follow the OpenAPI schemas for `Job` and `JobIndex`.
- OpenSearch upserts use `id` as the document ID. SigV4 signing can be enabled for AWS-hosted
  domains; basic auth is optional for local clusters.

## Requirements

- Python 3.12 (selected for AWS Lambda compatibility and long-term support)
- OpenSearch endpoint (AWS-managed or local)
- SQS queue delivering Job messages

## Project layout

```
src/jobs_indexer/    # Lambda handler and supporting modules
schemas/indexer/     # OpenAPI schema (authoritative)
samples/             # Example Job payload
scripts/             # Local helper scripts (create queue, publish messages)
tests/               # Pytest suite
docker-compose.yml   # Local OpenSearch + LocalStack + runner
```

## Installation

```bash
pip install poetry
poetry install
```

Run linters/tests:

```bash
poetry run ruff check
poetry run pytest
```

## Environment variables

| Name | Description |
| --- | --- |
| `AWS_REGION` | AWS region (default `us-east-1`) |
| `OPENSEARCH_ENDPOINT` | Base URL, e.g. `https://search-domain.region.es.amazonaws.com` or `http://localhost:9200` |
| `OPENSEARCH_INDEX` | Index name (default `jobs`) |
| `OPENSEARCH_AWS_AUTH` | `true` to enable SigV4 signing |
| `OPENSEARCH_USERNAME` / `OPENSEARCH_PASSWORD` | Optional basic auth for local clusters |
| `LOG_LEVEL` | `DEBUG`, `INFO`, etc. |
| `SQS_QUEUE_URL` | Required for local runner (not needed inside Lambda) |

See [.env.example](.env.example) for a starting point.

## Lambda handler

Entry point: `jobs_indexer.handler.lambda_handler`

Processing steps per record:
1. Parse body (direct Job, `{job: ...}`, or SNS `Message` wrapping).
2. Validate against `Job` schema (Pydantic v2).
3. Transform to `JobIndex`, dropping fields not present in the index shape and normalizing types
   (dates remain date-time strings; location supports objects or arrays; salary is a structured
   object).
4. Validate `JobIndex`.
5. Upsert into OpenSearch using document ID = `id`.
6. Collect failures to return `{"batchItemFailures": [{"itemIdentifier": "<messageId>"}]}`.

## Message body examples

Direct Job:
```json
{
  "id": "job-123",
  "title": "Senior Backend Engineer",
  "companyName": "Cabmark"
}
```

Envelope with job field:
```json
{
  "job": {
    "id": "job-123",
    "title": "Senior Backend Engineer",
    "companyName": "Cabmark"
  }
}
```

SNS -> SQS:
```json
{
  "Message": "{\"id\":\"job-123\",\"title\":\"Senior Backend Engineer\",\"companyName\":\"Cabmark\"}"
}
```

## Local development (docker-compose)

1. Copy `.env.example` to `.env` and adjust as needed.
2. Start dependencies and runner:
   ```bash
   docker compose up --build
   ```
3. Create the queue (inside the repo root):
   ```bash
   AWS_ENDPOINT_URL=http://localhost:4566 AWS_REGION=us-east-1 python scripts/create_queue.py
   ```
4. Update `.env` with the printed `SQS_QUEUE_URL` if it differs.
5. Publish a sample message:
   ```bash
   AWS_ENDPOINT_URL=http://localhost:4566 AWS_REGION=us-east-1 \
   SQS_QUEUE_URL=http://localhost:4566/000000000000/jobs-indexer-queue \
   python scripts/publish_sample_job.py
   ```
6. Verify in OpenSearch:
   ```bash
   curl -s http://localhost:9200/jobs/_search | jq '.hits.hits'
   ```

Local runner (`docker compose` `indexer-runner` service) polls SQS and uses the same code path as
Lambda to process messages.

## Deploying to AWS (high level)

1. Build the package (e.g., `pip install . -t build/ && zip -r function.zip build/` or with your CI).
2. Create a Lambda function using runtime `python3.12`, handler
   `jobs_indexer.handler.lambda_handler`, and set environment variables above.
3. Grant IAM permissions:
   - `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes` on the source queue.
   - `es:ESHttp*` (or least-privilege equivalent) for the target OpenSearch domain.
4. Create an event source mapping from the SQS queue to the Lambda; configure a DLQ for resiliency.
5. If using AWS-managed OpenSearch, set `OPENSEARCH_AWS_AUTH=true`; otherwise provide basic auth if
   required.

## Transformation rules

- Fields present in both `Job` and `JobIndex` are copied directly.
- Fields not in `JobIndex` (e.g., `applyUrl`, `applyDetail`, `contacts`) are dropped.
- Location supports an object or arrays of objects/strings.
- Salary is preserved as an object (`minAmount`, `maxAmount`, `currency`, `period`).
- Hook `apply_index_enhancements` is provided for future derived/index-optimized fields.

## Testing

```bash
poetry run pytest
```

## Notes

- Logging uses structured JSON for easy ingestion.
- OpenSearch requests log status codes only (no full payloads) to avoid leaking PII.
