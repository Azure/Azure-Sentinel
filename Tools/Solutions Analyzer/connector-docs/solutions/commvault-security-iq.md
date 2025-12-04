# Commvault Security IQ

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Commvault |
| **Support Tier** | Partner |
| **Support Link** | [https://www.commvault.com/support](https://www.commvault.com/support) |
| **Categories** | domains |
| **First Published** | 2023-08-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CommvaultSecurityIQ](../connectors/commvaultsecurityiq-cl.md)

**Publisher:** Commvault

This Azure Function enables Commvault users to ingest alerts/events into their Microsoft Sentinel instance. With Analytic Rules,Microsoft Sentinel can automatically create Microsoft Sentinel incidents from incoming events and logs.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommvaultSecurityIQ_CL` |
| **Connector Definition Files** | [CommvaultSecurityIQ_API_AzureFunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Data%20Connectors/CommvaultSecurityIQ_API_AzureFunctionApp.json) |

[→ View full connector details](../connectors/commvaultsecurityiq-cl.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommvaultSecurityIQ_CL` | [CommvaultSecurityIQ](../connectors/commvaultsecurityiq-cl.md) |

[← Back to Solutions Index](../solutions-index.md)
