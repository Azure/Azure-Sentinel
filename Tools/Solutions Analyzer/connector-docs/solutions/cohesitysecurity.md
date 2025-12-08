# CohesitySecurity

## Solution Information

| | |
|------------------------|-------|
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

| | |
|--------------------------|---|
| **Tables Ingested** | `Cohesity_CL` |
| **Connector Definition Files** | [Cohesity_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CohesitySecurity/Data%20Connectors/Helios2Sentinel/Cohesity_API_FunctionApp.json) |

[→ View full connector details](../connectors/cohesitydataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Cohesity_CL` | [Cohesity](../connectors/cohesitydataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
