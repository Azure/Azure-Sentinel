# Valence Security

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Valence Security |
| **Support Tier** | Partner |
| **Support Link** | [https://www.valencesecurity.com/](https://www.valencesecurity.com/) |
| **Categories** | domains |
| **First Published** | 2023-11-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [SaaS Security](../connectors/valencesecurity.md)

**Publisher:** Valence Security

Connects the Valence SaaS security platform Azure Log Analytics via the REST API interface.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Step 1 : Read the detailed documentation**

The installation process is documented in great detail in [Valence Security's knowledge base](https://support.valencesecurity.com). The user should consult this documentation further to understand installation and debug of the integration.

**2. Step 2: Retrieve the workspace access credentials**

The first installation step is to retrieve both your **Workspace ID** and **Primary Key** from the Microsoft Sentinel platform.
Copy the values shown below and save them for configuration of the API log forwarder integration.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Step 3: Configure Sentinel integration on the Valence Security Platform**

As a Valence Security Platform admin, go to the [configuration screen](https://app.valencesecurity.com/settings/configuration), click Connect in the SIEM Integration card, and choose Microsoft Sentinel. Paste the values from the previous step and click Connect. Valence will test the connection so when success is reported, the connection worked.

| | |
|--------------------------|---|
| **Tables Ingested** | `ValenceAlert_CL` |
| **Connector Definition Files** | [ValenceSecurity.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Valence%20Security/Data%20Connectors/ValenceSecurity.json) |

[→ View full connector details](../connectors/valencesecurity.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ValenceAlert_CL` | [SaaS Security](../connectors/valencesecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
