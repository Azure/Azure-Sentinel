# CiscoDuoSecurity

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cisco Systems |
| **Support Tier** | Partner |
| **Support Link** | [https://duo.com/support](https://duo.com/support) |
| **Categories** | domains |
| **First Published** | 2022-01-07 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cisco Duo Security](../connectors/ciscoduosecurity.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) | [Cisco Duo Security](../connectors/ciscoduosecurity.md) | Analytics, Hunting, Workbooks |

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
| [Cisco Duo - AD sync failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoADSyncFailed.yaml) | Medium | Impact | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Admin password reset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoAdminPasswordReset.yaml) | High | Persistence | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Admin user created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoNewAdmin.yaml) | Medium | Persistence, PrivilegeEscalation | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Admin user deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoAdminDeleted.yaml) | Medium | Impact | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Authentication device new location](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoNewAuthDeviceLocation.yaml) | Medium | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Multiple admin 2FA failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoAdminMFAFailures.yaml) | High | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Multiple user login failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoMultipleUserLoginFailures.yaml) | High | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Multiple users deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoMultipleUsersDeleted.yaml) | Medium | Impact | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - New access device](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoNewAccessDevice.yaml) | Medium | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Unexpected authentication factor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Analytic%20Rules/CiscoDuoUnexpectedAuthFactor.yaml) | Medium | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Cisco Duo - Admin failure authentications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoAdmin2FAFailure.yaml) | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Admin failure authentications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoAdminFailure.yaml) | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Authentication error reasons](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoAuthenticationErrorReasons.yaml) | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Authentication errors](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoAuthenticationErrorEvents.yaml) | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Delete actions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoAdminDeleteActions.yaml) | Impact | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Deleted users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoDeletedUsers.yaml) | Impact | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Devices with unsecure settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoUnsecuredDevices.yaml) | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Devices with vulnerable OS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoUnpachedAccessDevices.yaml) | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - Fraud authentications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoFraudAuthentication.yaml) | InitialAccess | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |
| [Cisco Duo - New users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Hunting%20Queries/CiscoDuoNewUsers.yaml) | InitialAccess, Persistence | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CiscoDuo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Workbooks/CiscoDuo.json) | [`CiscoDuo_CL`](../tables/ciscoduo-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CiscoDuo](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CiscoDuoSecurity/Parsers/CiscoDuo.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                     |
|-------------|--------------------------------|--------------------------------------------------------|
|  3.0.4      |  26-09-2025                    | Updated support **Microsoft** to **Partner**                   |
|  3.0.3      |  02-09-2025                    | Added support for new log endpoints                   |
|  3.0.2      |  16-04-2024                    | Added Deploy to Azure Goverment button for Government portal in **Dataconnector**<br/> Fixed **Parser** issue for Parser name and ParentID mismatch |
|  3.0.1      |  30-01-2024                    | Updated solution to fix **parser** query                   |
|  3.0.0      |  08-01-2024                    | Updated solution to fix Api version of saved searches  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
