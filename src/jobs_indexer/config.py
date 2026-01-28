from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Settings:
    aws_region: str
    opensearch_endpoint: str
    opensearch_index: str
    opensearch_aws_auth: bool
    opensearch_username: Optional[str]
    opensearch_password: Optional[str]
    log_level: str
    sqs_queue_url: Optional[str]

    @staticmethod
    def from_env() -> "Settings":
        return Settings(
            aws_region=os.environ.get("AWS_REGION", "us-east-1"),
            opensearch_endpoint=os.environ.get("OPENSEARCH_ENDPOINT", "").rstrip("/"),
            opensearch_index=os.environ.get("OPENSEARCH_INDEX", "jobs"),
            opensearch_aws_auth=os.environ.get("OPENSEARCH_AWS_AUTH", "false").lower()
            in ("1", "true", "yes"),
            opensearch_username=os.environ.get("OPENSEARCH_USERNAME"),
            opensearch_password=os.environ.get("OPENSEARCH_PASSWORD"),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            sqs_queue_url=os.environ.get("SQS_QUEUE_URL"),
        )
