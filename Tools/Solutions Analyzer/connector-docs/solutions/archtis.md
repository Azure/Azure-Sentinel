# archTIS

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | archTIS |
| **Support Tier** | Partner |
| **Support Link** | [https://www.archtis.com/nc-protect-support/](https://www.archtis.com/nc-protect-support/) |
| **Categories** | domains |
| **First Published** | 2021-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/archTIS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/archTIS) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [NC Protect](../connectors/nucleuscyberncprotect.md)

**Publisher:** archTIS

[NC Protect Data Connector (archtis.com)](https://info.archtis.com/get-started-with-nc-protect-sentinel-data-connector) provides the capability to ingest user activity logs and events into Microsoft Sentinel. The connector provides visibility into NC Protect user activity logs and events in Microsoft Sentinel to improve monitoring and investigation capabilities

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **NC Protect**: You must have a running instance of NC Protect for O365. Please [contact us](https://www.archtis.com/data-discovery-classification-protection-software-secure-collaboration/).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

1. Install NC Protect into your Azure Tenancy
2. Log into the NC Protect Administration site
3. From the left hand navigation menu, select General -> User Activity Monitoring
4. Tick the checkbox to Enable SIEM and click the Configure button
5. Select Microsoft Sentinel as the Application and complete the configuration using the information below
6. Click Save to activate the connection
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `NCProtectUAL_CL` |
| **Connector Definition Files** | [NucleusCyberNCProtect.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/archTIS/Data%20Connectors/NucleusCyberNCProtect.json) |

[→ View full connector details](../connectors/nucleuscyberncprotect.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `NCProtectUAL_CL` | [NC Protect](../connectors/nucleuscyberncprotect.md) |

[← Back to Solutions Index](../solutions-index.md)
