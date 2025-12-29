# VaronisSaaS

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Varonis |
| **Support Tier** | Partner |
| **Support Link** | [https://www.varonis.com/resources/support](https://www.varonis.com/resources/support) |
| **Categories** | domains |
| **First Published** | 2023-11-10 |
| **Last Updated** | 2023-11-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Varonis SaaS](../connectors/varonissaas.md)

**Publisher:** Varonis

Varonis SaaS provides the capability to ingest [Varonis Alerts](https://www.varonis.com/products/datalert) into Microsoft Sentinel.



Varonis prioritizes deep data visibility, classification capabilities, and automated remediation for data access. Varonis builds a single prioritized view of risk for your data, so you can proactively and systematically eliminate risk from insider threats and cyberattacks.

| Attribute | Value |
|:-------------------------|:---|
| **Tables Ingested** | `VaronisAlerts_CL` |
| **Connector Definition Files** | [VaronisSaaS_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS/Data%20Connectors/VaronisSaaS_API_FunctionApp.json) |

[→ View full connector details](../connectors/varonissaas.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `VaronisAlerts_CL` | [Varonis SaaS](../connectors/varonissaas.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.3       | 25-11-2025                     | Add Informational severity level support    |
| 3.0.2       | 12-09-2025                     | Save last alert ingest time                 |
| 3.0.1       | 02-12-2025                     | Bug fixes                                   |
| 3.0.0       | 02-07-2024                     | Refactor azure function                     |

[← Back to Solutions Index](../solutions-index.md)
