# [Deprecated] McAfee Network Security Platform

| | |
|----------|-------|
| **Connector ID** | `McAfeeNSP` |
| **Publisher** | McAfee |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [McAfee Network Security Platform](../solutions/mcafee-network-security-platform.md) |
| **Connector Definition Files** | [McAfeeNSP.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20Network%20Security%20Platform/Data%20Connectors/McAfeeNSP.json) |

The [McAfee® Network Security Platform](https://www.mcafee.com/enterprise/en-us/products/network-security-platform.html) data connector provides the capability to ingest [McAfee® Network Security Platform events](https://docs.mcafee.com/bundle/network-security-platform-10.1.x-integration-guide-unmanaged/page/GUID-8C706BE9-6AC9-4641-8A53-8910B51207D8.html) into Microsoft Sentinel. Refer to [McAfee® Network Security Platform](https://docs.mcafee.com/bundle/network-security-platform-10.1.x-integration-guide-unmanaged/page/GUID-F7D281EC-1CC9-4962-A7A3-5A9D9584670E.html) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**McAfeeNSPEvent**](https://aka.ms/sentinel-mcafeensp-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using McAfee® Network Security Platform version: 10.1.x

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Server where the McAfee® Network Security Platform logs are forwarded.

> Logs from McAfee® Network Security Platform Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

**2. Configure McAfee® Network Security Platform event forwarding**

Follow the configuration steps below to get McAfee® Network Security Platform logs into Microsoft Sentinel.
1. [Follow these instructions](https://docs.mcafee.com/bundle/network-security-platform-10.1.x-product-guide/page/GUID-E4A687B0-FAFB-4170-AC94-1D968A10380F.html) to forward alerts from the Manager to a syslog server.
2. Add a syslog notification profile, [more details here](https://docs.mcafee.com/bundle/network-security-platform-10.1.x-product-guide/page/GUID-5BADD5D7-21AE-4E3B-AEE2-A079F3FD6A38.html). This is mandatory. While creating profile, to make sure that events are formatted correctly, enter the following text in the Message text box:
		<SyslogAlertForwarderNSP>:|SENSOR_ALERT_UUID|ALERT_TYPE|ATTACK_TIME|ATTACK_NAME|ATTACK_ID
		|ATTACK_SEVERITY|ATTACK_SIGNATURE|ATTACK_CONFIDENCE|ADMIN_DOMAIN|SENSOR_NAME|INTERFACE
		|SOURCE_IP|SOURCE_PORT|DESTINATION_IP|DESTINATION_PORT|CATEGORY|SUB_CATEGORY
		|DIRECTION|RESULT_STATUS|DETECTION_MECHANISM|APPLICATION_PROTOCOL|NETWORK_PROTOCOL|

[← Back to Connectors Index](../connectors-index.md)
