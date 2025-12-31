# McAfee ePolicy Orchestrator

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2021-03-25 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] McAfee ePolicy Orchestrator (ePO)](../connectors/mcafeeepo.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] McAfee ePolicy Orchestrator (ePO)](../connectors/mcafeeepo.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **26 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 14 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [McAfee ePO - Agent Handler down](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOAgentHandlerDown.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Attempt uninstall McAfee agent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOAttemptUninstallAgent.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Deployment failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPODeploymentFailed.yaml) | High | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Error sending alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOAlertError.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - File added to exceptions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOExceptionAdded.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Firewall disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOFirewallDisabled.yaml) | Medium | DefenseEvasion, CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Logging error occurred](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOLoggingError.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Multiple threats on same host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOMultipleThreatsSameHost.yaml) | Medium | InitialAccess, Persistence, DefenseEvasion, PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Scanning engine disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOScanningEngineDisabled.yaml) | Low | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Spam Email detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOSpamEmail.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Task error](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOTaskError.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Threat was not blocked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOThreatNotBlocked.yaml) | High | InitialAccess, PrivilegeEscalation, DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Unable to clean or delete infected file](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOUnableCleanDeleteInfectedFile.yaml) | High | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Update failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Analytic%20Rules/McAfeeEPOUpdateFailed.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [McAfee ePO - Agent Errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOAgentErrors.yaml) | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Applications blocked or contained](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOApplicationsBlocked.yaml) | InitialAccess, Execution | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Email Treats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOEmailThreats.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Infected Systems](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOInfectedSystems.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Infected files by source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOInfectedFiles.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Long term infected systems](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOLongTermInfectedSystems.yaml) | InitialAccess, Persistence | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Objects not scanned](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOObjectsNotScanned.yaml) | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Scan Errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOScanErrors.yaml) | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Sources with multiple threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOMultipleThreats.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [McAfee ePO - Threats detected and not blocked, cleaned or deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Hunting%20Queries/McAfeeEPOThreatNotBlocked.yaml) | Persistence, PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [McAfeeePOOverview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Workbooks/McAfeeePOOverview.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [McAfeeEPOEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/McAfee%20ePolicy%20Orchestrator/Parsers/McAfeeEPOEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                         |
|-------------|--------------------------------|----------------------------------------------------------------------------|
| 3.0.2       | 18-12-2024                     | Removed Deprecated **Data Connector**                                      |
| 3.0.1       | 24-07-2024                     | Deprecated data connectors                                                 |
| 3.0.0       | 16-07-2024                     | Updated **Data Connector** Description                                     |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
