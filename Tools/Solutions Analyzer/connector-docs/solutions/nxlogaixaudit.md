# NXLogAixAudit

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | NXLog |
| **Support Tier** | Partner |
| **Support Link** | [https://nxlog.co/support-tickets/add/support-ticket](https://nxlog.co/support-tickets/add/support-ticket) |
| **Categories** | domains |
| **First Published** | 2022-05-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogAixAudit](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogAixAudit) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [NXLog AIX Audit](../connectors/nxlogaixaudit.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AIX_Audit_CL`](../tables/aix-audit-cl.md) | [NXLog AIX Audit](../connectors/nxlogaixaudit.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [NXLog_parsed_AIX_Audit_view](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/NXLogAixAudit/Parsers/NXLog_parsed_AIX_Audit_view.yaml) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
