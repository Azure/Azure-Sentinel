"""Constants file."""
import os

# consts for logging
NETSKOPE_TO_SENTINEL = "NetskopeToSentinel"
NETSKOPE_TO_AZURE_STORAGE = "NetskopeToAzureStorage"
LOGS_STARTS_WITH = "NetskopeDataConnector"
LOG_LEVEL = os.environ.get("Log_Level", "")

# consts for state_manager
CONNECTION_STRING = os.environ.get("ConnectionString", "")

# consts for netskope API

# *************************#
# Alert Type constants     #
# *************************#
ALERTS_URL = "https://{hostname}/api/v2/events/dataexport/alerts/{sub_type}?index={iterator_name}&operation={operation}"
# *************************#
# Event Type constants     #
# *************************#
EVENTS_URL = "https://{hostname}/api/v2/events/dataexport/events/{sub_type}?index={iterator_name}&operation={operation}"
EVENTS_LIST = {"page", "application", "incident", "audit", "infrastructure", "network", "connection"}
DATA_COLLECTION_TIMEOUT = 570
DIFFERENCE_BETWEEN_ITERATORS_IN_SECONDS = 100
URL = {"events": EVENTS_URL, "alerts": ALERTS_URL}

NETSKOPE_HOSTNAME = os.environ.get("NetskopeHostname", "")
NETSKOPE_TOKEN = os.environ.get("NetskopeToken", "")

# constants for state manager to sentinel
WORKSPACE_KEY = os.environ.get("WorkspaceKey", "")
WORKSPACE_ID = os.environ.get("WorkspaceId", "")
NETSKOPE_AZURE_STORAGE_TO_SENTINEL = "NetskopeAzureStorageToSentinel"
ORIGINAL_INDEX = 15000000
SHARE_NAME = os.environ.get("ShareName", "").replace(" ", "")
# Remove duplicated constants
NETSKOPE_REMOVE_DUPLICATES = "NetskopeRemoveDuplicatesFromStorage"

# constants for WebTx metrics
WEBTX_METRICS_URL = "https://{hostname}/api/v2/events/metrics/transactionevents"
NETSKOPE_WEBTX = "Netskope_WebTx_metrics"
LOG_TYPE = "Netskope_WebTx_metrics"
HOURS = 24
DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"  # sample : Mon, 19 Feb 2024 07:53:02 GMT
