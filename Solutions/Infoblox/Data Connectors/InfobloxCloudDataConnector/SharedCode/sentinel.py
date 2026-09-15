"""Ingest data into Microsoft Sentinel via the Log Ingestion API (Data Collection Endpoint / Data Collection Rule)."""

import inspect
from azure.core.exceptions import HttpResponseError
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from azure.monitor.ingestion import LogsIngestionClient
from .logger import applogger
from .infoblox_exception import InfobloxException
from ..SharedCode import consts

_credential = None
_clients_by_endpoint = {}


def _get_credential():
    """Build (once) and return the AAD client-secret credential used to call the Log Ingestion API.

    Picks the Azure Government authority when the DCR/DCE scope (consts.SCOPE) points at a
    ".us" endpoint, so the same code path works for both Azure Public and Gov Cloud tenants.
    """
    global _credential
    if _credential is None:
        if ".us" in consts.SCOPE:
            _credential = ClientSecretCredential(
                tenant_id=consts.AZURE_TENANT_ID,
                client_id=consts.AZURE_CLIENT_ID,
                client_secret=consts.AZURE_CLIENT_SECRET,
                authority=AzureAuthorityHosts.AZURE_GOVERNMENT,
            )
        else:
            _credential = ClientSecretCredential(
                tenant_id=consts.AZURE_TENANT_ID,
                client_id=consts.AZURE_CLIENT_ID,
                client_secret=consts.AZURE_CLIENT_SECRET,
            )
    return _credential


def _get_client(dce_endpoint):
    """Build (once per DCE endpoint) and return a LogsIngestionClient bound to that endpoint.

    Args:
        dce_endpoint (str): Logs ingestion endpoint URL of the Data Collection Endpoint.

    Returns:
        LogsIngestionClient: cached client for the given endpoint.
    """
    if dce_endpoint not in _clients_by_endpoint:
        _clients_by_endpoint[dce_endpoint] = LogsIngestionClient(
            endpoint=dce_endpoint,
            credential=_get_credential(),
            credential_scopes=[consts.SCOPE],
            logging_enable=False,
        )
    return _clients_by_endpoint[dce_endpoint]


def ingest_logs(records, table_key):
    """Ingest a list of records into Sentinel via the Log Ingestion API (DCE/DCR), replacing the legacy \
    HTTP Data Collector API (`post_data`/HMAC signing).

    Args:
        records (list): List of JSON-serializable dict records. Each dict must match the columns declared
            on the target DCR stream (see consts.DCR_STREAMS / the DCR ARM template).
        table_key (str): Key into consts.DCR_STREAMS identifying which DCE/DCR/stream to ingest into.

    Returns:
        None

    Raises:
        InfobloxException: If table_key has no DCE/DCR configured, or the upload fails.
    """
    __method_name = inspect.currentframe().f_code.co_name
    if not records:
        return
    stream_config = consts.DCR_STREAMS.get(table_key)
    if not stream_config or not stream_config.get("immutable_id") or not stream_config.get("endpoint"):
        message = "Missing DCE/DCR configuration for table_key={}".format(table_key)
        applogger.error(
            "{}(method={}) : {}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                message,
            )
        )
        raise InfobloxException(message)
    try:
        client = _get_client(stream_config["endpoint"])
        client.upload(
            rule_id=stream_config["immutable_id"],
            stream_name=stream_config["stream"],
            logs=records,
        )
        applogger.debug(
            "{}(method={}) : Ingested {} record(s) into stream={} via Log Ingestion API.".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                len(records),
                stream_config["stream"],
            )
        )
    except HttpResponseError as error:
        applogger.error(
            "{}(method={}) : Log Ingestion API error for table_key={} : Error-{}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                table_key,
                error,
            )
        )
        raise InfobloxException(str(error)) from error
    except Exception as error:
        applogger.error(
            "{}(method={}) : Unexpected error for table_key={} : Error-{}".format(
                consts.LOGS_STARTS_WITH,
                __method_name,
                table_key,
                error,
            )
        )
        raise InfobloxException(str(error)) from error
