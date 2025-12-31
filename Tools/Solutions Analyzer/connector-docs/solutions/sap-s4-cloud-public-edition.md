# SAP S4 Cloud Public Edition

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SAP |
| **Support Tier** | Partner |
| **Support Link** | [https://api.sap.com/api/SecurityAuditLog_ODataService/overview](https://api.sap.com/api/SecurityAuditLog_ODataService/overview) |
| **Categories** | domains |
| **First Published** | 2025-09-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20S4%20Cloud%20Public%20Edition](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP%20S4%20Cloud%20Public%20Edition) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [SAP S/4HANA Cloud Public Edition](../connectors/saps4publicalerts.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ABAPAuditLog`](../tables/abapauditlog.md) | [SAP S/4HANA Cloud Public Edition](../connectors/saps4publicalerts.md) | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                  |
|-------------|--------------------------------|---------------------------------------------------------------------|
| 3.0.2       | 30-10-2025                     |DCR transform updates|
| 3.0.1       | 16-10-2025                     |DCR transform updates|
| 3.0.0       | 06-10-2025                     |Initial release|

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
