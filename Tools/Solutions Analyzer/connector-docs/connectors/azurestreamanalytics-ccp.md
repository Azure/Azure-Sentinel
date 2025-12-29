# Azure Stream Analytics

| | |
|----------|-------|
| **Connector ID** | `AzureStreamAnalytics_CCP` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AzureDiagnostics`](../tables-index.md#azurediagnostics) |
| **Used in Solutions** | [Azure Stream Analytics](../solutions/azure-stream-analytics.md) |
| **Connector Definition Files** | [AzureStreamAnalytics_CCP.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Stream%20Analytics/Data%20Connectors/AzureStreamAnalytics_CCP.JSON) |

Azure Stream Analytics is a real-time analytics and complex event-processing engine that is designed to analyze and process high volumes of fast streaming data from multiple sources simultaneously. This connector lets you stream your Azure Stream Analytics hub diagnostics logs into Microsoft Sentinel, allowing you to continuously monitor activity. 

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Policy**: owner role assigned for each policy assignment scope

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect your Azure Stream Analytics diagnostics logs into Sentinel.**

This connector uses Azure Policy to apply a single Azure Stream Analytics log-streaming configuration to a collection of instances, defined as a scope. Follow the instructions below to create and apply a policy to all current and future instances. Note, you may already have an active policy for this resource type.
**Stream diagnostics logs from your Azure Stream Analytics at scale**
**Launch the Azure Policy Assignment wizard and follow the steps.**

    >    1. In the **Basics** tab, click the button with the three dots under **Scope** to select your subscription.<br />2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log categories you want to ingest.<br />3. To apply the policy on your existing resources, mark the **Create a remediation task** check box in the **Remediation** tab.</value>
    > 📋 **Additional Configuration Step**: This connector includes a configuration step of type `PolicyAssignment`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
