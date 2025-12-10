# AIShield AI Security Monitoring

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | AIShield |
| **Support Tier** | Partner |
| **Support Link** | [https://azuremarketplace.microsoft.com/marketplace/apps/rbei.bgsw_aishield_product/](https://azuremarketplace.microsoft.com/marketplace/apps/rbei.bgsw_aishield_product/) |
| **Categories** | domains |
| **First Published** | 2022-01-11 |
| **Last Updated** | 2025-03-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [AIShield](../connectors/boschaishield.md)

**Publisher:** Bosch

[AIShield](https://www.boschaishield.com/) connector allows users to connect with AIShield custom defense mechanism logs with Microsoft Sentinel, allowing the creation of dynamic Dashboards, Workbooks, Notebooks and tailored Alerts to improve investigation and thwart attacks on AI systems. It gives users more insight into their organization's AI assets security posturing and improves their AI systems security operation capabilities.AIShield.GuArdIan analyzes the LLM generated content to identify and mitigate harmful content, safeguarding against legal, policy, role based, and usage based violations

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Note**: Users should have utilized AIShield SaaS offering to conduct vulnerability analysis and deployed custom defense mechanisms generated along with their AI asset. [**Click here**](https://azuremarketplace.microsoft.com/marketplace/apps/rbei.bgsw_aishield_product) to know more or get in touch.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**AIShield**](https://aka.ms/sentinel-boschaishield-parser) which is deployed with the Microsoft Sentinel Solution.

>**IMPORTANT:** Before deploying the AIShield Connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `AIShield_CL` |
| **Connector Definition Files** | [AIShieldConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Data%20Connectors/AIShieldConnector.json) |

[→ View full connector details](../connectors/boschaishield.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AIShield_CL` | [AIShield](../connectors/boschaishield.md) |

[← Back to Solutions Index](../solutions-index.md)
