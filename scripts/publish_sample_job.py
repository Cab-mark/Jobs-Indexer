#!/usr/bin/env python
import json
import os
from pathlib import Path

import boto3


def main() -> None:
    region = os.environ.get("AWS_REGION", "us-east-1")
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    queue_url = os.environ.get("SQS_QUEUE_URL")
    if not queue_url:
        raise SystemExit("SQS_QUEUE_URL must be set")

    sample_path = Path(__file__).resolve().parent.parent / "samples" / "job.json"
    with sample_path.open() as f:
        payload = json.load(f)

    sqs = boto3.client("sqs", region_name=region, endpoint_url=endpoint_url)
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(payload))
    print(f"MessageId: {response['MessageId']}")


if __name__ == "__main__":
    main()
