# AWSAthena

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-11-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **9 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 9 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [AWS Athena - Execute Query and Get Results](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena/Playbooks/AWSAthenaPlaybooks/AWSAthena-GetQueryResults/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and performs the following act... | - |
| [AWSAthena_FunctionAppConnector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena/Playbooks/CustomConnector/AWSAthena_FunctionAppConnector/azuredeploy.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena/Playbooks/CustomConnector/AWSAthena_FunctionAppConnector/GetQueryExecution/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena/Playbooks/CustomConnector/AWSAthena_FunctionAppConnector/GetQueryResults/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena/Playbooks/CustomConnector/AWSAthena_FunctionAppConnector/ListDatabases/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena/Playbooks/CustomConnector/AWSAthena_FunctionAppConnector/ListDataCatalogs/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena/Playbooks/CustomConnector/AWSAthena_FunctionAppConnector/ListQueryExecutions/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena/Playbooks/CustomConnector/AWSAthena_FunctionAppConnector/StartQueryExecution/function.json) | - | - |
| [host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWSAthena/Playbooks/CustomConnector/AWSAthena_FunctionAppConnector/host.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.1       | 09-08-2024                     | Updated **Playbook** post deployement steps			                   | 
| 3.0.0       | 29-01-2024                     | App insights to LA change in data connector and repackage                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
