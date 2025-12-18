# Azure Activity

| | |
|----------|-------|
| **Connector ID** | `AzureActivity` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AzureActivity`](../tables-index.md#azureactivity) |
| **Used in Solutions** | [Azure Activity](../solutions/azure-activity.md) |
| **Connector Definition Files** | [AzureActivity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20Activity/Data%20Connectors/AzureActivity.json) |

Azure Activity Log is a subscription log that provides insight into subscription-level events that occur in Azure, including events from Azure Resource Manager operational data, service health events, write operations taken on the resources in your subscription, and the status of activities performed in Azure. For more information, see the [Microsoft Sentinel documentation ](https://go.microsoft.com/fwlink/p/?linkid=2219695&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **Policy​**: owner role assigned for each policy assignment scope.​
- **Subscription**: owner role permission on the relevant subscription

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

ℹ️ This connector has been updated to use the diagnostics settings back-end pipeline. which provides increased functionality and better consistency with resource logs.
Connectors using this pipeline can also be governed at scale by Azure Policy. Learn more about the new <a href="https://docs.microsoft.com/azure/sentinel/connect-azure-activity">Azure Activity connector</a>.
Follow the instructions below to upgrade your connector to the diagnostics settings pipeline.

**1. Disconnect your subscriptions from the legacy method**

The subscriptions listed below are still using the older, legacy method. You are strongly encouraged to upgrade to the new pipeline.<br>
To do this, click on the 'Disconnect All' button below, before proceeding to launch the Azure Policy Assignment wizard.
- Configure data source: AzureActivityLog

**2.  Connect your subscriptions through diagnostic settings new pipeline**

This connector uses Azure Policy to apply a single Azure Subscription log-streaming configuration to a collection of subscriptions, defined as a scope.
Follow the instructions below to create and apply a policy to all current and future subscriptions. **Note**, you may already have an active policy for this resource type.
**Launch the Azure Policy Assignment wizard and follow the steps.​**

  >1. In the **Basics** tab, click the button with the three dots under **Scope** to select your resources assignment scope.
        >2. In the **Parameters** tab, choose your Microsoft Sentinel workspace from the **Log Analytics workspace** drop-down list, and leave marked as "True" all the log and metric types you want to ingest.
        >3. To apply the policy on your existing resources, select the **Remediation tab** and mark the **Create a remediation task** checkbox.
  - **Configure policy assignment**

[← Back to Connectors Index](../connectors-index.md)
