# Custom logs via AMA

| | |
|----------|-------|
| **Connector ID** | `CustomlogsviaAMA` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`ApacheHTTPServer_CL`](../tables-index.md#apachehttpserver_cl), [`JBossEvent_CL`](../tables-index.md#jbossevent_cl), [`JuniperIDP_CL`](../tables-index.md#juniperidp_cl), [`MarkLogicAudit_CL`](../tables-index.md#marklogicaudit_cl), [`MongoDBAudit_CL`](../tables-index.md#mongodbaudit_cl), [`NGINX_CL`](../tables-index.md#nginx_cl), [`OracleWebLogicServer_CL`](../tables-index.md#oracleweblogicserver_cl), [`PostgreSQL_CL`](../tables-index.md#postgresql_cl), [`SecurityBridgeLogs_CL`](../tables-index.md#securitybridgelogs_cl), [`SquidProxy_CL`](../tables-index.md#squidproxy_cl), [`Tomcat_CL`](../tables-index.md#tomcat_cl), [`Ubiquiti_CL`](../tables-index.md#ubiquiti_cl), [`VectraStream_CL`](../tables-index.md#vectrastream_cl), [`ZPA_CL`](../tables-index.md#zpa_cl), [`meraki_CL`](../tables-index.md#meraki_cl), [`vcenter_CL`](../tables-index.md#vcenter_cl) |
| **Used in Solutions** | [CustomLogsAma](../solutions/customlogsama.md) |
| **Connector Definition Files** | [CustomLogsViaAmaTemplate.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CustomLogsAma/Data%20Connectors/CustomLogsViaAmaTemplate.json) |

Many applications log information to text or JSON files instead of standard logging services, such as Windows Event logs, Syslog or CEF. The Custom Logs data connector allows you to collect events from files on both Windows and Linux computers and stream them to custom logs tables you created. While streaming the data you can parse and transform the contents using the DCR. After collecting the data, you can apply analytic rules, hunting, searching, threat intelligence, enrichments and more.



**NOTE: Use this connector for the following devices:** Cisco Meraki, Zscaler Private Access (ZPA), VMware vCenter, Apache HTTP server, Apache Tomcat, Jboss Enterprise application platform, Juniper IDP, MarkLogic Audit, MongoDB Audit, Nginx HTTP server, Oracle Weblogic server, PostgreSQL Events, Squid Proxy, Ubiquiti UniFi, SecurityBridge Threat detection SAP and AI vectra stream.

## Permissions

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**
- **Permissions**: To collect data from non-Azure VMs, they must have Azure Arc installed and enabled. [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable data collection rule**

> Custom logs are collected from both Windows and Linux agents.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `CustomLogsAMA`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.
- **Create data collection rule**

[← Back to Connectors Index](../connectors-index.md)
