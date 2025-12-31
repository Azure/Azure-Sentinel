# AWS_IAM

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com](https://support.microsoft.com) |
| **Categories** | domains |
| **First Published** | 2022-09-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **17 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 17 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [AWS - Disable S3 Bucket Public Access](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/Playbooks/AWS-DisableS3BucketPublicAccess/azuredeploy.json) | This playbook disables public access AWS S3 bucket. It is triggered by an incident in Microsoft Sent... | - |
| [AWS IAM - Add tag to user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/Playbooks/AWSIAM-AddTagToUser/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | - |
| [AWS IAM - Delete access keys](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/Playbooks/AWSIAM-DeleteAccessKeys/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | - |
| [AWS IAM - Enrich incident with user info](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/Playbooks/AWSIAM-EnrichIncidentWithUserInfo/azuredeploy.json) | Once a new Microsoft Sentinel incident is created, this playbook gets triggered and performs the fol... | - |
| [AWS_IAM_FunctionAppConnector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/azuredeploy.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/DeleteAccessKey/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/DeleteUserPolicy/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/DetachUserPolicy/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/DisableS3BucketPublicAccess/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/GetUser/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/ListAccessKeys/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/ListAttachedUserPolicies/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/ListGroupsForUser/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/ListUserPolicies/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/TagUser/function.json) | - | - |
| [host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/host.json) | - | - |
| [proxies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS_IAM/Playbooks/AWS_IAM_FunctionAppConnector/proxies.json) | - | - |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
