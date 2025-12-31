# VMWareESXi

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-01-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] VMware ESXi](../connectors/vmwareesxi.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | [[Deprecated] VMware ESXi](../connectors/vmwareesxi.md) | Analytics, Hunting, Workbooks |

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
| [VMware ESXi - Dormant VM started](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiDormantVMStarted.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Low patch disk space](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiLowPatchDiskSpace.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Low temp directory space](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiLowTempDirSpace.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Multiple Failed Shell Login via SSH](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiMultipleFailedSSHLogin.yaml) | Medium | CredentialAccess | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Multiple VMs stopped](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiMultipleVMStopped.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Multiple new VMs started](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiMultipleNewVM.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - New VM started](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiNewVM.yaml) | Medium | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Root impersonation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiRootImpersonation.yaml) | Medium | PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Root login](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiRootLogin.yaml) | High | InitialAccess, PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Root password changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiRootPasswordChange.yaml) | High | InitialAccess, Persistence, DefenseEvasion | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - SSH Enable on ESXi Host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiSSHEnableOnHost.yaml) | High | LateralMovement | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Shared or stolen root account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiSharedOrStolenRootAccount.yaml) | High | InitialAccess, PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Unexpected disk image](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiUnexpectedDiskImage.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - VM stopped](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Analytic%20Rules/ESXiVMStopped.yaml) | Medium | Impact | [`Syslog`](../tables/syslog.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [VMware ESXi - Download errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiDownloadErrors.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - List of dormant users.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiDormantUsers.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - List of powered off VMs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiVMPoweredOff.yaml) | Impact | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - List of powered on VMs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiVMPoweredOn.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - List of unused VMs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiUnusedVMs.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - List of virtual disks (images)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiVirtualImagesList.yaml) | Impact | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - NFC download activities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiNFCDownloadActivities.yaml) | InitialAccess | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Root logins](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiRootLogins.yaml) | InitialAccess, PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - Root logins failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiRootLoginFailure.yaml) | InitialAccess, PrivilegeEscalation | [`Syslog`](../tables/syslog.md) |
| [VMware ESXi - VM high resource load](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Hunting%20Queries/ESXiVMHighLoad.yaml) | Impact | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [VMWareESXi](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Workbooks/VMWareESXi.json) | [`Syslog`](../tables/syslog.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [VMwareESXi](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VMWareESXi/Parsers/VMwareESXi.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                     |
|-------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.5       | 03-11-2025                     | Added new **Analytic Rule** (VMware ESXi - Root change password) and (VMware ESXi - Multiple Failed SSH Login)      |
| 3.0.4       | 09-10-2025                     | Added new **Analytic Rule** (VMware ESXi - SSH Enable on ESXi Host)    |
| 3.0.3       | 02-12-2024                     | Removed Deprecated **Data connectors**                                 |
| 3.0.2       | 01-08-2024                     | Update **Parser** as part of Syslog migration                          |
|             |                                | Deprecating data connectors                                            |
| 3.0.1       | 30-04-2024                     | Repackaged for parser name issue                                       |
| 3.0.0       | 15-04-2024                     | Updated **Parser** VMwareESXi.yaml to automatic update applicable logs |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
