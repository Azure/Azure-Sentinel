"""This file contains all constants."""
import os

LOGS_STARTS_WITH = "Rubrik:"
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL = os.environ.get("LogLevel", "")
WORKSPACE_ID = os.environ.get("WorkspaceID")
WORKSPACE_KEY = os.environ.get("WorkspaceKey")
ANOMALY_LOG_TYPE = os.environ.get("Anomalies_table_name", "Rubrik_Anomaly_Data")
RANSOMWARE_LOG_TYPE = os.environ.get("RansomwareAnalysis_table_name", "Rubrik_Ransomware_Data")
THREATHUNT_LOG_TYPE = os.environ.get("ThreatHunts_table_name", "Rubrik_ThreatHunt_Data")
EVENTS_LOG_TYPE = os.environ.get("Events_table_name", "Rubrik_Events_Data")
