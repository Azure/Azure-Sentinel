# SailPointIdentityNow

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | SailPoint |
| **Support Tier** | Partner |
| **Categories** | domains |
| **First Published** | 2021-10-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SailPoint IdentityNow](../connectors/sailpointidentitynow.md)

**Publisher:** SailPoint

The [SailPoint](https://www.sailpoint.com/) IdentityNow data connector provides the capability to ingest [SailPoint IdentityNow] search events into Microsoft Sentinel through the REST API. The connector provides customers the ability to extract audit information from their IdentityNow tenant. It is intended to make it even easier to bring IdentityNow user activity and governance events into Microsoft Sentinel to improve insights from your security incident and event monitoring solution.

| | |
|--------------------------|---|
| **Tables Ingested** | `SailPointIDN_Events_CL` |
| | `SailPointIDN_Triggers_CL` |
| **Connector Definition Files** | [SailPoint_IdentityNow_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SailPointIdentityNow/Data%20Connectors/SailPoint_IdentityNow_FunctionApp.json) |

[→ View full connector details](../connectors/sailpointidentitynow.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SailPointIDN_Events_CL` | [SailPoint IdentityNow](../connectors/sailpointidentitynow.md) |
| `SailPointIDN_Triggers_CL` | [SailPoint IdentityNow](../connectors/sailpointidentitynow.md) |

[← Back to Solutions Index](../solutions-index.md)
