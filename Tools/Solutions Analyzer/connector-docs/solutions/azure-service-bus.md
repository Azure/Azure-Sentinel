# Azure Service Bus

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Service%20Bus](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Service%20Bus) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Azure Service Bus

**Publisher:** Microsoft

Azure Service Bus is a fully managed enterprise message broker with message queues and publish-subscribe topics (in a namespace). This connector lets you stream your Azure Service Bus diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. 

**Tables Ingested:**

- `AzureDiagnostics`

**Connector Definition Files:**

- [AzureServiceBus_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Service%20Bus/Data%20Connectors/AzureServiceBus_CCP.JSON)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | Azure Service Bus |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n