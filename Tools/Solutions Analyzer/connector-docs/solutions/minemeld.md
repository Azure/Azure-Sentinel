# Minemeld

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-10-11 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Minemeld](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Minemeld) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **2 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 2 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Create Indicator - Minemeld](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Minemeld/Playbooks/MinemeldPlaybooks/Minemeld-CreateIndicator/azuredeploy.json) | This playbook search for indicators in Minemeld related to the entities(IP, filehash, URL) gathered ... | - |
| [Entity (IP, URL, FileHash) Enrichment - Minemeld](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Minemeld/Playbooks/MinemeldPlaybooks/Minemeld-EnrichIncident/azuredeploy.json) | This playbook search for indicators in Minemeld related to the entities(IP, filehash, URL) gathered ... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.0       | 03-04-2024					   | Added RleaseNotes file for Minemeld solution		   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
