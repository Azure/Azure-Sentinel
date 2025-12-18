# SAP LogServ (RISE), S/4HANA Cloud private edition

| | |
|----------|-------|
| **Connector ID** | `SAPLogServ` |
| **Publisher** | SAP SE |
| **Tables Ingested** | [`SAPLogServ_CL`](../tables-index.md#saplogserv_cl) |
| **Used in Solutions** | [SAP LogServ](../solutions/sap-logserv.md) |
| **Connector Definition Files** | [SAPLogServ.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Data%20Connectors/SAPLogServ.json), [SAPLogServ_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Data%20Connectors/SAPLogServ_PUSH_CCP/SAPLogServ_connectorDefinition.json) |

SAP LogServ is an SAP Enterprise Cloud Services (ECS) service aimed at collection, storage, forwarding and access of logs. LogServ centralizes the logs from all systems, applications, and ECS services used by a registered customer. 

 Main Features include:

Near Realtime Log Collection: With ability to integrate into Microsoft Sentinel as SIEM solution.

LogServ complements the existing SAP application layer threat monitoring and detections in Microsoft Sentinel with the log types owned by SAP ECS as the system provider. This includes logs like: SAP Security Audit Log (AS ABAP), HANA database, AS JAVA, ICM, SAP Web Dispatcher, SAP Cloud Connector, OS, SAP Gateway, 3rd party Database, Network, DNS, Proxy, Firewall

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
  Application: SAP LogServ push to Microsoft Sentinel

**2. Maintain the data collection endpoint details and authentication info in SAP LogServ**

Share the data collection endpoint URL and authentication info with the SAP LogServ administrator to configure the SAP LogServ to send data to the data collection endpoint.

Learn more from [this blog series](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/ultimate-blog-series-sap-logserv-integration-with-microsoft-sentinel/ba-p/14126401).
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

[← Back to Connectors Index](../connectors-index.md)
