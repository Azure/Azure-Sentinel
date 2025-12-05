# Cyfirma Compromised Accounts

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-05-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Compromised%20Accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Compromised%20Accounts) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [CYFIRMA Compromised Accounts](../connectors/cyfirmacompromisedaccountsdataconnector.md)

**Publisher:** Microsoft

The CYFIRMA Compromised Accounts data connector enables seamless log ingestion from the DeCYFIR/DeTCT API into Microsoft Sentinel. Built on the Microsoft Sentinel Codeless Connector Platform, it leverages the DeCYFIR/DeTCT API to retrieve logs. Additionally, it supports DCR-based [ingestion time transformations](https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview), which parse security data into a custom table during ingestion. This eliminates the need for query-time parsing, enhancing performance and efficiency.

| | |
|--------------------------|---|
| **Tables Ingested** | `CyfirmaCompromisedAccounts_CL` |
| **Connector Definition Files** | [CyfirmaCompAcc_DataConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Compromised%20Accounts/Data%20Connectors/CyfirmaCompromisedAccounts_ccp/CyfirmaCompAcc_DataConnectorDefinition.json) |

[→ View full connector details](../connectors/cyfirmacompromisedaccountsdataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CyfirmaCompromisedAccounts_CL` | [CYFIRMA Compromised Accounts](../connectors/cyfirmacompromisedaccountsdataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
