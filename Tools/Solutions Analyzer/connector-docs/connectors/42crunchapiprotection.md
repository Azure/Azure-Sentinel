# API Protection

| | |
|----------|-------|
| **Connector ID** | `42CrunchAPIProtection` |
| **Publisher** | 42Crunch |
| **Tables Ingested** | [`apifirewall_log_1_CL`](../tables-index.md#apifirewall_log_1_cl) |
| **Used in Solutions** | [42Crunch API Protection](../solutions/42crunch-api-protection.md) |
| **Connector Definition Files** | [42CrunchAPIProtection.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/42Crunch%20API%20Protection/Data%20Connectors/42CrunchAPIProtection.json) |

Connects the 42Crunch API protection to Azure Log Analytics via the REST API interface

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Step 1 : Read the detailed documentation**

The installation process is documented in great detail in the GitHub repository [Microsoft Sentinel integration](https://github.com/42Crunch/azure-sentinel-integration). The user should consult this repository further to understand installation and debug of the integration.

**2. Step 2: Retrieve the workspace access credentials**

The first installation step is to retrieve both your **Workspace ID** and **Primary Key** from the Microsoft Sentinel platform.
Copy the values shown below and save them for configuration of the API log forwarder integration.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

**3. Step 3: Install the 42Crunch protection and log forwarder**

The next step is to install the 42Crunch protection and log forwarder to protect your API. Both components are availabe as containers from the [42Crunch repository](https://hub.docker.com/u/42crunch). The exact installation will depend on your environment, consult the [42Crunch protection documentation](https://docs.42crunch.com/latest/content/concepts/api_firewall_deployment_architecture.htm) for full details. Two common installation scenarios are described below:
**Installation via Docker Compose**

  The solution can be installed using a [Docker compose file](https://github.com/42Crunch/azure-sentinel-integration/blob/main/sample-deployment/docker-compose.yml).

  **Installation via Helm charts**

  The solution can be installed using a [Helm chart](https://github.com/42Crunch/azure-sentinel-integration/tree/main/helm/sentinel).
**4. Step 4: Test the data ingestion**

In order to test the data ingestion the user should deploy the sample *httpbin* application alongside the 42Crunch protection and log forwarder [described in detail here](https://github.com/42Crunch/azure-sentinel-integration/tree/main/sample-deployment).
**4.1 Install the sample**

  The sample application can be installed locally using a [Docker compose file](https://github.com/42Crunch/azure-sentinel-integration/blob/main/sample-deployment/docker-compose.yml) which will install the httpbin API server, the 42Crunch API protection and the Microsoft Sentinel log forwarder. Set the environment variables as required using the values copied from step 2.

  **4.2 Run the sample**

  Verfify the API protection is connected to the 42Crunch platform, and then exercise the API locally on the *localhost* at port 8080 using Postman, curl, or similar. You should see a mixture of passing and failing API calls.

  **4.3 Verify the data ingestion on Log Analytics**

  After approximately 20 minutes access the Log Analytics workspace on your Microsoft Sentinel installation, and locate the *Custom Logs* section verify that a *apifirewall_log_1_CL* table exists. Use the sample queries to examine the data.

[← Back to Connectors Index](../connectors-index.md)
