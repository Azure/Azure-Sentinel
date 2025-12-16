# SeraphicSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Seraphic Security |
| **Support Tier** | Partner |
| **Support Link** | [https://seraphicsecurity.com](https://seraphicsecurity.com) |
| **Categories** | domains |
| **First Published** | 2023-07-31 |
| **Last Updated** | 2023-07-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SeraphicSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SeraphicSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Seraphic Web Security](../connectors/seraphicwebsecurity.md)

**Publisher:** Seraphic

The Seraphic Web Security data connector provides the capability to ingest [Seraphic Web Security](https://seraphicsecurity.com/) events and alerts into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

**Custom Permissions:**
- **Seraphic API key**: API key for Microsoft Sentinel connected to your Seraphic Web Security tenant. To get this API key for your tenant - [read this documentation](https://constellation.seraphicsecurity.com/integrations/microsoft_sentinel/Guidance/MicrosoftSentinel-IntegrationGuide-230822.pdf).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Seraphic Web Security**

Please insert the integration name, the Seraphic integration URL and your workspace name for Microsoft Sentinel:
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `APIKey`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.

| | |
|--------------------------|---|
| **Tables Ingested** | `SeraphicWebSecurity_CL` |
| **Connector Definition Files** | [SeraphicSecurityConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SeraphicSecurity/Data%20Connectors/SeraphicSecurityConnector.json) |

[→ View full connector details](../connectors/seraphicwebsecurity.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `SeraphicWebSecurity_CL` | [Seraphic Web Security](../connectors/seraphicwebsecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
