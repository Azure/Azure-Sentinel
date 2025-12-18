# Google Kubernetes Engine

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2025-04-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md)

**Publisher:** Microsoft

The Google Kubernetes Engine (GKE) Logs enable you to capture cluster activity, workload behavior, and security events, allowing you to monitor Kubernetes workloads, analyze performance, and detect potential threats across GKE clusters.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

#### 1. Set up your GCP environment 
You must have the following GCP resources defined and configured: topic, subscription for the topic, workload identity pool, workload identity provider, and service account with permissions to get and consume from the subscription.

To configure this data connector, execute the following Terraform scripts:

1. Setup Required Resources: [Configuration Guide](https://github.com/Alekhya0824/GithubValidationREPO/blob/main/gke/Readme.md)
2. Setup Authentication: [Authentication tutorial](https://learn.microsoft.com/en-us/azure/sentinel/connect-google-cloud-platform?tabs=terraform%2Cauditlogs#gcp-authentication-setup). Note: If Authentication is already setup using another GCP data connector, kindly skip this step and use the existing service account and workload identity pool.
- **Tenant ID: A unique identifier that is used as an input in the Terraform configuration within a GCP environment.**: `TenantId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
#### 2. Enable Kubernetes Engine Logging 
In your GCP account, navigate to the Kubernetes Engine section. Enable Cloud Logging for your clusters. Within Cloud Logging, ensure that the specific logs you want to ingest—such as API server, scheduler, controller manager, HPA decision, and application logs—are enabled for effective monitoring and security analysis.
#### 3. Connect new collectors 
To enable GKE Logs for Microsoft Sentinel, click the **Add new collector** button, fill in the required information in the context pane, and click **Connect**.
**GCP Collector Management**

📊 **View GCP Collectors**: A management interface displays your configured Google Cloud Platform data collectors.

➕ **Add New Collector**: Click "Add new collector" to configure a new GCP data connection.

> 💡 **Portal-Only Feature**: This configuration interface is only available in the Microsoft Sentinel portal.

**GCP Connection Configuration**

When you click "Add new collector" in the portal, you'll be prompted to provide:
- **Project ID**: Your Google Cloud Platform project ID
- **Service Account**: GCP service account credentials with appropriate permissions
- **Subscription**: The Pub/Sub subscription to monitor for log data

> 💡 **Portal-Only Feature**: This configuration form is only available in the Microsoft Sentinel portal.

| | |
|--------------------------|---|
| **Tables Ingested** | `GKEAPIServer` |
| | `GKEApplication` |
| | `GKEAudit` |
| | `GKEControllerManager` |
| | `GKEHPADecision` |
| | `GKEScheduler` |
| **Connector Definition Files** | [GoogleKubernetesEngineLogs_ConnectorDefinition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Google%20Kubernetes%20Engine/Data%20Connectors/GoogleKubernetesEngineLogs_ccp/GoogleKubernetesEngineLogs_ConnectorDefinition.json) |

[→ View full connector details](../connectors/gkeccpdefinition.md)

## Tables Reference

This solution ingests data into **6 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `GKEAPIServer` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEApplication` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEAudit` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEControllerManager` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEHPADecision` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |
| `GKEScheduler` | [Google Kubernetes Engine (via Codeless Connector Framework)](../connectors/gkeccpdefinition.md) |

[← Back to Solutions Index](../solutions-index.md)
