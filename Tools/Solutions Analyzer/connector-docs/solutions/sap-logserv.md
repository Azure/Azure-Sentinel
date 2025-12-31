# SAP LogServ

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SAP |
| **Support Tier** | Partner |
| **Support Link** | [https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/announcing-limited-preview-of-sap-logserv-integration-with-microsoft/ba-p/13942180](https://community.sap.com/t5/enterprise-resource-planning-blogs-by-sap/announcing-limited-preview-of-sap-logserv-integration-with-microsoft/ba-p/13942180) |
| **Categories** | domains |
| **First Published** | 2025-02-17 |
| **Last Updated** | 2025-07-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [SAP LogServ (RISE), S/4HANA Cloud private edition](../connectors/saplogserv.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SAPLogServ_CL`](../tables/saplogserv-cl.md) | [SAP LogServ (RISE), S/4HANA Cloud private edition](../connectors/saplogserv.md) | Analytics, Workbooks |
| [`filteredLogs`](../tables/filteredlogs.md) | - | Workbooks |

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 4 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [SAP LogServ - HANA DB - Assign Admin Authorizations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Analytic%20Rules/SAPLogServ-AssignAdminAuthorizations.yaml) | High | PrivilegeEscalation | [`SAPLogServ_CL`](../tables/saplogserv-cl.md) |
| [SAP LogServ - HANA DB - Audit Trail Policy Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Analytic%20Rules/SAPLogServ-AuditTrailPolicyChanges.yaml) | High | Persistence, LateralMovement, DefenseEvasion | [`SAPLogServ_CL`](../tables/saplogserv-cl.md) |
| [SAP LogServ - HANA DB - Deactivation of Audit Trail](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Analytic%20Rules/SAPLogServ-DeactivationofAuditTrail.yaml) | High | Persistence, LateralMovement, DefenseEvasion | [`SAPLogServ_CL`](../tables/saplogserv-cl.md) |
| [SAP LogServ - HANA DB - User Admin actions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Analytic%20Rules/SAPLogServ-UserAdminActions.yaml) | High | PrivilegeEscalation | [`SAPLogServ_CL`](../tables/saplogserv-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [SAPLogServObserve](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20LogServ/Workbooks/SAPLogServObserve.json) | [`SAPLogServ_CL`](../tables/saplogserv-cl.md)<br>[`filteredLogs`](../tables/filteredlogs.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.4       |  11-08-2025                    | Connector UI updates |
| 3.0.3       |  17-07-2025                    | Observability Workbook added |
| 3.0.2       |  25-06-2025                    | Analytic Rules for HANA DB added |
| 3.0.1       |  09-04-2025                    | Retention setting dropped from table to default to LogAnalytics ws default |
| 3.0.0       |  17-02-2025                    | Initial Solution Release |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
