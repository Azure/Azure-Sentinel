# Pathlock_TDnR

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Pathlock Inc. |
| **Support Tier** | Partner |
| **Support Link** | [https://pathlock.com/support/](https://pathlock.com/support/) |
| **Categories** | domains,verticals |
| **First Published** | 2022-02-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pathlock_TDnR](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pathlock_TDnR) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Pathlock Inc.: Threat Detection and Response for SAP](../connectors/pathlock-tdnr.md)

**Publisher:** Pathlock Inc.

The [Pathlock Threat Detection and Response (TD&R)](https://pathlock.com/products/cybersecurity-application-controls/) integration with **Microsoft Sentinel Solution for SAP** delivers unified, real-time visibility into SAP security events, enabling organizations to detect and act on threats across all SAP landscapes. This out-of-the-box integration allows Security Operations Centers (SOCs) to correlate SAP-specific alerts with enterprise-wide telemetry, creating actionable intelligence that connects IT security with business processes.



Pathlock’s connector is purpose-built for SAP and forwards only **security-relevant events by default**, minimizing data volume and noise while maintaining the flexibility to forward all log sources when needed. Each event is enriched with **business process context**, allowing Microsoft Sentinel Solution for SAP analytics to distinguish operational patterns from real threats and to prioritize what truly matters.



This precision-driven approach helps security teams drastically reduce false positives, focus investigations, and accelerate **mean time to detect (MTTD)** and **mean time to respond (MTTR)**. Pathlock’s library consists of more than 1,500 SAP-specific detection signatures across 70+ log sources, the solution uncovers complex attack behaviors, configuration weaknesses, and access anomalies.



By combining business-context intelligence with advanced analytics, Pathlock enables enterprises to strengthen detection accuracy, streamline response actions, and maintain continuous control across their SAP environments—without adding complexity or redundant monitoring layers.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.
- **Keys** (Workspace): Read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key)

**Custom Permissions:**
- **Microsoft Entra**: Permission to create an app registration in Microsoft Entra ID. Typically requires Entra ID Application Developer role or higher.
- **Microsoft Azure**: Permission to assign Monitoring Metrics Publisher role on data collection rules. Typically requires Azure RBAC Owner or User Access Administrator role.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Create ARM Resources and Provide the Required Permissions**

We will create data collection rule (DCR) and data collection endpoint (DCE) resources. We will also create a Microsoft Entra app registration and assign the required permissions to it.
#### Automated deployment of Azure resources
Clicking on "Deploy push connector resources" will trigger the creation of DCR and DCE resources.
It will then create a Microsoft Entra app registration with client secret and grant permissions on the DCR. This setup enables data to be sent securely to the DCR using a OAuth v2 client credentials.
- Deploy push connector resources
  Application: Pathlock Inc. Threat Detection and Response for SAP

**2. Maintain the data collection endpoint details and authentication info in your central instance of Pathlock's Cybersecurity Application Controls: Threat Detection and Response**

Share the data collection endpoint URL and authentication info with the Pathlock administrator to configure the plug and play forwarding in Threat Detection and Response to send data to the data collection endpoint.
Please do not hesitate to contact Pathlock if support is needed.
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

| | |
|--------------------------|---|
| **Tables Ingested** | `ABAPAuditLog` |
| | `Pathlock_TDnR_CL` |
| **Connector Definition Files** | [Pathlock_TDnR_connectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Pathlock_TDnR/Data%20Connectors/Pathlock_TDnR_PUSH_CCP/Pathlock_TDnR_connectorDefinition.json) |

[→ View full connector details](../connectors/pathlock-tdnr.md)

## Tables Reference

This solution ingests data into **2 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ABAPAuditLog` | [Pathlock Inc.: Threat Detection and Response for SAP](../connectors/pathlock-tdnr.md) |
| `Pathlock_TDnR_CL` | [Pathlock Threat Detection and Response Integration](../connectors/pathlock-tdnr.md) |

[← Back to Solutions Index](../solutions-index.md)
