# Eset Security Management Center

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Eset |
| **Support Tier** | Partner |
| **Support Link** | [https://support.eset.com/en](https://support.eset.com/en) |
| **Categories** | domains |
| **First Published** | 2022-05-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Eset%20Security%20Management%20Center](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Eset%20Security%20Management%20Center) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Eset Security Management Center](../connectors/esetsmc.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`eset_CL`](../tables/eset-cl.md) | [Eset Security Management Center](../connectors/esetsmc.md) | Analytics, Workbooks |

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 2 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Threats detected by Eset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Eset%20Security%20Management%20Center/Analytic%20Rules/eset-threats.yaml) | Low | Execution, CredentialAccess, PrivilegeEscalation | [`eset_CL`](../tables/eset-cl.md) |
| [Web sites blocked by Eset](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Eset%20Security%20Management%20Center/Analytic%20Rules/eset-sites-blocked.yaml) | Low | Exfiltration, CommandAndControl, InitialAccess | [`eset_CL`](../tables/eset-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [esetSMCWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Eset%20Security%20Management%20Center/Workbooks/esetSMCWorkbook.json) | [`eset_CL`](../tables/eset-cl.md) |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
