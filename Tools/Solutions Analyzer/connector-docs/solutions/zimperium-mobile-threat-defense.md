# Zimperium Mobile Threat Defense

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Zimperium |
| **Support Tier** | Partner |
| **Support Link** | [https://www.zimperium.com/support/](https://www.zimperium.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zimperium%20Mobile%20Threat%20Defense](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zimperium%20Mobile%20Threat%20Defense) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Zimperium Mobile Threat Defense](../connectors/zimperiummtdalerts.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ZimperiumMitigationLog_CL`](../tables/zimperiummitigationlog-cl.md) | [Zimperium Mobile Threat Defense](../connectors/zimperiummtdalerts.md) | - |
| [`ZimperiumThreatLog_CL`](../tables/zimperiumthreatlog-cl.md) | [Zimperium Mobile Threat Defense](../connectors/zimperiummtdalerts.md) | Workbooks |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Workbooks | 1 |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [ZimperiumWorkbooks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Zimperium%20Mobile%20Threat%20Defense/Workbooks/ZimperiumWorkbooks.json) | [`ZimperiumThreatLog_CL`](../tables/zimperiumthreatlog-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
