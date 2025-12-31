# Entrust identity as Service

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2023-05-22 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Entrust%20identity%20as%20Service](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Entrust%20identity%20as%20Service) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **5 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 5 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Block Risky/Compromised User From Entrust](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Entrust%20identity%20as%20Service/Playbooks/EntrustPlaybooks/Entrust-BlockUser/azuredeploy.json) | This playbook Block the risky user and update the status in comments section of triggered incident s... | - |
| [Fetch IP Details From Entrust](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Entrust%20identity%20as%20Service/Playbooks/EntrustPlaybooks/Entrust-EnrichIncidentWithIPDetails/azuredeploy.json) | This playbook provides the IP details in comments section of triggered incident so that SOC analysts... | - |
| [Fetch IP Details From Entrust - Entity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Entrust%20identity%20as%20Service/Playbooks/EntrustPlaybooks/Entrust-EnrichIP-EntityTrigger/azuredeploy.json) | This playbook provides the IP details of user authentication and management activity in comments sec... | - |
| [Fetch User Details From Entrust](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Entrust%20identity%20as%20Service/Playbooks/EntrustPlaybooks/Entrust-EnrichIncidentWithUserDetails/azuredeploy.json) | This playbook provides the user essential details in comments section of triggered incident so that ... | - |
| [Fetch User Details From Entrust - Entity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Entrust%20identity%20as%20Service/Playbooks/EntrustPlaybooks/Entrust-EnrichUser-EntityTrigger/azuredeploy.json) | This playbook provides the user essential details in comments section of incident so that SOC analys... | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
