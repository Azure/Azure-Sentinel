# Commvault Cloud Security IQ Integration: Security Telemetry & Schema Guide

This document describes the security telemetry ingested by the **Commvault Cloud Security IQ** data connector, its expected database schema inside Microsoft Sentinel, and reference documentation resources.

---

## 1. Ingested Security Telemetry

The data connector continuously polls the Commvault Cloud Security IQ / Unusual File Activity API to forward high-fidelity security threat indicators. It collects and structures the following telemetry:

*   **Unusual File Activity (Anomalies)**:
    *   Abnormal counts of file creations, modifications, deletions, and renames on client file systems.
    *   Automatic baseline tracking (established after 7 days of monitoring) to alert on deviations.
*   **File Type Mismatches (MIME)**:
    *   Discrepancies where a file's actual MIME header type does not match its declared file extension, suggesting potential payload corruption or encryption.
*   **File Extension & Rename Anomalies**:
    *   Bulk renaming of files to extensions known to be associated with ransomware strains.
*   **Backup Size Anomalies (Data Written)**:
    *   Anomalous increases in the volume of data written to backup media during backup jobs, indicating possible bulk file encryption.

---

## 2. Microsoft Sentinel Database Schema

All ingested events are written to the custom table **`CommvaultAlertsCCF_CL`** in your Log Analytics workspace. 

### Database Columns (`CommvaultAlertsCCF_CL`)

| Column Name         | Data Type | Description                                                                                      |     |
| :--------------------| :----------| :-------------------------------------------------------------------------------------------------| -----|
| **`TimeGenerated`** | Datetime  | Ingestion/occurrence timestamp used by Sentinel for queries and alerts.                          |     |
| **`RefTime`**       | Long      | UNIX Epoch timestamp (in seconds) representing the detection time.                               |     |
| **`AnomalyType`**   | Int       | Bitfield representing the anomaly types (see Bitfield Legend below).                             |     |
| **`CreateCount`**   | Int       | Number of files created in the path during the detection interval.                               |     |
| **`DeleteCount`**   | Int       | Number of files deleted in the path during the detection interval.                               |     |
| **`ModCount`**      | Int       | Number of files modified in the path during the detection interval.                              |     |
| **`RenameCount`**   | Int       | Number of files renamed in the path during the detection interval.                               |     |
| **`Location`**      | String    | XML geo-location snippet containing IP, state, country, lat/long, and ISP details of the client. |     |
| **`ClientName`**    | String    | The host name of the client computer registered in Commvault.                                    |     |
| **`ClientId`**      | String    | Commvault internal client/server identification number.                                          |     |

---

### AnomalyType Bitfield Legend

The `AnomalyType` column is stored as an integer bitmask. Multiple types can be active simultaneously on a single event record (by adding the values together):

*   **`1`**: `ANOMALY_CREATED` (File created)
*   **`2`**: `ANOMALY_RENAMED` (File renamed)
*   **`4`**: `ANOMALY_MODIFIED` (File modified)
*   **`8`**: `ANOMALY_DELETED` (File deleted)
*   **`15`**: `ANOMALY_FILE_ACTIVITY` (Composite flags: `1 + 2 + 4 + 8`)
*   **`32`**: `ANOMALY_MIME_CLASSIFICATION` (File type/extension mismatch)
*   **`512`**: `ANOMALY_FILE_EXTENSION` (Suspicious file extension change)
*   **`4096`**: `ANOMALY_DATA_WRITTEN` (Backup size anomaly)

*Example query to check for active file type mismatch indicators:*
```kusto
CommvaultAlertsCCF_CL
| where binary_and(AnomalyType, 32) == 32
```

---

## 3. Reference Documentation

Customers can reference the following official documentation for deeper configuration and platform details:

*   **Commvault Threat Indicators Dashboard Overview**:
    [Commvault Threat Indicators Dashboard Docs](https://documentation.commvault.com/2024e/commcell-console/threat_indicators_dashboard.html)
*   **Threat Indicators Report (Unusual File Activity)**:
    [Commvault Threat Indicators Report Docs](https://documentation.commvault.com/2024e/software/threat_indicators_report.html)
*   **Backup Job File Activity Anomalies**:
    [Commvault File System Backup Job Anomalies Docs](https://documentation.commvault.com/2024e/commcell-console/threat_indicators_backup_job_anomalies_for_file_system.html)
*   **Backup Size Anomalies**:
    [Commvault Backup Size Anomalies Docs](https://documentation.commvault.com/2024e/commcell-console/threat_indicators_backup_size_anomalies_for_file_system.html)
*   **File Type (MIME) Anomalies**:
    [Commvault File Type Anomalies Docs](https://documentation.commvault.com/2024e/commcell-console/threat_indicators_file_type_anomalies_in_backup_jobs.html)
*   **File Extension Anomalies**:
    [Commvault File Extension Anomalies Docs](https://documentation.commvault.com/2024e/commcell-console/threat_indicators_file_extension_anomalies_in_backup_jobs.html)
