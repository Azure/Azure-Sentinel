# Servicenow

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-09-19 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Servicenow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Servicenow) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **3 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 3 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Create And Update ServiceNow Record](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Servicenow/Playbooks/ServiceNow-CreateAndUpdateIncident/azuredeploy.json) | This playbook will create or update incident in ServiceNow. When incident is created, playbook will ... | - |
| [Create ServiceNow record - Alert trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Servicenow/Playbooks/Create-ServiceNow-record/alert-trigger/azuredeploy.json) | This playbook will open a Service Now incident when a new incident is opened in Microsoft Sentinel. | - |
| [Create ServiceNow record - Incident trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Servicenow/Playbooks/Create-ServiceNow-record/incident-trigger/azuredeploy.json) | This playbook will open a Service Now incident when a new incident is opened in Microsoft Sentinel. | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
