# ElasticAgent

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-11-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ElasticAgent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ElasticAgent) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Elastic Agent](../connectors/elasticagent.md)

**Publisher:** Elastic

The [Elastic Agent](https://www.elastic.co/security) data connector provides the capability to ingest Elastic Agent logs, metrics, and security data into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**
- **Include custom pre-requisites if the connectivity requires - else delete customs**: Description for any custom pre-requisite

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**ElasticAgentEvent**](https://aka.ms/sentinel-ElasticAgent-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using **Elastic Agent 7.14**.

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Server where the Elastic Agent logs are forwarded.

> Logs from Elastic Agents deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
**Choose where to install the Linux agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**Choose where to install the Windows agent:**

**Install agent on Azure Windows Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install/configure: InstallAgentOnVirtualMachine**

  **Install agent on a non-Azure Windows Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install/configure: InstallAgentOnNonAzure**

**2. Configure Elastic Agent (Standalone)**

[Follow the instructions](https://www.elastic.co/guide/en/fleet/current/elastic-agent-configuration.html) to configure Elastic Agent to output to Logstash

**3. Configure Logstash to use Microsoft Logstash Output Plugin**

Follow the steps to configure Logstash to use microsoft-logstash-output-azure-loganalytics plugin:

3.1) Check if the plugin is already installed:
> ./logstash-plugin list | grep 'azure-loganalytics'
**(if the plugin is installed go to step 3.3)**

3.2) Install plugin:
> ./logstash-plugin install microsoft-logstash-output-azure-loganalytics

3.3) [Configure Logstash](https://github.com/Azure/Azure-Sentinel/tree/master/DataConnectors/microsoft-logstash-output-azure-loganalytics) to use the plugin

**4. Validate log ingestion**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using custom table specified in step 3.3 (e.g. ElasticAgentLogs_CL).

>It may take about 30 minutes until the connection streams data to your workspace.

| | |
|--------------------------|---|
| **Tables Ingested** | `ElasticAgentLogs_CL` |
| **Connector Definition Files** | [Connector_ElasticAgent.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ElasticAgent/Data%20Connectors/Connector_ElasticAgent.json) |

[→ View full connector details](../connectors/elasticagent.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ElasticAgentLogs_CL` | [Elastic Agent](../connectors/elasticagent.md) |

[← Back to Solutions Index](../solutions-index.md)
