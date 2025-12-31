# Azure SQL Database solution for sentinel

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-08-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Azure SQL Databases](../connectors/azuresql.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AzureDiagnostics`](../tables/azurediagnostics.md) | [Azure SQL Databases](../connectors/azuresql.md) | Analytics, Hunting, Workbooks |
| [`anomalyData`](../tables/anomalydata.md) | - | Hunting |
| [`queryData`](../tables/querydata.md) | - | Hunting |
| [`securityresources`](../tables/securityresources.md) | - | Workbooks |

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | - | Workbooks |
| [`SecurityIncident`](../tables/securityincident.md) | - | Workbooks |

## Content Items

This solution includes **19 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 8 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Affected rows stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-VolumeAffectedRowsStatefulAnomalyOnDatabase.yaml) | Medium | Impact | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Credential errors stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-ErrorsCredentialStatefulAnomalyOnDatabase.yaml) | Medium | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Drop attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsDropStatefulAnomalyOnDatabase.yaml) | Medium | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Execution attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsExecutionStatefulAnomalyOnDatabase.yaml) | Medium | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Firewall errors stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-ErrorsFirewallStatefulAnomalyOnDatabase.yaml) | Medium | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Firewall rule manipulation attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsFirewallRuleStatefulAnomalyOnDatabase.yaml) | Medium | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [OLE object manipulation attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsOLEObjectStatefulAnomalyOnDatabase.yaml) | Medium | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Outgoing connection attempts stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-HotwordsOutgoingStatefulAnomalyOnDatabase.yaml) | Medium | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Response rows stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-VolumeResponseRowsStatefulAnomalyOnDatabase.yaml) | Medium | Exfiltration | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Syntax errors stateful anomaly on database](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Analytic%20Rules/Detection-ErrorsSyntaxStatefulAnomalyOnDatabase.yaml) | Medium | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Affected rows stateful anomaly on database - hunting query](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-VolumeAffectedRowsStatefulAnomalyOnDatabase.yaml) | Impact | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Anomalous Query Execution Time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-AffectedRowAnomaly.yaml) | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Anomalous Query Execution Time](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-ExecutionTimeAnomaly.yaml) | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Boolean Blind SQL Injection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-BooleanBlindSQLi.yaml) | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`queryData`](../tables/querydata.md) |
| [Prevalence Based SQL Query Size Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-PrevalenceBasedQuerySizeAnomaly.yaml) | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`anomalyData`](../tables/anomalydata.md) |
| [Response rows stateful anomaly on database - hunting query](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-VolumeResponseRowsStatefulAnomalyOnDatabase.yaml) | Exfiltration | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Suspicious SQL Stored Procedures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-SuspiciousStoredProcedures.yaml) | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |
| [Time Based SQL Query Size Anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Hunting%20Queries/HuntingQuery-TimeBasedQuerySizeAnomaly.yaml) | InitialAccess | [`AzureDiagnostics`](../tables/azurediagnostics.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Workbook-AzureSQLSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Azure%20SQL%20Database%20solution%20for%20sentinel/Workbooks/Workbook-AzureSQLSecurity.json) | [`AzureDiagnostics`](../tables/azurediagnostics.md)<br>[`securityresources`](../tables/securityresources.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md)<br>[`SecurityIncident`](../tables/securityincident.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                       |
|-------------|--------------------------------|--------------------------------------------------------------------------|   
| 3.0.0       | 25-10-2024                     | Updated description of CreateUi and **Analytic Rule**					  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
