# AristaAwakeSecurity

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Arista - Awake Security |
| **Support Tier** | Partner |
| **Support Link** | [https://awakesecurity.com/](https://awakesecurity.com/) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [[Deprecated] Awake Security via Legacy Agent](../connectors/aristaawakesecurity.md)

**Publisher:** Arista Networks

The Awake Security CEF connector allows users to send detection model matches from the Awake Security Platform to Microsoft Sentinel. Remediate threats quickly with the power of network detection and response and speed up investigations with deep visibility especially into unmanaged entities including users, devices and applications on your network. The connector also enables the creation of network security-focused custom alerts, incidents, workbooks and notebooks that align with your existing security operations workflows. 

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Linux Syslog agent configuration**

Install and configure the Linux agent to collect your Common Event Format (CEF) Syslog messages and forward them to Microsoft Sentinel.

> Notice that the data from all regions will be stored in the selected workspace
**1.1 Select or create a Linux machine**

  Select or create a Linux machine that Microsoft Sentinel will use as the proxy between your security solution and Microsoft Sentinel this machine can be on your on-prem environment, Azure or other clouds.

  **1.2 Install the CEF collector on the Linux machine**

  Install the Microsoft Monitoring Agent on your Linux machine and configure the machine to listen on the necessary port and forward messages to your Microsoft Sentinel workspace. The CEF collector collects CEF messages on port 514 TCP.

> 1. Make sure that you have Python on your machine using the following command: python -version.

> 2. You must have elevated permissions (sudo) on your machine.
  - **Run the following command to install and apply the CEF collector:**: `sudo wget -O cef_installer.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_installer.py&&sudo python cef_installer.py {0} {1}`
**2. Forward Awake Adversarial Model match results to a CEF collector.**

Perform the following steps to forward Awake Adversarial Model match results to a CEF collector listening on TCP port **514** at IP **192.168.0.1**:
- Navigate to the Detection Management Skills page in the Awake UI.
- Click + Add New Skill.
- Set the Expression field to,
>integrations.cef.tcp { destination: "192.168.0.1", port: 514, secure: false, severity: Warning }
- Set the Title field to a descriptive name like,
>Forward Awake Adversarial Model match result to Microsoft Sentinel.
- Set the Reference Identifier to something easily discoverable like,
>integrations.cef.sentinel-forwarder
- Click Save.

Note: Within a few minutes of saving the definition and other fields the system will begin sending new model match results to the CEF events collector as they are detected.

For more information, refer to the **Adding a Security Information and Event Management Push Integration** page from the Help Documentation in the Awake UI.

**3. Validate connection**

Follow the instructions to validate your connectivity:

Open Log Analytics to check if the logs are received using the CommonSecurityLog schema.

>It may take about 20 minutes until the connection streams data to your workspace.

If the logs are not received, run the following connectivity validation script:

> 1. Make sure that you have Python on your machine using the following command: python -version

>2. You must have elevated permissions (sudo) on your machine
- **Run the following command to validate your connectivity:**: `sudo wget  -O cef_troubleshoot.py https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/DataConnectors/CEF/cef_troubleshoot.py&&sudo python cef_troubleshoot.py  {0}`

**4. Secure your machine**

Make sure to configure the machine's security according to your organization's security policy


[Learn more >](https://aka.ms/SecureCEF)

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Connector_AristaAwakeSecurity_CEF.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AristaAwakeSecurity/Data%20Connectors/Connector_AristaAwakeSecurity_CEF.json) |

[→ View full connector details](../connectors/aristaawakesecurity.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] Awake Security via Legacy Agent](../connectors/aristaawakesecurity.md) |

[← Back to Solutions Index](../solutions-index.md)
