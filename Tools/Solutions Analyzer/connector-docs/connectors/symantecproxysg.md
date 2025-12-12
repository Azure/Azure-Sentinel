# [Deprecated] Symantec ProxySG

| | |
|----------|-------|
| **Connector ID** | `SymantecProxySG` |
| **Publisher** | Symantec |
| **Tables Ingested** | [`Syslog`](../tables-index.md#syslog) |
| **Used in Solutions** | [SymantecProxySG](../solutions/symantecproxysg.md) |
| **Connector Definition Files** | [Connector_Syslog_SymantecProxySG.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SymantecProxySG/Data%20Connectors/Connector_Syslog_SymantecProxySG.json) |

The [Symantec ProxySG](https://www.broadcom.com/products/cyber-security/network/gateway/proxy-sg-and-advanced-secure-gateway) allows you to easily connect your Symantec ProxySG logs with Microsoft Sentinel, to view dashboards, create custom alerts, and improve investigations. Integrating Symantec ProxySG with Microsoft Sentinel provides more visibility into your organization's network proxy traffic and will enhance security monitoring capabilities.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): write permission is required.

**Custom Permissions:**
- **Symantec ProxySG**: must be configured to export logs via Syslog

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected which is deployed as part of the solution. To view the function code in Log Analytics, open Log Analytics/Microsoft Sentinel Logs blade, click Functions and search for the alias Symantec Proxy SG and load the function code or click [here](https://aka.ms/sentinel-SymantecProxySG-parser), on the second line of the query, enter the hostname(s) of your Symantec Proxy SG device(s) and any other unique identifiers for the logstream. The function usually takes 10-15 minutes to activate after solution installation/update.

**1. Install and onboard the agent for Linux**

Typically, you should install the agent on a different computer from the one on which the logs are generated.

>  Syslog logs are collected only from **Linux** agents.
**Choose where to install the agent:**

**Install agent on Azure Linux Virtual Machine**

  Select the machine to install the agent on and then click **Connect**.
  - **Install agent on Linux Virtual Machine**

  **Install agent on a non-Azure Linux Machine**

  Download the agent on the relevant machine and follow the instructions.
  - **Install agent on Linux (Non-Azure)**

**2. Configure the logs to be collected**

Configure the facilities you want to collect and their severities.
 1. Under workspace advanced settings **Configuration**, select **Data** and then **Syslog**.
 2. Select **Apply below configuration to my machines** and select the facilities and severities.
 3.  Click **Save**.
- **Open Syslog settings**

**3. Configure and connect the Symantec ProxySG**

1. Log in to the Blue Coat Management Console .
 2. Select Configuration > Access Logging > Formats.
 3. Select New.
 4.  Enter a unique name in the Format Name field.
 5. Click the radio button for  **Custom format string**  and paste the following string into the field.
 <p><code>1 $(date) $(time) $(time-taken) $(c-ip) $(cs-userdn) $(cs-auth-groups) $(x-exception-id) $(sc-filter-result) $(cs-categories) $(quot)$(cs(Referer))$(quot) $(sc-status) $(s-action) $(cs-method) $(quot)$(rs(Content-Type))$(quot) $(cs-uri-scheme) $(cs-host) $(cs-uri-port) $(cs-uri-path) $(cs-uri-query) $(cs-uri-extension) $(quot)$(cs(User-Agent))$(quot) $(s-ip) $(sr-bytes) $(rs-bytes) $(x-virus-id) $(x-bluecoat-application-name) $(x-bluecoat-application-operation) $(cs-uri-port) $(x-cs-client-ip-country) $(cs-threat-risk)</code></p>
 6. Click the **OK** button. 
 7. Click the **Apply** button. 
 8. [Follow these instructions](https://knowledge.broadcom.com/external/article/166529/sending-access-logs-to-a-syslog-server.html) to enable syslog streaming of **Access** Logs. Use the IP address or hostname for the Linux device with the Linux agent installed as the Destination IP address

[← Back to Connectors Index](../connectors-index.md)
