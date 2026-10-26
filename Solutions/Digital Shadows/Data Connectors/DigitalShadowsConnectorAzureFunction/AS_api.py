""" Microsoft Sentinel ingestion client — Logs Ingestion API (Phase 1 / GPB-658420). """
import logging
import requests
from azure.identity import DefaultAzureCredential

logger = logging.getLogger("AS_api")

LOGS_INGESTION_SCOPE = "https://monitor.azure.com/.default"
API_VERSION = "2023-01-01"


class logs_api:
    """
    Posts records to a Data Collection Endpoint (DCE) routed by a
    Data Collection Rule (DCR) into the target Log Analytics table.
    Auth is via Managed Identity (DefaultAzureCredential).
    """

    def __init__(self, dce_url, dcr_immutable_id, stream_name):
        self.dce_url = dce_url.rstrip("/")
        self.dcr_immutable_id = dcr_immutable_id
        self.stream_name = stream_name
        self._credential = DefaultAzureCredential()
        self._cached_token = None

    def _get_token(self):
        token = self._cached_token
        if token is None or token.expires_on - 60 < _now_epoch():
            token = self._credential.get_token(LOGS_INGESTION_SCOPE)
            self._cached_token = token
        return token.token

    def post_data(self, body, log_type=None):
        """
        Send a JSON body (a list of records, serialized) through the DCR.
        `log_type` is accepted for call-site compatibility but ignored — the
        destination table is encoded in the DCR + stream_name.
        """
        uri = (
            f"{self.dce_url}/dataCollectionRules/"
            f"{self.dcr_immutable_id}/streams/{self.stream_name}"
            f"?api-version={API_VERSION}"
        )
        headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }
        response = requests.post(uri, data=body, headers=headers, timeout=60)
        response.raise_for_status()
        logger.info("Accepted")


def _now_epoch():
    import time
    return int(time.time())


class management_api:
    """ kept for backwards compatibility with old import paths; unused. """
    pass
