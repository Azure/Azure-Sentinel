# Cisco Firepower EStreamer

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cisco |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cisco.com/c/en_in/support/index.html](https://www.cisco.com/c/en_in/support/index.html) |
| **Categories** | domains |
| **First Published** | 2022-05-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] Cisco Firepower eStreamer via Legacy Agent](../connectors/ciscofirepowerestreamer.md)

**Publisher:** Cisco

### [[Deprecated] Cisco Firepower eStreamer via AMA](../connectors/ciscofirepowerestreamerama.md)

**Publisher:** Cisco

eStreamer is a Client Server API designed for the Cisco Firepower NGFW Solution. The eStreamer client requests detailed event data on behalf of the SIEM or logging solution in the Common Event Format (CEF).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Custom Permissions:**

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Kindly follow the steps to configure the data connector**

**Step A. Configure the Common Event Format (CEF) via AMA data connector**

  _Note:- CEF logs are collected only from Linux Agents_

1. Navigate to Microsoft Sentinel workspace ---> configuration ---> Data connector blade .

2. Search for 'Common Event Format (CEF) via AMA' data connector and open it.

3. Check If there is no existing DCR configured to collect required facility of logs, Create a new DCR (Data Collection Rule)

	_Note:- It is recommended to install minimum 1.27 version of AMA agent [Learn more](https://learn.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-manage?tabs=azure-portal ) and ensure there is no duplicate DCR as it can cause log duplicacy_

4. Run the command provided in the CEF via AMA data connector page to configure the CEF collector on the machine

  **Step B. Install the Firepower eNcore client**

  Install and configure the Firepower eNcore eStreamer client, for more details see full install [guide](https://www.cisco.com/c/en/us/td/docs/security/firepower/670/api/eStreamer_enCore/eStreamereNcoreSentinelOperationsGuide_409.html)
**1. Download the Firepower Connector from github**

    Download the latest version of the Firepower eNcore connector for Microsoft Sentinel [here](https://github.com/CiscoSecurity/fp-05-microsoft-sentinel-connector).  If you plan on using python3 use the [python3 eStreamer connector](https://github.com/CiscoSecurity/fp-05-microsoft-sentinel-connector/tree/python3)

    **2. Create a pkcs12 file using the Azure/VM Ip Address**

    Create a pkcs12 certificate using the public IP of the VM instance in Firepower under System->Integration->eStreamer, for more information please see install [guide](https://www.cisco.com/c/en/us/td/docs/security/firepower/670/api/eStreamer_enCore/eStreamereNcoreSentinelOperationsGuide_409.html#_Toc527049443)

    **3.  Test Connectivity between the Azure/VM Client and the FMC**

    Copy the pkcs12 file from the FMC to the Azure/VM instance and run the test utility (./encore.sh test) to ensure a connection can be established, for more details please see the setup [guide](https://www.cisco.com/c/en/us/td/docs/security/firepower/670/api/eStreamer_enCore/eStreamereNcoreSentinelOperationsGuide_409.html#_Toc527049430)

    **4. Configure encore to stream data to the agent**

    Configure encore to stream data via TCP to the Microsoft Agent, this should be enabled by default, however, additional ports and streaming protocols can configured depending on your network security posture, it is also possible to save the data to the file system, for more information please see [Configure Encore](https://www.cisco.com/c/en/us/td/docs/security/firepower/670/api/eStreamer_enCore/eStreamereNcoreSentinelOperationsGuide_409.html#_Toc527049433)
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

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_CiscoFirepowerEStreamerAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Firepower%20EStreamer/Data%20Connectors/template_CiscoFirepowerEStreamerAMA.json) |

[→ View full connector details](../connectors/ciscofirepowerestreamerama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Cisco Firepower eStreamer via AMA](../connectors/ciscofirepowerestreamerama.md), [[Deprecated] Cisco Firepower eStreamer via Legacy Agent](../connectors/ciscofirepowerestreamer.md) |

[← Back to Solutions Index](../solutions-index.md)
