"""This file contains all constants."""
import os

LOGS_STARTS_WITH = "Rubrik"
LOG_FORMAT = "{} {}: (method = {}) : {}"
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.environ.get("LogLevel", "")
FUNCTION_APP_TIMEOUT_SECONDS = 570

# Custom log table names (workspace tables carry the _CL suffix)
ANOMALY_LOG_TYPE = os.environ.get("Anomalies_table_name", "Rubrik_Anomaly_Data_CL")
RANSOMWARE_LOG_TYPE = os.environ.get("RansomwareAnalysis_table_name", "Rubrik_Ransomware_Data_CL")
THREATHUNT_LOG_TYPE = os.environ.get("ThreatHunts_table_name", "Rubrik_ThreatHunt_Data_CL")
EVENTS_LOG_TYPE = os.environ.get("Events_table_name", "Rubrik_Events_Data_CL")
VIOLATION_LOG_TYPE = os.environ.get("Violation_table_name", "Rubrik_Violation_Data_CL")

# DCR stream names (Custom-{TableName})
ANOMALY_STREAM = "Custom-Rubrik_Anomaly_Data_CL"
RANSOMWARE_STREAM = "Custom-Rubrik_Ransomware_Data_CL"
THREATHUNT_STREAM = "Custom-Rubrik_ThreatHunt_Data_CL"
EVENTS_STREAM = "Custom-Rubrik_Events_Data_CL"
VIOLATION_STREAM = "Custom-Rubrik_Violation_Data_CL"

# Log Ingestion API configuration
AZURE_DATA_COLLECTION_ENDPOINT = os.environ.get("AZURE_DATA_COLLECTION_ENDPOINT")
DCR_WEBHOOK_RULE_ID = os.environ.get("DCR_WEBHOOK_RULE_ID")
DCR_EVENTS_RULE_ID = os.environ.get("DCR_EVENTS_RULE_ID")
SCOPE = os.environ.get("SCOPE", "https://monitor.azure.com//.default")

# Rubrik Security Cloud (RSC) API configuration — used by the Violation classification gate
RUBRIK_INSTANCE_URL = os.environ.get("RubrikInstanceUrl")
RUBRIK_CLIENT_ID = os.environ.get("RubrikClientId")
RUBRIK_CLIENT_SECRET = os.environ.get("RubrikClientSecret")
RSC_HTTP_TIMEOUT = 60

RSC_RESOLVE_SNAPSHOT_QUERY = (
    "query ResolveSnapshot($snappableId: String!, $beforeTime: DateTime!) "
    "{ allSnapshotsClosestToPointInTime(snappableIds: [$snappableId], beforeTime: $beforeTime) "
    "{ snappableId error snapshot { id date } } }"
)

RSC_HIT_COUNT_QUERY = (
    "query ObjectHitCountQuery($snappableFid: String!, $snapshotFid: String!) "
    "{ policyObj(snappableFid: $snappableFid, snapshotFid: $snapshotFid) "
    "{ rootFileResult { hits { totalHits violations } } } }"
)

# Classification-event discriminators (raw webhook JSON)
CLASSIFICATION_CLASS = "Classification"
CLASSIFICATION_EVENT_NAME = "ClassficationResultsAvailable"

# Log Ingestion API retry configuration — used by RubrikActivity/sentinel.py
MAX_RETRIES = 3
RETRYABLE_STATUS = (429, 500, 502, 503, 504)
