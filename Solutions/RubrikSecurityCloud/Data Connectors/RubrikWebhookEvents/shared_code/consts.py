"""This file contains all constants."""
import os

LOGS_STARTS_WITH = "Rubrik:"
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.environ.get("LogLevel", "")
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
ANOMALY_LOG_TYPE = os.environ.get("Anomalies_table_name")
RANSOMWARE_LOG_TYPE = os.environ.get("RansomwareAnalysis_table_name")
THREATHUNT_LOG_TYPE = os.environ.get("ThreatHunts_table_name")
