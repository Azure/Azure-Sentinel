# [Deprecated] Trend Micro Apex One via AMA

| | |
|----------|-------|
| **Connector ID** | `TrendMicroApexOneAma` |
| **Publisher** | Trend Micro |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Trend Micro Apex One](../solutions/trend-micro-apex-one.md) |
| **Connector Definition Files** | [template_TrendMicro_ApexOneAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Trend%20Micro%20Apex%20One/Data%20Connectors/template_TrendMicro_ApexOneAMA.json) |

The [Trend Micro Apex One](https://www.trendmicro.com/en_us/business/products/user-protection/sps/endpoint.html) data connector provides the capability to ingest [Trend Micro Apex One events](https://aka.ms/sentinel-TrendMicroApex-OneEvents) into Microsoft Sentinel. Refer to [Trend Micro Apex Central](https://aka.ms/sentinel-TrendMicroApex-OneCentral) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>This data connector depends on a parser based on a Kusto Function to work as expected [**TMApexOneEvent**](https://aka.ms/sentinel-TMApexOneEvent-parser) which is deployed with the Microsoft Sentinel Solution.
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Forward Common Event Format (CEF) logs to Syslog agent**

  [Follow these steps](https://docs.trendmicro.com/en-us/enterprise/trend-micro-apex-central-2019-online-help/detections/logs_001/syslog-forwarding.aspx) to configure Apex Central sending alerts via syslog. While configuring, on step 6, select the log format **CEF**.

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
