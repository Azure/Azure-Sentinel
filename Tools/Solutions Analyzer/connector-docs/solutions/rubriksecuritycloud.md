# RubrikSecurityCloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Rubrik |
| **Support Tier** | Partner |
| **Support Link** | [https://support.rubrik.com](https://support.rubrik.com) |
| **Categories** | domains |
| **First Published** | 2022-07-19 |
| **Last Updated** | 2025-07-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md)

**Publisher:** Rubrik, Inc

The Rubrik Security Cloud data connector enables security operations teams to integrate insights from Rubrik's Data Observability services into Microsoft Sentinel. The insights include identification of anomalous filesystem behavior associated with ransomware and mass deletion, assess the blast radius of a ransomware attack, and sensitive data operators to prioritize and more rapidly investigate potential incidents.

| | |
|--------------------------|---|
| **Tables Ingested** | `Rubrik_Anomaly_Data_CL` |
| | `Rubrik_Events_Data_CL` |
| | `Rubrik_Ransomware_Data_CL` |
| | `Rubrik_ThreatHunt_Data_CL` |
| **Connector Definition Files** | [RubrikWebhookEvents_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RubrikSecurityCloud/Data%20Connectors/RubrikWebhookEvents/RubrikWebhookEvents_FunctionApp.json) |

[→ View full connector details](../connectors/rubriksecuritycloudazurefunctions.md)

## Tables Reference

This solution ingests data into **4 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Rubrik_Anomaly_Data_CL` | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) |
| `Rubrik_Events_Data_CL` | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) |
| `Rubrik_Ransomware_Data_CL` | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) |
| `Rubrik_ThreatHunt_Data_CL` | [Rubrik Security Cloud data connector](../connectors/rubriksecuritycloudazurefunctions.md) |

[← Back to Solutions Index](../solutions-index.md)
