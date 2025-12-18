# [Deprecated] RSA® SecurID (Authentication Manager)

| | |
|----------|-------|
| **Connector ID** | `RSASecurIDAM` |
| **Publisher** | RSA |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [RSA SecurID](../solutions/rsa-securid.md) |
| **Connector Definition Files** | [RSASecurID.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/RSA%20SecurID/Data%20Connectors/RSASecurID.json) |

The [RSA® SecurID Authentication Manager](https://www.securid.com/) data connector provides the capability to ingest [RSA® SecurID Authentication Manager events](https://community.rsa.com/t5/rsa-authentication-manager/rsa-authentication-manager-log-messages/ta-p/630160) into Microsoft Sentinel. Refer to [RSA® SecurID Authentication Manager documentation](https://community.rsa.com/t5/rsa-authentication-manager/getting-started-with-rsa-authentication-manager/ta-p/569582) for more information.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**RSASecurIDAMEvent**](https://aka.ms/sentinel-rsasecuridam-parser) which is deployed with the Microsoft Sentinel Solution.

>**NOTE:** This data connector has been developed using RSA SecurID Authentication Manager version: 8.4 and 8.5

**1. Install and onboard the agent for Linux or Windows**

Install the agent on the Server where the RSA® SecurID Authentication Manager logs are forwarded.

> Logs from RSA® SecurID Authentication Manager Server deployed on Linux or Windows servers are collected by **Linux** or **Windows** agents.
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

**2. Configure RSA® SecurID Authentication Manager event forwarding**

Follow the configuration steps below to get RSA® SecurID Authentication Manager logs into Microsoft Sentinel.
1. [Follow these instructions](https://community.rsa.com/t5/rsa-authentication-manager/configure-the-remote-syslog-host-for-real-time-log-monitoring/ta-p/571374) to forward alerts from the Manager to a syslog server.

[← Back to Connectors Index](../connectors-index.md)
