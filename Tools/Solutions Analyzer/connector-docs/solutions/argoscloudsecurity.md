# ARGOSCloudSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | ARGOS Cloud Security |
| **Support Tier** | Partner |
| **Support Link** | [https://argos-security.io/contact-us](https://argos-security.io/contact-us) |
| **Categories** | domains |
| **First Published** | 2022-08-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ARGOSCloudSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ARGOSCloudSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [ARGOS Cloud Security](../connectors/argoscloudsecurity.md)

**Publisher:** ARGOS Cloud Security

The ARGOS Cloud Security integration for Microsoft Sentinel allows you to have all your important cloud security events in one place. This enables you to easily create dashboards, alerts, and correlate events across multiple systems. Overall this will improve your organization's security posture and security incident response.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Subscribe to ARGOS**

Ensure you already own an ARGOS Subscription. If not, browse to [ARGOS Cloud Security](https://argos-security.io) and sign up to ARGOS.

Alternatively, you can also purchase ARGOS via the [Azure Marketplace](https://azuremarketplace.microsoft.com/en-au/marketplace/apps/argoscloudsecurity1605618416175.argoscloudsecurity?tab=Overview).

**2. Configure Sentinel integration from ARGOS**

Configure ARGOS to forward any new detections to your Sentinel workspace by providing ARGOS with your Workspace ID and Primary Key.

There is **no need to deploy any custom infrastructure**.

Enter the information into the [ARGOS Sentinel](https://app.argos-security.io/account/sentinel) configuration page.

New detections will automatically be forwarded.

[Learn more about the integration](https://www.argos-security.io/resources#integrations)
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `ARGOS_CL` |
| **Connector Definition Files** | [Connector_ARGOS.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ARGOSCloudSecurity/Data%20Connectors/Connector_ARGOS.json) |

[→ View full connector details](../connectors/argoscloudsecurity.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ARGOS_CL` | [ARGOS Cloud Security](../connectors/argoscloudsecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
