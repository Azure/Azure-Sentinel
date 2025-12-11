# Subscription-based Microsoft Defender for Cloud (Legacy)

| | |
|----------|-------|
| **Connector ID** | `AzureSecurityCenter` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`SecurityAlert`](../tables-index.md#securityalert) |
| **Used in Solutions** | [Microsoft Defender for Cloud](../solutions/microsoft-defender-for-cloud.md) |
| **Connector Definition Files** | [AzureSecurityCenter.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Defender%20for%20Cloud/Data%20Connectors/AzureSecurityCenter.JSON) |

Microsoft Defender for Cloud is a security management tool that allows you to detect and quickly respond to threats across Azure, hybrid, and multi-cloud workloads. This connector allows you to stream your security alerts from Microsoft Defender for Cloud into Microsoft Sentinel, so you can view Defender data in workbooks, query it to produce alerts, and investigate and respond to incidents.



[For more information>](https://aka.ms/ASC-Connector)

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.

**Custom Permissions:**
- **License**: The connector is available for all deployments of Microsoft Defender for Cloud.
- **Subscription**: [read security data](https://docs.microsoft.com/azure/security-center/security-center-permissions).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Defender for Cloud to Microsoft Sentinel**

Mark the check box of each Azure subscription whose alerts you want to import into Microsoft Sentinel, then select **Connect** above the list.

> The connector can be enabled only on subscriptions that have at least one Microsoft Defender plan enabled in Microsoft Defender for Cloud, and only by users with Security Reader permissions on the subscription.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `AzureSecurityCenterSubscriptions`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
