from __future__ import annotations

import time
from typing import Dict, List

import boto3

from .config import Settings
from .handler import _build_client, _process_record
from .logging import setup_logger


def poll_queue_once(settings: Settings, client, logger) -> List[Dict[str, str]]:
    sqs = boto3.client("sqs", region_name=settings.aws_region)
    response = sqs.receive_message(
        QueueUrl=settings.sqs_queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=5,
    )
    failures: List[Dict[str, str]] = []
    for record in response.get("Messages", []):
        wrapper = {
            "messageId": record.get("MessageId"),
            "body": record.get("Body", ""),
        }
        success = _process_record(wrapper, client, logger)
        if not success and wrapper.get("messageId"):
            failures.append({"itemIdentifier": wrapper["messageId"]})
    return failures


def main() -> None:
    settings = Settings.from_env()
    if not settings.sqs_queue_url:
        raise SystemExit("SQS_QUEUE_URL must be set for local polling mode")

    logger = setup_logger(settings.log_level)
    client = _build_client(settings, logger)

    logger.info("Starting local runner", extra={"queue": settings.sqs_queue_url})
    while True:
        poll_queue_once(settings, client, logger)
        time.sleep(1)


if __name__ == "__main__":
    main()
