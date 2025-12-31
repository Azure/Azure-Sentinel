# Aruba ClearPass

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-23 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Aruba%20ClearPass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Aruba%20ClearPass) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [[Deprecated] Aruba ClearPass via Legacy Agent](../connectors/arubaclearpass.md)
- [[Deprecated] Aruba ClearPass via AMA](../connectors/arubaclearpassama.md)

## Tables Reference

This solution uses **1 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CommonSecurityLog`](../tables/commonsecuritylog.md) | [[Deprecated] Aruba ClearPass via AMA](../connectors/arubaclearpassama.md), [[Deprecated] Aruba ClearPass via Legacy Agent](../connectors/arubaclearpass.md) | - |

## Content Items

This solution includes **1 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 1 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ArubaClearPass](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Aruba%20ClearPass/Parsers/ArubaClearPass.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       |   13-11-2024                   |    Removed Deprecated **Data Connectors**                          |
| 3.0.2       |   08-07-2024                   |	Deprecating **Data Connector**          						|
| 3.0.1       |   26-09-2023                   |	Parser link update          						            |
| 3.0.0       |   21-09-2023                   |	Addition of new Aruba ClearPass AMA **Data Connector**          |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
