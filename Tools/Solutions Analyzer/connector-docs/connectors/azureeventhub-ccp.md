# Azure Event Hub

| | |
|----------|-------|
| **Connector ID** | `AzureEventHub_CCP` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AzureDiagnostics`](../tables-index.md#azurediagnostics) |
| **Used in Solutions** | [Azure Event Hubs](../solutions/azure-event-hubs.md) |
| **Connector Definition Files** | [AzureEventHub_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Event%20Hubs/Data%20Connectors/AzureEventHub_CCP.JSON) |

Azure Event Hubs is a big data streaming platform and event ingestion service. It can receive and process millions of events per second. This connector lets you stream your Azure Event Hub diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. 

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Policy**: owner role assigned for each policy assignment scope

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect your Azure Event Hub diagnostics logs into Sentinel.**

This connector uses Azure Policy to apply a single Azure Event Hub log-streaming configuration to a collection of instances, defined as a scope. Follow the instructions below to create and apply a policy to all current and future instances. Note, you may already have an active policy for this resource type.
**Stream diagnostics logs from your Azure Event Hub at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
