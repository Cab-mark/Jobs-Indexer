from __future__ import annotations

import logging
from typing import Optional, Union
from urllib.parse import quote

import boto3
import requests
from requests.auth import HTTPBasicAuth
from requests_aws4auth import AWS4Auth


class OpenSearchError(Exception):
    """Raised when an OpenSearch operation fails."""


class OpenSearchClient:
    def __init__(
        self,
        endpoint: str,
        index: str,
        region: str,
        use_aws_auth: bool = False,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 10,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.index = index
        self.region = region
        self.use_aws_auth = use_aws_auth
        self.timeout = timeout
        self.logger = logger or logging.getLogger("jobs-indexer")
        self._session = requests.Session()
        self._auth = self._build_auth(username, password)

    def _build_auth(
        self, username: Optional[str], password: Optional[str]
    ) -> Optional[Union[HTTPBasicAuth, AWS4Auth]]:
        if self.use_aws_auth:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials is None:
                raise OpenSearchError("AWS credentials not available for SigV4 signing")
            frozen = credentials.get_frozen_credentials()
            return AWS4Auth(
                frozen.access_key,
                frozen.secret_key,
                self.region,
                "es",
                session_token=frozen.token,
            )
        if username and password:
            return HTTPBasicAuth(username, password)
        return None

    def upsert_document(self, document_id: str, document: dict) -> None:
        if not self.endpoint:
            raise OpenSearchError("OPENSEARCH_ENDPOINT is not configured")
        if not document_id or "/" in document_id or ".." in document_id:
            raise OpenSearchError("Invalid document id")

        url = f"{self.endpoint}/{quote(self.index)}/_doc/{quote(document_id)}"
        response = self._session.put(
            url,
            json=document,
            timeout=self.timeout,
            auth=self._auth,
            headers={"Accept": "application/json"},
        )
        if response.status_code not in (200, 201):
            self.logger.error(
                "OpenSearch upsert failed",
                extra={"status": response.status_code, "documentId": document_id},
            )
            raise OpenSearchError(
                f"Failed to upsert document {document_id}: {response.status_code}"
            )
        self.logger.info(
            "OpenSearch upsert succeeded",
            extra={"documentId": document_id, "status": response.status_code},
        )
