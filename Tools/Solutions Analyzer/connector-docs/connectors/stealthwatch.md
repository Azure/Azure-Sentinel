# [Deprecated] Cisco Secure Cloud Analytics

| | |
|----------|-------|
| **Connector ID** | `Stealthwatch` |
| **Publisher** | Cisco |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [Cisco Secure Cloud Analytics](../solutions/cisco-secure-cloud-analytics.md) |
| **Connector Definition Files** | [Cisco_Stealthwatch_syslog.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20Secure%20Cloud%20Analytics/Data%20Connectors/Cisco_Stealthwatch_syslog.json) |

The [Cisco Secure Cloud Analytics](https://www.cisco.com/c/en/us/products/security/stealthwatch/index.html) data connector provides the capability to ingest [Cisco Secure Cloud Analytics events](https://www.cisco.com/c/dam/en/us/td/docs/security/stealthwatch/management_console/securit_events_alarm_categories/7_4_2_Security_Events_and_Alarm_Categories_DV_2_1.pdf) into Microsoft Sentinel. Refer to [Cisco Secure Cloud Analytics documentation](https://www.cisco.com/c/dam/en/us/td/docs/security/stealthwatch/system_installation_configuration/7_5_0_System_Configuration_Guide_DV_1_3.pdf) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**StealthwatchEvent**](https://aka.ms/sentinel-stealthwatch-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using Cisco Secure Cloud Analytics version 7.3.2

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Server where the Cisco Secure Cloud Analytics logs are forwarded.

> Logs from Cisco Secure Cloud Analytics Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

**2. Configure Cisco Secure Cloud Analytics event forwarding**

Follow the configuration steps below to get Cisco Secure Cloud Analytics logs into Microsoft Sentinel.
1. Log in to the Stealthwatch Management Console (SMC) as an administrator.
2. In the menu bar, click **Configuration** **>** **Response Management**.
3. From the **Actions** section in the **Response Management** menu, click **Add > Syslog Message**.
4. In the Add Syslog Message Action window, configure parameters.
5. Enter the following custom format:
|Lancope|Stealthwatch|7.3|{alarm_type_id}|0x7C|src={source_ip}|dst={target_ip}|dstPort={port}|proto={protocol}|msg={alarm_type_description}|fullmessage={details}|start={start_active_time}|end={end_active_time}|cat={alarm_category_name}|alarmID={alarm_id}|sourceHG={source_host_group_names}|targetHG={target_host_group_names}|sourceHostSnapshot={source_url}|targetHostSnapshot={target_url}|flowCollectorName={device_name}|flowCollectorIP={device_ip}|domain={domain_name}|exporterName={exporter_hostname}|exporterIPAddress={exporter_ip}|exporterInfo={exporter_label}|targetUser={target_username}|targetHostname={target_hostname}|sourceUser={source_username}|alarmStatus={alarm_status}|alarmSev={alarm_severity_name}

6. Select the custom format from the list and click **OK**
7. Click **Response Management > Rules**.
8. Click **Add** and select **Host Alarm**.
9. Provide a rule name in the **Name** field.
10. Create rules by selecting values from the Type and Options menus. To add more rules, click the ellipsis icon. For a Host Alarm, combine as many possible types in a statement as possible.

[← Back to Connectors Index](../connectors-index.md)
