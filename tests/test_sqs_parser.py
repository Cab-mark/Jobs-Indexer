import json

import pytest

from jobs_indexer.sqs_parser import BodyParsingError, extract_job_payload


def test_extract_direct_job():
    body = json.dumps({"id": "1", "title": "t", "companyName": "c"})
    assert extract_job_payload(body)["id"] == "1"


def test_extract_job_envelope():
    body = json.dumps({"job": {"id": "2", "title": "t", "companyName": "c"}})
    assert extract_job_payload(body)["id"] == "2"


def test_extract_sns_wrapped():
    inner = json.dumps({"id": "3", "title": "t", "companyName": "c"})
    body = json.dumps({"Message": inner})
    assert extract_job_payload(body)["id"] == "3"


def test_extract_invalid_json():
    with pytest.raises(BodyParsingError):
        extract_job_payload("not-json")
