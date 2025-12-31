# SAP BTP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2023-04-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [SAP BTP](../connectors/sapbtpauditevents.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SAPBTPAuditLog_CL`](../tables/sapbtpauditlog-cl.md) | [SAP BTP](../connectors/sapbtpauditevents.md) | Analytics, Workbooks |
| [`user_account_changes`](../tables/user-account-changes.md) | - | Workbooks |

## Content Items

This solution includes **6 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 5 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [BTP - Failed access attempts across multiple BAS subaccounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP/Analytic%20Rules/BTP%20-%20Failed%20access%20attempts%20across%20multiple%20BAS%20subaccounts.yaml) | Medium | Reconnaissance, Discovery | [`SAPBTPAuditLog_CL`](../tables/sapbtpauditlog-cl.md) |
| [BTP - Malware detected in BAS dev space](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP/Analytic%20Rules/BTP%20-%20Malware%20detected%20in%20BAS%20dev%20space.yaml) | Medium | ResourceDevelopment, Execution, Persistence | [`SAPBTPAuditLog_CL`](../tables/sapbtpauditlog-cl.md) |
| [BTP - Mass user deletion in a sub account](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP/Analytic%20Rules/BTP%20-%20Mass%20user%20deletion%20in%20a%20sub%20account.yaml) | Medium | Impact | [`SAPBTPAuditLog_CL`](../tables/sapbtpauditlog-cl.md) |
| [BTP - Trust and authorization Identity Provider monitor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP/Analytic%20Rules/BTP%20-%20Trust%20and%20authorization%20Identity%20Provider%20monitor.yaml) | Medium | CredentialAccess, PrivilegeEscalation | [`SAPBTPAuditLog_CL`](../tables/sapbtpauditlog-cl.md) |
| [BTP - User added to sensitive privileged role collection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP/Analytic%20Rules/BTP%20-%20User%20added%20to%20sensitive%20privileged%20role%20collection.yaml) | Low | LateralMovement, PrivilegeEscalation | [`SAPBTPAuditLog_CL`](../tables/sapbtpauditlog-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SAPBTPActivity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20BTP/Workbooks/SAPBTPActivity.json) | [`SAPBTPAuditLog_CL`](../tables/sapbtpauditlog-cl.md)<br>[`user_account_changes`](../tables/user-account-changes.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                  |
|-------------|--------------------------------|---------------------------------------------------------------------|
| 3.0.10      | 03-10-2025                     |Resolves data connector duplicate handle pagination errors|
| 3.0.9       | 02-09-2025                     |Connector UI fix|
| 3.0.8       | 03-12-2024                     |Removal of Function App data connector|
| 3.0.7       | 24-07-2024                     |Updated BAS malware rule after changes in source message format|
| 3.0.6       | 23-07-2024                     |Resolves ContentTemplateNotFound error for CCP|
| 3.0.5       | 15-07-2024                     |Remove data source mappings for deprecated function app connector|
| 3.0.4       | 11-07-2024                     |Move codeless connector to GA and deprecated function app connector|
| 3.0.3       | 21-06-2024                     |Fixes issue with data connector TokenEndpoint query parameter|
| 3.0.2       | 21-03-2024                     |Fix data connector version mismatch|
| 3.0.1       | 19-03-2024                     |Add data connector based on CCP with support for multiple subaccounts|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
