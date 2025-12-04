# VaronisSaaS

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Varonis |
| **Support Tier** | Partner |
| **Support Link** | [https://www.varonis.com/resources/support](https://www.varonis.com/resources/support) |
| **Categories** | domains |
| **First Published** | 2023-11-10 |
| **Last Updated** | 2023-11-10 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Varonis SaaS

**Publisher:** Varonis

Varonis SaaS provides the capability to ingest [Varonis Alerts](https://www.varonis.com/products/datalert) into Microsoft Sentinel.



Varonis prioritizes deep data visibility, classification capabilities, and automated remediation for data access. Varonis builds a single prioritized view of risk for your data, so you can proactively and systematically eliminate risk from insider threats and cyberattacks.

**Tables Ingested:**

- `VaronisAlerts_CL`

**Connector Definition Files:**

- [VaronisSaaS_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VaronisSaaS/Data%20Connectors/VaronisSaaS_API_FunctionApp.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `VaronisAlerts_CL` | Varonis SaaS |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n