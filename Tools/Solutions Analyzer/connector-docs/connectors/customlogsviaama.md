# Custom logs via AMA

| | |
|----------|-------|
| **Connector ID** | `CustomlogsviaAMA` |
| **Publisher** | Microsoft |
| **Used in Solutions** | [CustomLogsAma](../solutions/customlogsama.md) |
| **Connector Definition Files** | [CustomLogsViaAmaTemplate.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CustomLogsAma/Data%20Connectors/CustomLogsViaAmaTemplate.json) |

Many applications log information to text or JSON files instead of standard logging services, such as Windows Event logs, Syslog or CEF. The Custom Logs data connector allows you to collect events from files on both Windows and Linux computers and stream them to custom logs tables you created. While streaming the data you can parse and transform the contents using the DCR. After collecting the data, you can apply analytic rules, hunting, searching, threat intelligence, enrichments and more.



**NOTE: Use this connector for the following devices:** Cisco Meraki, Zscaler Private Access (ZPA), VMware vCenter, Apache HTTP server, Apache Tomcat, Jboss Enterprise application platform, Juniper IDP, MarkLogic Audit, MongoDB Audit, Nginx HTTP server, Oracle Weblogic server, PostgreSQL Events, Squid Proxy, Ubiquiti UniFi, SecurityBridge Threat detection SAP and AI vectra stream.

## Tables Ingested

This connector ingests data into the following tables:

| Table | Supports Transformations | Ingestion API Supported |
|-------|:------------------------:|:-----------------------:|
| [`ApacheHTTPServer_CL`](../tables/apachehttpserver-cl.md) | — | — |
| [`JBossEvent_CL`](../tables/jbossevent-cl.md) | — | — |
| [`JuniperIDP_CL`](../tables/juniperidp-cl.md) | — | — |
| [`MarkLogicAudit_CL`](../tables/marklogicaudit-cl.md) | — | — |
| [`MongoDBAudit_CL`](../tables/mongodbaudit-cl.md) | — | — |
| [`NGINX_CL`](../tables/nginx-cl.md) | — | — |
| [`OracleWebLogicServer_CL`](../tables/oracleweblogicserver-cl.md) | — | — |
| [`PostgreSQL_CL`](../tables/postgresql-cl.md) | — | — |
| [`SecurityBridgeLogs_CL`](../tables/securitybridgelogs-cl.md) | — | — |
| [`SquidProxy_CL`](../tables/squidproxy-cl.md) | — | — |
| [`Tomcat_CL`](../tables/tomcat-cl.md) | — | — |
| [`Ubiquiti_CL`](../tables/ubiquiti-cl.md) | — | — |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | — | — |
| [`ZPA_CL`](../tables/zpa-cl.md) | — | — |
| [`meraki_CL`](../tables/meraki-cl.md) | — | — |
| [`vcenter_CL`](../tables/vcenter-cl.md) | — | — |

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
