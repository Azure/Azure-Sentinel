# SecurityBridge Solution for SAP

| | |
|----------|-------|
| **Connector ID** | `SecurityBridge` |
| **Publisher** | SecurityBridge Group GmbH |
| **Tables Ingested** | [`ABAPAuditLog`](../tables-index.md#abapauditlog) |
| **Used in Solutions** | [SecurityBridge App](../solutions/securitybridge-app.md) |
| **Connector Definition Files** | [SecurityBridge_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SecurityBridge%20App/Data%20Connectors/SecurityBridge_PUSH_CCP/SecurityBridge_connectorDefinition.json) |

SecurityBridge enhances SAP security by integrating seamlessly with Microsoft Sentinel, enabling real-time monitoring and threat detection across SAP environments. This integration allows Security Operations Centers (SOCs) to consolidate SAP security events with other organizational data, providing a unified view of the threat landscape . Leveraging AI-powered analytics and Microsoft’s Security Copilot, SecurityBridge identifies sophisticated attack patterns and vulnerabilities within SAP applications, including ABAP code scanning and configuration assessments . The solution supports scalable deployments across complex SAP landscapes, whether on-premises, in the cloud, or hybrid environments . By bridging the gap between IT and SAP security teams, SecurityBridge empowers organizations to proactively detect, investigate, and respond to threats, enhancing overall security posture.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Microsoft Entra**: Permission to create an app registration in Microsoft Entra ID. Typically requires Entra ID Application Developer role or higher.
- **Microsoft Azure**: Permission to assign Monitoring Metrics Publisher role on data collection rules. Typically requires Azure RBAC Owner or User Access Administrator role.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Create ARM Resources and Provide the Required Permissions**

We will create data collection rule (DCR) and data collection endpoint (DCE) resources. We will also create a Microsoft Entra app registration and assign the required permissions to it.
#### Automated deployment of Azure resources
Clicking on "Deploy push connector resources" will trigger the creation of DCR and DCE resources.
It will then create a Microsoft Entra app registration with client secret and grant permissions on the DCR. This setup enables data to be sent securely to the DCR using a OAuth v2 client credentials.
- Deploy push connector resources
  Application: SecurityBridge Solution for SAP

**2. Maintain the data collection endpoint details and authentication info in SecurityBridge**

Share the data collection endpoint URL and authentication info with the SecurityBridge administrator to configure the Securitybridge to send data to the data collection endpoint.

Learn more from our KB Page https://abap-experts.atlassian.net/wiki/spaces/SB/pages/4099309579/REST+Push+Interface
- **Use this value to configure as Tenant ID in the LogIngestionAPI credential.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra Application ID**: `ApplicationId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Entra Application Secret**: `ApplicationSecret`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Use this value to configure the LogsIngestionURL parameter when deploying the IFlow.**: `DataCollectionEndpoint`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **DCR Immutable ID**: `DataCollectionRuleId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Sentinel for SAP Stream ID**: `SAP_ABAPAUDITLOG`
- **SecurityBridge_CL Stream ID**: `Custom-SecurityBridge_CL`

[← Back to Connectors Index](../connectors-index.md)
