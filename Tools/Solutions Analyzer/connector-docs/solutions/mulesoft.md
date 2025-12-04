# Mulesoft

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-07-12 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mulesoft](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mulesoft) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### MuleSoft Cloudhub

**Publisher:** MuleSoft

The [MuleSoft Cloudhub](https://www.mulesoft.com/platform/saas/cloudhub-ipaas-cloud-based-integration) data connector provides the capability to retrieve logs from Cloudhub applications using the Cloudhub API and more events into Microsoft Sentinel through the REST API. The connector provides ability to get events which helps to examine potential security risks, analyze your team's use of collaboration, diagnose configuration problems and more.

**Tables Ingested:**

- `MuleSoft_Cloudhub_CL`

**Connector Definition Files:**

- [MuleSoft_Cloudhub_API_FunctionApp.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Mulesoft/Data%20Connectors/MuleSoft_Cloudhub_API_FunctionApp.json)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `MuleSoft_Cloudhub_CL` | MuleSoft Cloudhub |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n