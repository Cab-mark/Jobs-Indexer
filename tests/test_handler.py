from jobs_indexer import handler


class DummyClient:
    def __init__(self):
        self.upserts = []

    def upsert_document(self, document_id: str, document: dict) -> None:
        self.upserts.append((document_id, document))


def test_process_record_calls_opensearch(monkeypatch):
    client = DummyClient()
    logger = handler.setup_logger("DEBUG")
    record = {
        "messageId": "msg-1",
        "body": '{"id":"1","title":"Engineer","companyName":"Cabmark"}',
    }
    ok = handler._process_record(record, client, logger)
    assert ok is True
    assert client.upserts[0][0] == "1"
    assert client.upserts[0][1]["title"] == "Engineer"


def test_lambda_handler_marks_failed(monkeypatch):
    # Ensure env has minimal config
    monkeypatch.setenv("OPENSEARCH_ENDPOINT", "http://localhost:9200")
    monkeypatch.setenv("OPENSEARCH_INDEX", "jobs")
    # Build a dummy client so we do not hit the network
    dummy_client = DummyClient()
    monkeypatch.setattr(handler, "_build_client", lambda settings, logger: dummy_client)

    event = {
        "Records": [
            {
                "messageId": "fail-1",
                "body": '{"title":"Missing id","companyName":"Cabmark"}',
            },
            {
                "messageId": "ok-1",
                "body": '{"id":"2","title":"Good","companyName":"Cabmark"}',
            },
        ]
    }

    result = handler.lambda_handler(event, None)
    assert result["batchItemFailures"] == [{"itemIdentifier": "fail-1"}]
    assert dummy_client.upserts[0][0] == "2"
