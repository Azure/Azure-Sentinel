# Cribl

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cribl |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cribl.io/support/](https://www.cribl.io/support/) |
| **Categories** | domains |
| **First Published** | 2024-08-01 |
| **Last Updated** | 2024-09-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cribl](../connectors/cribl.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CriblAccess_CL`](../tables/criblaccess-cl.md) | [Cribl](../connectors/cribl.md) | - |
| [`CriblAudit_CL`](../tables/criblaudit-cl.md) | [Cribl](../connectors/cribl.md) | - |
| [`CriblInternal_CL`](../tables/criblinternal-cl.md) | [Cribl](../connectors/cribl.md) | - |
| [`CriblUIAccess_CL`](../tables/cribluiaccess-cl.md) | [Cribl](../connectors/cribl.md) | - |

## Content Items

This solution includes **4 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 4 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CriblAccess](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl/Parsers/CriblAccess.yaml) | - | - |
| [CriblAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl/Parsers/CriblAudit.yaml) | - | - |
| [CriblInternal](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl/Parsers/CriblInternal.yaml) | - | - |
| [CriblUIAccess](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cribl/Parsers/CriblUIAccess.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYY)** | **Change History**                          |
|-------------|-------------------------------|---------------------------------------------|
| 3.0.1       | 08-08-2025                    | Corrected Query in **Parsers** to display correct columns.                    |
| 3.0.0       | 19-08-2024                    | Initial Solution Release.                    |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
