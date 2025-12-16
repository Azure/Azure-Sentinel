# [Deprecated] CrowdStrike Falcon Endpoint Protection via AMA

| | |
|----------|-------|
| **Connector ID** | `CrowdStrikeFalconEndpointProtectionAma` |
| **Publisher** | CrowdStrike |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md) |
| **Connector Definition Files** | [template_CrowdStrikeFalconEndpointProtectionAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/template_CrowdStrikeFalconEndpointProtectionAma.json) |

The [CrowdStrike Falcon Endpoint Protection](https://www.crowdstrike.com/endpoint-security-products/) connector allows you to easily connect your CrowdStrike Falcon Event Stream with Microsoft Sentinel, to create custom dashboards, alerts, and improve investigation. This gives you more insight into your organization's endpoints and improves your security operation capabilities.<p><span style='color:red; font-weight:bold;'>NOTE:</span> This data connector has been deprecated, consider moving to the CCP data connector available in the solution which replaces ingestion via the <a href='https://learn.microsoft.com/en-us/azure/azure-monitor/logs/custom-logs-migrate' style='color:#1890F1;'>deprecated HTTP Data Collector API</a>.</p>

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Crowd Strike Falcon Endpoint Protection and load the function code or click [here](https://aka.ms/sentinel-crowdstrikefalconendpointprotection-parser), on the second line of the query, enter the hostname(s) of your CrowdStrikeFalcon device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward CrowdStrike Falcon Event Stream logs to a Syslog agent**

  Deploy the CrowdStrike Falcon SIEM Collector to forward Syslog messages in CEF format to your Microsoft Sentinel workspace via the Syslog agent.
1. [Follow these instructions](https://www.crowdstrike.com/blog/tech-center/integrate-with-your-siem/) to deploy the SIEM Collector and forward syslog
2. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address.

  **Step C. Validate connection**

  Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

 1. Make sure that you have Python on your machine using the following command: python -version

2. You must have elevated permissions (sudo) on your machine
  - **Run the following command to validate your connectivity:**: `sudo wget -O Sentinel_AMA_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/Syslog/Sentinel_AMA_troubleshoot.py&&sudo python Sentinel_AMA_troubleshoot.py --cef`

**2. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

[← Back to Connectors Index](../connectors-index.md)
