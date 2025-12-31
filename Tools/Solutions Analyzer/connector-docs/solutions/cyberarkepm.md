# CyberArkEPM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CyberArk Support |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyberark.com/services-support/technical-support-contact/](https://www.cyberark.com/services-support/technical-support-contact/) |
| **Categories** | domains |
| **First Published** | 2022-04-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CyberArkEPM](../connectors/cyberarkepm.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) | [CyberArkEPM](../connectors/cyberarkepm.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **22 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CyberArkEPM - Attack attempt not blocked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMAttackAttemptNotBlocked.yaml) | High | Execution | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - MSBuild usage as LOLBin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMMSBuildLOLBin.yaml) | Medium | DefenseEvasion | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Multiple attack types](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMMultipleAttackAttempts.yaml) | High | Execution | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Possible execution of Powershell Empire](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMPossibleExecutionOfPowershellEmpire.yaml) | High | Execution | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Process started from different locations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMProcessChangedStartLocation.yaml) | Medium | Execution, DefenseEvasion | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Renamed Windows binary](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMRenamedWindowsBinary.yaml) | High | Execution, DefenseEvasion | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Uncommon Windows process started from System folder](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMNewProcessStartetFromSystem.yaml) | Medium | Execution, DefenseEvasion | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Uncommon process Internet access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMRareProcInternetAccess.yaml) | High | Execution, DefenseEvasion, CommandAndControl | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Unexpected executable extension](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMUnexpectedExecutableExtension.yaml) | Medium | Execution, DefenseEvasion | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Unexpected executable location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Analytic%20Rules/CyberArkEPMUnexpectedExecutableLocation.yaml) | Medium | Execution, DefenseEvasion | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [CyberArkEPM - Elevation requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMElevationRequests.yaml) | Execution, PrivilegeEscalation | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Powershell downloads](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMPowershellDownloads.yaml) | Execution | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Powershell scripts execution parameters](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMPowershellExecutionParameters.yaml) | Execution | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Process hash changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMProcessNewHash.yaml) | DefenseEvasion | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Processes run as admin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMProcessesRunAsAdmin.yaml) | Execution, PrivilegeEscalation | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Processes with Internet access attempts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMProcessesAccessedInternet.yaml) | CommandAndControl | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Rare process run by users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMRareProcessesRunByUsers.yaml) | Execution | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Rare process vendors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMRareProcVendors.yaml) | Execution | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Scripts executed on hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMScriptsExecuted.yaml) | Execution | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |
| [CyberArkEPM - Suspicious activity attempts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Hunting%20Queries/CyberArkEPMSuspiciousActivityAttempts.yaml) | Execution | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CyberArkEPM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Workbooks/CyberArkEPM.json) | [`CyberArkEPM_CL`](../tables/cyberarkepm-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CyberArkEPM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArkEPM/Parsers/CyberArkEPM.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                         |
|-------------|--------------------------------|------------------------------------------------------------|
| 3.0.0       | 27-07-2023                     | Updated solution to fix deployment validations             | 
| 3.0.1       | 28-04-2025                     | Updated deployment instructions to use Python 3.10 version |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
