# Seraphic Web Security

| | |
|----------|-------|
| **Connector ID** | `SeraphicWebSecurity` |
| **Publisher** | Seraphic |
| **Tables Ingested** | [`SeraphicWebSecurity_CL`](../tables-index.md#seraphicwebsecurity_cl) |
| **Used in Solutions** | [SeraphicSecurity](../solutions/seraphicsecurity.md) |
| **Connector Definition Files** | [SeraphicSecurityConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SeraphicSecurity/Data%20Connectors/SeraphicSecurityConnector.json) |

The Seraphic Web Security data connector provides the capability to ingest [Seraphic Web Security](https://seraphicsecurity.com/) events and alerts into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Seraphic API key**: API key for Microsoft Sentinel connected to your Seraphic Web Security tenant. To get this API key for your tenant - [read this documentation](https://constellation.seraphicsecurity.com/integrations/microsoft_sentinel/Guidance/MicrosoftSentinel-IntegrationGuide-230822.pdf).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Seraphic Web Security**

Please insert the integration name, the Seraphic integration URL and your workspace name for Microsoft Sentinel:
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

[← Back to Connectors Index](../connectors-index.md)
