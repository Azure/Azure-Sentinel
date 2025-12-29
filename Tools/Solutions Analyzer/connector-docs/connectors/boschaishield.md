# AIShield

| | |
|----------|-------|
| **Connector ID** | `BoschAIShield` |
| **Publisher** | Bosch |
| **Tables Ingested** | [`AIShield_CL`](../tables-index.md#aishield_cl) |
| **Used in Solutions** | [AIShield AI Security Monitoring](../solutions/aishield-ai-security-monitoring.md) |
| **Connector Definition Files** | [AIShieldConnector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Data%20Connectors/AIShieldConnector.json) |

[AIShield](https://www.boschaishield.com/) connector allows users to connect with AIShield custom defense mechanism logs with Microsoft Sentinel, allowing the creation of dynamic Dashboards, Workbooks, Notebooks and tailored Alerts to improve investigation and thwart attacks on AI systems. It gives users more insight into their organization's AI assets security posturing and improves their AI systems security operation capabilities.AIShield.GuArdIan analyzes the LLM generated content to identify and mitigate harmful content, safeguarding against legal, policy, role based, and usage based violations

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Note**: Users should have utilized AIShield SaaS offering to conduct vulnerability analysis and deployed custom defense mechanisms generated along with their AI asset. [**Click here**](https://azuremarketplace.microsoft.com/marketplace/apps/rbei.bgsw_aishield_product) to know more or get in touch.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**AIShield**](https://aka.ms/sentinel-boschaishield-parser) which is deployed with the Microsoft Sentinel Solution.

>**IMPORTANT:** Before deploying the AIShield Connector, have the Workspace ID and Workspace Primary Key (can be copied from the following).
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

[← Back to Connectors Index](../connectors-index.md)
