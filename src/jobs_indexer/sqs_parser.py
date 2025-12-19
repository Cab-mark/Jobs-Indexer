from __future__ import annotations

import json
from typing import Any


class BodyParsingError(Exception):
    """Raised when a message body cannot be parsed into a Job payload."""


def _maybe_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def extract_job_payload(body: str) -> Any:
    """
    Extract the Job payload from common SQS/SNS body shapes.

    Supported:
    - Body contains the Job JSON directly
    - Body contains {"job": {...}}
    - Body contains SNS envelope {"Message": "..."} (stringified JSON)
    """
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise BodyParsingError("Body is not valid JSON") from exc

    # SNS -> SQS pattern: Message holds the original payload (often a string)
    if isinstance(parsed, dict) and "Message" in parsed:
        parsed = _maybe_json(parsed["Message"])

    if isinstance(parsed, dict) and "job" in parsed:
        return _maybe_json(parsed["job"])

    if isinstance(parsed, dict):
        return parsed

    raise BodyParsingError("Unsupported message envelope")
