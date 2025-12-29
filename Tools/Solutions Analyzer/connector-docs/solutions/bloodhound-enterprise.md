# BloodHound Enterprise

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | SpecterOps |
| **Support Tier** | Partner |
| **Support Link** | [https://bloodhoundenterprise.io/](https://bloodhoundenterprise.io/) |
| **Categories** | domains |
| **First Published** | 2023-05-04 |
| **Last Updated** | 2021-05-04 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BloodHound%20Enterprise](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BloodHound%20Enterprise) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Bloodhound Enterprise](../connectors/bloodhoundenterprise.md)

**Publisher:** SpecterOps

The solution is designed to test Bloodhound Enterprise package creation process.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `BHEAttackPathsData_CL` |
| **Connector Definition Files** | [BloodHoundFunction.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/BloodHound%20Enterprise/Data%20Connectors/BloodHoundFunction.json) |

[→ View full connector details](../connectors/bloodhoundenterprise.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `BHEAttackPathsData_CL` | [Bloodhound Enterprise](../connectors/bloodhoundenterprise.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                 |
|-------------|--------------------------------|------------------------------------------------------------------------------------|
| 3.2.0       | 15-09-2025                     | Added two extra **Workbooks** (Finding Trends & Posture History). Upgraded **Data Connector** to Azure Function. |
| 3.1.2       | 25-02-2025                     | Bump version for portal deployment                                                 |
| 3.1.1       | 01-02-2025                     | Fixed compilation error in golang **Data Connector** function app. Removed non-working function app installation hint, the workspace name. |
|             | 17-12-2024                     | Updated **Workbooks** - principals now shown properly, percentages calculated correctly, **Data Connector** function app mapping to custom table fixed |
| 3.1.0       | 17-11-2024                     | Updated Solution: table schema updated, new **Workbooks**, new golang **Data Connector** function app uses bloodhound-golang-sdk |
| 3.0.0       | 20-07-2023                     | Initial Solution Release                                                           |

[← Back to Solutions Index](../solutions-index.md)
