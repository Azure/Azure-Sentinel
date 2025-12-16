# Azure Service Bus

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-06-29 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Service%20Bus](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Service%20Bus) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Azure Service Bus](../connectors/azureservicebus-ccp.md)

**Publisher:** Microsoft

Azure Service Bus is a fully managed enterprise message broker with message queues and publish-subscribe topics (in a namespace). This connector lets you stream your Azure Service Bus diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. 

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Policy**: owner role assigned for each policy assignment scope

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect your Azure Service Bus diagnostics logs into Sentinel.**

This connector uses Azure Policy to apply a single Azure Service Bus log-streaming configuration to a collection of instances, defined as a scope. Follow the instructions below to create and apply a policy to all current and future instances. Note, you may already have an active policy for this resource type.
**Stream diagnostics logs from your Azure Service Bus at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

| | |
|--------------------------|---|
| **Tables Ingested** | `AzureDiagnostics` |
| **Connector Definition Files** | [AzureServiceBus_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Service%20Bus/Data%20Connectors/AzureServiceBus_CCP.JSON) |

[→ View full connector details](../connectors/azureservicebus-ccp.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AzureDiagnostics` | [Azure Service Bus](../connectors/azureservicebus-ccp.md) |

[← Back to Solutions Index](../solutions-index.md)
