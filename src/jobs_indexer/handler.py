from __future__ import annotations

import logging
from typing import Any, Dict, List

from pydantic import ValidationError

from .config import Settings
from .logging import setup_logger
from .models import Job
from .opensearch_client import OpenSearchClient, OpenSearchError
from .sqs_parser import BodyParsingError, extract_job_payload
from .transformer import transform_job_to_index


def _build_client(settings: Settings, logger: logging.Logger) -> OpenSearchClient:
    return OpenSearchClient(
        endpoint=settings.opensearch_endpoint,
        index=settings.opensearch_index,
        region=settings.aws_region,
        use_aws_auth=settings.opensearch_aws_auth,
        username=settings.opensearch_username,
        password=settings.opensearch_password,
        logger=logger,
    )


def _process_record(
    record: Dict[str, Any], client: OpenSearchClient, logger: logging.Logger
) -> bool:
    message_id = record.get("messageId")
    body = record.get("body", "")
    try:
        raw_job = extract_job_payload(body)
        job = Job.model_validate(raw_job)
        job_index = transform_job_to_index(job)
        client.upsert_document(document_id=job_index.id, document=job_index.model_dump())
        logger.info("Record processed", extra={"messageId": message_id})
        return True
    except (BodyParsingError, ValidationError) as exc:
        logger.error("Validation failed", extra={"messageId": message_id, "error": str(exc)})
    except OpenSearchError as exc:
        logger.error("OpenSearch failure", extra={"messageId": message_id, "error": str(exc)})
    except Exception:  # pragma: no cover - safeguard
        logger.exception("Unhandled error while processing record", extra={"messageId": message_id})
    return False


def lambda_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, List[Dict[str, str]]]:
    settings = Settings.from_env()
    logger = setup_logger(settings.log_level)
    client = _build_client(settings, logger)

    failures: List[Dict[str, str]] = []
    records = event.get("Records", []) or []
    for record in records:
        success = _process_record(record, client, logger)
        if not success and record.get("messageId"):
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}
