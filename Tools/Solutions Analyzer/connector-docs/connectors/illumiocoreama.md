# [Deprecated] Illumio Core via AMA

| | |
|----------|-------|
| **Connector ID** | `IllumioCoreAma` |
| **Publisher** | Illumio |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [Illumio Core](../solutions/illumio-core.md) |
| **Connector Definition Files** | [template_IllumioCoreAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Illumio%20Core/Data%20Connectors/template_IllumioCoreAMA.json) |

The [Illumio Core](https://www.illumio.com/products/) data connector provides the capability to ingest Illumio Core logs into Microsoft Sentinel.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias IllumioCoreEvent and load the function code or click [here](https://aka.ms/sentinel-IllumioCore-parser).The function usually takes 10-15 minutes to activate after solution installation/update and maps Illumio Core events to Microsoft Sentinel Information Model (ASIM).
**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine.

  **Step B. Configure Ilumio Core to send logs using CEF**

  Configure Event Format

 1. From the PCE web console menu, choose **Settings > Event Settings** to view your current settings.

 2. Click **Edit** to change the settings.

 3. Set **Event Format** to CEF.

 4. (Optional) Configure **Event Severity** and **Retention Period**.

Configure event forwarding to an external syslog server

 1. From the PCE web console menu, choose **Settings > Event Settings**.

 2. Click **Add**.

 3. Click **Add Repository**.

 4. Complete the **Add Repository** dialog.

 5. Click **OK** to save the event forwarding configuration.

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
