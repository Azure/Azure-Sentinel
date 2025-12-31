# Dynatrace

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Dynatrace |
| **Support Tier** | Partner |
| **Support Link** | [https://www.dynatrace.com/services-support/](https://www.dynatrace.com/services-support/) |
| **Categories** | domains |
| **First Published** | 2022-10-18 |
| **Last Updated** | 2023-10-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace) |

## Data Connectors

This solution provides **4 data connector(s)**:

- [Dynatrace Attacks](../connectors/dynatraceattacks.md)
- [Dynatrace Audit Logs](../connectors/dynatraceauditlogs.md)
- [Dynatrace Problems](../connectors/dynatraceproblems.md)
- [Dynatrace Runtime Vulnerabilities](../connectors/dynatraceruntimevulnerabilities.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`DynatraceAttacks_CL`](../tables/dynatraceattacks-cl.md) | [Dynatrace Attacks](../connectors/dynatraceattacks.md) | Analytics, Workbooks |
| [`DynatraceAuditLogs_CL`](../tables/dynatraceauditlogs-cl.md) | [Dynatrace Audit Logs](../connectors/dynatraceauditlogs.md) | Workbooks |
| [`DynatraceProblems_CL`](../tables/dynatraceproblems-cl.md) | [Dynatrace Problems](../connectors/dynatraceproblems.md) | Analytics, Workbooks |
| [`DynatraceSecurityProblems_CL`](../tables/dynatracesecurityproblems-cl.md) | [Dynatrace Runtime Vulnerabilities](../connectors/dynatraceruntimevulnerabilities.md) | Analytics, Workbooks |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | - | Playbooks |

## Content Items

This solution includes **16 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 6 |
| Analytic Rules | 5 |
| Parsers | 4 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Dynatrace - Problem detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Analytic%20Rules/Dynatrace_ProblemDetection.yaml) | Informational | DefenseEvasion, Execution, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`DynatraceProblems_CL`](../tables/dynatraceproblems-cl.md) |
| [Dynatrace Application Security - Attack detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Analytic%20Rules/DynatraceApplicationSecurity_AttackDetection.yaml) | High | Execution, Impact, InitialAccess, PrivilegeEscalation | [`DynatraceAttacks_CL`](../tables/dynatraceattacks-cl.md) |
| [Dynatrace Application Security - Code-Level runtime vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Analytic%20Rules/DynatraceApplicationSecurity_CodeLevelVulnerabilityDetection.yaml) | Medium | DefenseEvasion, Execution, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`DynatraceSecurityProblems_CL`](../tables/dynatracesecurityproblems-cl.md) |
| [Dynatrace Application Security - Non-critical runtime vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Analytic%20Rules/DynatraceApplicationSecurity_NonCriticalVulnerabilityDetection.yaml) | Informational | DefenseEvasion, Execution, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`DynatraceSecurityProblems_CL`](../tables/dynatracesecurityproblems-cl.md) |
| [Dynatrace Application Security - Third-Party runtime vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Analytic%20Rules/DynatraceApplicationSecurity_ThirdPartyVulnerabilityDetection.yaml) | Medium | DefenseEvasion, Execution, Impact, InitialAccess, LateralMovement, Persistence, PrivilegeEscalation | [`DynatraceSecurityProblems_CL`](../tables/dynatracesecurityproblems-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Dynatrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Workbooks/Dynatrace.json) | [`DynatraceAttacks_CL`](../tables/dynatraceattacks-cl.md)<br>[`DynatraceAuditLogs_CL`](../tables/dynatraceauditlogs-cl.md)<br>[`DynatraceProblems_CL`](../tables/dynatraceproblems-cl.md)<br>[`DynatraceSecurityProblems_CL`](../tables/dynatracesecurityproblems-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Add Dynatrace Application Security Attack Source IP Address to Threat Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Playbooks/Add_DynatraceApplicationSecurityAttackSourceIpThreatIntelligence/azuredeploy.json) | This playbook will add an attackers source ip to Threat Intelligence when a new incident is opened i... | - |
| [Enrich Dynatrace Application Security Attack Incident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Playbooks/Enrich_DynatraceApplicationSecurityAttackIncident/azuredeploy.json) | This playbook will enriche Dynatrace Application Security Attack Incidents with additional informati... | - |
| [Enrich Dynatrace Application Security Attack with related Microsoft Defender XDR insights](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Playbooks/Enrich-DynatraceAppSecAttackMSDefenderXDR/azuredeploy.json) | This playbook will enrich Dynatrace Application Security Attack with related Microsoft Defender XDR ... | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) *(read)* |
| [Enrich Dynatrace Application Security Attack with related Microsoft Sentinel Security Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Playbooks/Enrich-DynatraceAppSecAttackWithSecurityAlerts/azuredeploy.json) | This playbook will enrich Dynatrace Application Security Attack with related Microsoft Sentinel Secu... | *Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) *(read)* |
| [Ingest Microsoft Defender XDR insights into Dynatrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Playbooks/Ingest-DynatraceMSDefenderXDR/azuredeploy.json) | This playbook will ingest Microsoft Defender XDR insights into Dynatrace. | - |
| [Ingest Microsoft Sentinel Security Alerts into Dynatrace](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Playbooks/Ingest-DynatraceMSSentinelSecurityAlerts/azuredeploy.json) | This playbook will ingest Microsoft Sentinel Security Alerts into Dynatrace. | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [DynatraceAttacks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Parsers/DynatraceAttacks.yaml) | - | - |
| [DynatraceAuditLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Parsers/DynatraceAuditLogs.yaml) | - | - |
| [DynatraceProblems](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Parsers/DynatraceProblems.yaml) | - | - |
| [DynatraceSecurityProblems](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Dynatrace/Parsers/DynatraceSecurityProblems.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.2       | 03-05-2024                     | Repackaged for parser issue fix on reinstall                       |
| 3.0.1       | 18-01-2024                     | Changes for rebranding from Microsoft 365 Defender to Microsoft Defender XDR,         |
|             |                                | Updated user-agent strings used when calling Dynatrace REST API's,                    |
|             |                                | Added new Entity Mappings to **Analytic Rules**                                       |
|             |                                | Aligned Playbook, Data Connector & Workbook version numbers with rest of solution     |
| 3.0.0       | 16-10-2023                     | Enabled new api paging mode on **Data Connector** to fix issues related to polling Dynatrace REST API's with a large number of results.   |
| 2.0.0       | 18-10-2022                     | Initial Solution Release.   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
