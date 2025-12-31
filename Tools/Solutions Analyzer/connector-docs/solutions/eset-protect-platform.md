# ESET Protect Platform

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | ESET Enterprise Integrations |
| **Support Tier** | Partner |
| **Support Link** | [https://help.eset.com/eset_connect/en-US/integrations.html](https://help.eset.com/eset_connect/en-US/integrations.html) |
| **Categories** | domains |
| **First Published** | 2024-10-29 |
| **Last Updated** | 2025-06-17 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [ESET Protect Platform](../connectors/esetprotectplatform.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`IntegrationTableIncidents_CL`](../tables/integrationtableincidents-cl.md) | [ESET Protect Platform](../connectors/esetprotectplatform.md) | - |
| [`IntegrationTable_CL`](../tables/integrationtable-cl.md) | [ESET Protect Platform](../connectors/esetprotectplatform.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ESETProtectPlatform](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ESET%20Protect%20Platform/Parsers/ESETProtectPlatform.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                         |
|-------------|--------------------------------|----------------------------------------------------------------------------|
| 3.1.1       | 25-04-2025                     | Add the location parameter to ARM template and update the email address.   |
| 3.1.0       | 06-02-2025                     | Updated **Data Connector** FunctionApp code to work with old param and new |
| 3.0.0       | 04-11-2024                     | Initial Solution Release                                                   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
