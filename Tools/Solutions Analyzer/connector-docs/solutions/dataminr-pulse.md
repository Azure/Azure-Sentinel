# Dataminr Pulse

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Dataminr Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.dataminr.com/dataminr-support#support](https://www.dataminr.com/dataminr-support#support) |
| **Categories** | domains |
| **First Published** | 2023-04-12 |
| **Last Updated** | 2023-04-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Dataminr Pulse Alerts Data Connector](../connectors/dataminrpulsealerts.md)

**Publisher:** Dataminr

Dataminr Pulse Alerts Data Connector brings our AI-powered real-time intelligence into Microsoft Sentinel for faster threat detection and response.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `DataminrPulse_Alerts_CL` |
| **Connector Definition Files** | [DataminrPulseAlerts_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dataminr%20Pulse/Data%20Connectors/DataminrPulseAlerts/DataminrPulseAlerts_FunctionApp.json) |

[→ View full connector details](../connectors/dataminrpulsealerts.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DataminrPulse_Alerts_CL` | [Dataminr Pulse Alerts Data Connector](../connectors/dataminrpulsealerts.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.5       |     16-09-2025                 | Updated Python version to 3.12 and Added Log Ingestion API support             |
| 3.0.4       |     12-09-2025                 | Added support for Azure GovCloud |
| 3.0.3       |     03-05-2024                 | Repackaged for parser issue fix on reinstall |
| 3.0.2       |     14-12-2023                 | Updated **Data Connector** code                    |
| 3.0.1       |     06-12-2023                 | Updated steps in **DataConnector** UI and **README.md** file.                     |
| 3.0.0       |     14-07-2023                 | Initial Solution Release                     |

[← Back to Solutions Index](../solutions-index.md)
