# Proofpoint On Demand Email Security (via Codeless Connector Platform)

| | |
|----------|-------|
| **Connector ID** | `ProofpointCCPDefinition` |
| **Publisher** | Proofpoint |
| **Tables Ingested** | [`ProofpointPODMailLog_CL`](../tables-index.md#proofpointpodmaillog_cl), [`ProofpointPODMessage_CL`](../tables-index.md#proofpointpodmessage_cl) |
| **Used in Solutions** | [Proofpoint On demand(POD) Email Security](../solutions/proofpoint-on-demand(pod)-email-security.md) |
| **Connector Definition Files** | [ProofpointPOD_Definaton.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Proofpoint%20On%20demand%28POD%29%20Email%20Security/Data%20Connectors/ProofPointEmailSecurity_CCP/ProofpointPOD_Definaton.json) |

Proofpoint On Demand Email Security data connector provides the capability to get Proofpoint on Demand Email Protection data, allows users to check message traceability, monitoring into email activity, threats,and data exfiltration by attackers and malicious insiders. The connector provides ability to review events in your org on an accelerated basis, get event log files in hourly increments for recent activity.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions on the workspace are required.

**Custom Permissions:**
- **Websocket API Credentials/permissions**: **ProofpointClusterID**, and **ProofpointToken** are required. [See the documentation to learn more about API](https://proofpointcommunities.force.com/community/s/article/Proofpoint-on-Demand-Pod-Log-API).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### Configuration steps for the Proofpoint POD Websocket API 
 ####  The PoD Log API does not allow use of the same token for more than one session at the same time, so make sure your token isn't used anywhere. 
 Proofpoint Websocket API service requires Remote Syslog Forwarding license. Please refer the [documentation](https://proofpointcommunities.force.com/community/s/article/Proofpoint-on-Demand-Pod-Log-API) on how to enable and check PoD Log API. 
 You must provide your cluster id and security token.
#### 1. Retrieve the cluster id
   1.1. Log in to the [proofpoint](https://admin.proofpoint.com/) [**Management Console**] with Admin user credentials

   1.2. In the **Management Console**, the cluster id is displayed in the upper-right corner.
#### 2. Retrieve the API token
   2.1. Log in to the [proofpoint](https://admin.proofpoint.com/) [**Management Console**] with Admin user credentials

  2.2. In the **Management Console**, click **Settings** -> **API Key Management** 

  2.3. Under **API Key Management** click on the **PoD Logging** tab.

   2.4. Get or create a new API key.
- **Cluster Id**: cluster_id
- **API Key**: API Key
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
