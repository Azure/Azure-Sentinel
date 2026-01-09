# BeyondTrustPMCloud

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | BeyondTrust |
| **Support Tier** | Partner |
| **Support Link** | [https://www.beyondtrust.com/](https://www.beyondtrust.com/) |
| **Categories** | domains |
| **First Published** | 2025-10-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BeyondTrustPMCloud](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BeyondTrustPMCloud) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [BeyondTrust PM Cloud](../connectors/beyondtrustpmcloud.md)

**Publisher:** BeyondTrust

The BeyondTrust Privilege Management Cloud data connector provides the capability to ingest activity audit logs and client event logs from BeyondTrust PM Cloud into Microsoft Sentinel.



This connector uses Azure Functions to pull data from the BeyondTrust PM Cloud API and ingest it into custom Log Analytics tables.

| | |
|--------------------------|---|
| **Tables Ingested** | `BeyondTrustPM_ActivityAudits_CL` |
| | `BeyondTrustPM_ClientEvents_CL` |
| **Connector Definition Files** | [BeyondTrustPMCloud_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BeyondTrustPMCloud/Data%20Connectors/BeyondTrustPMCloud_API_FunctionApp.json) |

[→ View full connector details](../connectors/beyondtrustpmcloud.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BeyondTrustPM_ActivityAudits_CL` | [BeyondTrust PM Cloud](../connectors/beyondtrustpmcloud.md) |
| `BeyondTrustPM_ClientEvents_CL` | [BeyondTrust PM Cloud](../connectors/beyondtrustpmcloud.md) |

[← Back to Solutions Index](../solutions-index.md)
