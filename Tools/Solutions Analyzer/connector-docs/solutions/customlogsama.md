# CustomLogsAma

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2024-07-21 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CustomLogsAma](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CustomLogsAma) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Custom logs via AMA](../connectors/customlogsviaama.md)

**Publisher:** Microsoft

Many applications log information to text or JSON files instead of standard logging services, such as Windows Event logs, Syslog or CEF. The Custom Logs data connector allows you to collect events from files on both Windows and Linux computers and stream them to custom logs tables you created. While streaming the data you can parse and transform the contents using the DCR. After collecting the data, you can apply analytic rules, hunting, searching, threat intelligence, enrichments and more.



**NOTE: Use this connector for the following devices:** Cisco Meraki, Zscaler Private Access (ZPA), VMware vCenter, Apache HTTP server, Apache Tomcat, Jboss Enterprise application platform, Juniper IDP, MarkLogic Audit, MongoDB Audit, Nginx HTTP server, Oracle Weblogic server, PostgreSQL Events, Squid Proxy, Ubiquiti UniFi, SecurityBridge Threat detection SAP and AI vectra stream.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace data sources** (Workspace): read and write permissions.

**Custom Permissions:**
- **Permissions**: To collect data from non-Azure VMs, they must have Azure Arc installed and enabled. [Learn more](https://docs.microsoft.com/azure/azure-monitor/agents/azure-monitor-agent-install?tabs=ARMAgentPowerShell,PowerShellWindows,PowerShellWindowsArc,CLIWindows,CLIWindowsArc)

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Enable data collection rule**

> Custom logs are collected from both Windows and Linux agents.
> 📋 **Additional Configuration Step**: This connector includes a configuration step of type `CustomLogsAMA`. Please refer to the Microsoft Sentinel portal for detailed configuration options for this step.
- **Create data collection rule**

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `ApacheHTTPServer_CL` |
| | `JBossEvent_CL` |
| | `JuniperIDP_CL` |
| | `MarkLogicAudit_CL` |
| | `MongoDBAudit_CL` |
| | `NGINX_CL` |
| | `OracleWebLogicServer_CL` |
| | `PostgreSQL_CL` |
| | `SecurityBridgeLogs_CL` |
| | `SquidProxy_CL` |
| | `Tomcat_CL` |
| | `Ubiquiti_CL` |
| | `VectraStream_CL` |
| | `ZPA_CL` |
| | `meraki_CL` |
| | `vcenter_CL` |
| **Connector Definition Files** | [CustomLogsViaAmaTemplate.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CustomLogsAma/Data%20Connectors/CustomLogsViaAmaTemplate.json) |

[→ View full connector details](../connectors/customlogsviaama.md)

## Tables Reference

This solution ingests data into **16 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ApacheHTTPServer_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `JBossEvent_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `JuniperIDP_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `MarkLogicAudit_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `MongoDBAudit_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `NGINX_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `OracleWebLogicServer_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `PostgreSQL_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `SecurityBridgeLogs_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `SquidProxy_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `Tomcat_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `Ubiquiti_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `VectraStream_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `ZPA_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `meraki_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |
| `vcenter_CL` | [Custom logs via AMA](../connectors/customlogsviaama.md) |

[← Back to Solutions Index](../solutions-index.md)
