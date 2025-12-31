# JuniperIDP

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2021-03-31 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JuniperIDP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JuniperIDP) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [[Deprecated] Juniper IDP](../connectors/juniperidp.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`JuniperIDP_CL`](../tables/juniperidp-cl.md) | [[Deprecated] Juniper IDP](../connectors/juniperidp.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [JuniperIDP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/JuniperIDP/Parsers/JuniperIDP.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                          |
|-------------|--------------------------------|-------------------------------------------------------------|
| 3.0.1       | 31-12-2024                     | Removed Deprecated **Data connector**                       |
| 3.0.0       | 13-08-2024                     | Deprecating data connector                                  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
