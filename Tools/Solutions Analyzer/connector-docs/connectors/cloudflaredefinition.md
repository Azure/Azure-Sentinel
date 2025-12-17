# Cloudflare (Using Blob Container) (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `CloudflareDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CloudflareV2_CL`](../tables-index.md#cloudflarev2_cl) |
| **Used in Solutions** | [Cloudflare](../solutions/cloudflare.md), [Cloudflare CCF](../solutions/cloudflare-ccf.md) |
| **Connector Definition Files** | [CloudflareLog_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cloudflare/Data%20Connectors/CloudflareLog_CCF/CloudflareLog_ConnectorDefinition.json) |

 The Cloudflare data connector provides the capability to ingest Cloudflare logs into Microsoft Sentinel using the Cloudflare Logpush and Azure Blob Storage. Refer to [Cloudflare documentation](https://developers.cloudflare.com/logs/about/)for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Create a storage account and a container**: Before setting up logpush in Cloudflare, first create a storage account and a container in Microsoft Azure. Use [this guide](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) to know more about Container and Blob. Follow the steps in the [documentation](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal) to create an Azure Storage account.
- **Generate a Blob SAS URL**: Create and Write permissions are required. Refer the [documentation](https://learn.microsoft.com/en-us/azure/ai-services/translator/document-translation/how-to-guides/create-sas-tokens?tabs=Containers) to know more about Blob SAS token and url.
- **Collecting logs from Cloudflare to your Blob container**: Follow the steps in the [documentation](https://developers.cloudflare.com/logs/get-started/enable-destinations/azure/) for collecting logs from Cloudflare to your Blob container.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Cloudflare Logs to Microsoft Sentinel**

To enable Cloudflare logs for Microsoft Sentinel, provide the required information below and click on Connect.
>
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `ServicePrincipalIDTextBox_test`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.
- **The Blob container's URL you want to collect data from**
- **The Blob container's storage account resource group name**
- **The Blob container's storage account location**
- **The Blob container's storage account subscription id**
- **The event grid topic name of the blob container's storage account if exist. else keep empty.**
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
