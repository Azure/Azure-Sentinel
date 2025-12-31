# Neustar IP GeoPoint

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-09-30 |
| **Last Updated** | 2022-09-30 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Neustar%20IP%20GeoPoint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Neustar%20IP%20GeoPoint) |

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
| [EnrichIP-GeoInfo-Neustar](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Neustar%20IP%20GeoPoint/Playbooks/Neustar-GetIPGeoInfo/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |
| [NeustarIPGeoPoint_FunctionAppConnector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Neustar%20IP%20GeoPoint/Playbooks/NeustarIPGeoPoint_FunctionAppConnector/azuredeploy.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Neustar%20IP%20GeoPoint/Playbooks/NeustarIPGeoPoint_FunctionAppConnector/GetIPGeoInfo/function.json) | - | - |
| [host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Neustar%20IP%20GeoPoint/Playbooks/NeustarIPGeoPoint_FunctionAppConnector/host.json) | - | - |
| [proxies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Neustar%20IP%20GeoPoint/Playbooks/NeustarIPGeoPoint_FunctionAppConnector/proxies.json) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
