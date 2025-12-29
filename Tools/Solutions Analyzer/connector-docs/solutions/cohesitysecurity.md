# CohesitySecurity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cohesity |
| **Support Tier** | Partner |
| **Support Link** | [https://support.cohesity.com/](https://support.cohesity.com/) |
| **Categories** | domains |
| **First Published** | 2022-10-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CohesitySecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CohesitySecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Cohesity](../connectors/cohesitydataconnector.md)

**Publisher:** Cohesity

The Cohesity function apps provide the ability to ingest Cohesity Datahawk ransomware alerts into Microsoft Sentinel.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `Cohesity_CL` |
| **Connector Definition Files** | [Cohesity_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/Cohesity_API_FunctionApp.json) |

[→ View full connector details](../connectors/cohesitydataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Cohesity_CL` | [Cohesity](../connectors/cohesitydataconnector.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          									|
|-------------|--------------------------------|--------------------------------------------------------------------------------|
| 3.1.2       | 21-10-2024                     | Corrected Param for JobId for recovery API 									|
| 3.1.1       | 10-10-2024                     | Updating Solution with fix for Restore **Playbook**   							|
| 3.1.0       | 19-07-2024                     | added missing helioID using anomaly strength   								|
| 3.0.0       | 29-06-2023                     | Updating Azure Function to Azure Functions in **Data Connector** Description   |

[← Back to Solutions Index](../solutions-index.md)
