# Cisco ISE

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-07-03 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Cisco Identity Services Engine](../connectors/ciscoise.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] Cisco Identity Services Engine](../connectors/ciscoise.md) | Analytics, Hunting, Workbooks |

## Content Items

This solution includes **25 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Playbooks | 3 |
| Workbooks | 1 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CiscoISE -  Command executed with the highest privileges from new IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISECmdExecutionWithHighestPrivilegesNewIP.yaml) | Medium | InitialAccess, Persistence, PrivilegeEscalation, DefenseEvasion, Execution | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Attempt to delete local store logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISEAttempDeleteLocalStoreLogs.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Backup failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISEBackupFailed.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Certificate has expired](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISECertExpired.yaml) | Medium | CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Command executed with the highest privileges by new user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISECmdExecutionWithHighestPrivilegesNewUser.yaml) | Medium | InitialAccess, Persistence, PrivilegeEscalation, DefenseEvasion, Execution | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Device PostureStatus changed to non-compliant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISEDevicePostureStatusChanged.yaml) | Medium | PrivilegeEscalation, Persistence | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Device changed IP in last 24 hours](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISEDeviceChangedIP.yaml) | Medium | CommandAndControl | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - ISE administrator password has been reset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISEAdminPasswordReset.yaml) | Medium | Persistence, PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Log collector was suspended](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISELogCollectorSuspended.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Log files deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Analytic%20Rules/CiscoISELogsDeleted.yaml) | Medium | DefenseEvasion | [`Syslog`](../tables/syslog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [CiscoISE - Attempts to suspend the log collector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISESuspendLogCollector.yaml) | DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Authentication attempts to suspended user account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISEAuthenticationToSuspendedAccount.yaml) | InitialAccess, CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Dynamic authorization failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISEDynamicAuthorizationFailed.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Expired certificate in the client certificates chain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISEExpiredCertInClientCertChain.yaml) | - | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Failed authentication events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISEFailedAuthentication.yaml) | CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Failed login attempts via SSH CLI (users)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISEFailedLoginsSSHCLI.yaml) | LateralMovement | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Guest authentication failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISEGuestAuthenticationFailed.yaml) | CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Guest authentication succeeded](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISEGuestAuthenticationSuccess.yaml) | InitialAccess, Persistence, PrivilegeEscalation, DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Rare or new useragent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISERareUserAgent.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [CiscoISE - Sources with high number of 'Failed Authentication' events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Hunting%20Queries/CiscoISESourceHighNumberAuthenticationErrors.yaml) | CredentialAccess | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CiscoISE](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Workbooks/CiscoISE.json) | [`Syslog`](../tables/syslog.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoISE-False Positives Clear Policies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Playbooks/CiscoISE-FalsePositivesClearPolicies/azuredeploy.json) | This playbook gets triggered when a new sentinel incident is created 1.For each MAC address (MACAddr... | - |
| [CiscoISE-SuspendGuestUser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Playbooks/CiscoISE-SuspendGuestUser/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |
| [CiscoISE-TakeEndpointActionFromTeams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Playbooks/CiscoISE-TakeEndpointActionFromTeams/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoISEEvent](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cisco%20ISE/Parsers/CiscoISEEvent.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYY)** | **Change History**                              |
|-------------|-------------------------------|-------------------------------------------------|
| 3.0.3       | 20-05-2025                    | Updated **Parser** to parse new fields          |
| 3.0.2       | 04-12-2024                    | Removed Deprecated **Data connectors**          |
| 3.0.1       | 23-07-2024                    | Deprecated data connectors                      |
| 3.0.0       | 11-07-2023                    | **Parser** query optimization done		        |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
