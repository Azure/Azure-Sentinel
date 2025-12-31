# AWS Systems Manager

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **23 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 23 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [AWS Systems Manager - Get Missing Patches for EC2 Instances](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/AWSSystemsManagerPlaybooks/AWS-SSM-GetInstancePatches/azuredeploy.json) | When an incident is created in Microsoft Sentinel, this playbook gets triggered and perform the foll... | - |
| [AWS Systems Manager - Get Missing Patches for EC2 Instances for given Hostname](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/AWSSystemsManagerPlaybooks/AWS-SSM-GetInstancePatches-HostEntityTrigger/azuredeploy.json) | The playbook can be triggered manually from a Host Entity to get the missing patches on a managed EC... | - |
| [AWS Systems Manager - Get Missing Patches for EC2 Instances for given Private IP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/AWSSystemsManagerPlaybooks/AWS-SSM-GetInstancePatches-IPEntityTrigger/azuredeploy.json) | The playbook can be triggered manually from an IP Entity to get the missing patches on a managed EC2... | - |
| [AWS Systems Manager - Run Automation Runbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/AWSSystemsManagerPlaybooks/AWS-SSM-RunAutomationRunbook/azuredeploy.json) | When a new sentinel incident is created, this playbook gets triggered and runs the specified AWS Sys... | - |
| [AWS Systems Manager - Stop Managed EC2 Instances](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/AWSSystemsManagerPlaybooks/AWS-SSM-StopManagedInstance/azuredeploy.json) | This playbook can be used by SOC Analysts to stop malicious or compromised EC2 instances in AWS. Thi... | - |
| [AWS Systems Manager - Stop Managed EC2 Instances Host Entity Trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/AWSSystemsManagerPlaybooks/AWS-SSM-StopManagedInstance-HostEntityTrigger/azuredeploy.json) | This playbook can be used by SOC Analysts to stop malicious or compromised EC2 instances in AWS. The... | - |
| [AWS Systems Manager - Stop Managed EC2 Instances IP Entity Trigger](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/AWSSystemsManagerPlaybooks/AWS-SSM-StopManagedInstance-IPEntityTrigger/azuredeploy.json) | This playbook can be used by SOC Analysts to stop malicious or compromised EC2 instances in AWS. The... | - |
| [AWS_SSM_FunctionAppConnector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/azuredeploy.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/AddTagsToResource/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/CreateDocument/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/DeleteDocument/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/DescribeDocument/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/DescribeInstanceInformation/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/DescribeInstancePatches/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/GetAutomationExecution/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/GetDocument/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/GetInventory/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/ListDocuments/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/ListTagsForResource/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/RemoveTagFromResource/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/StartAutomationExecution/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/StopAutomationExecution/function.json) | - | - |
| [host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AWS%20Systems%20Manager/Playbooks/CustomConnector/AWS_SSM_FunctionAppConnector/host.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.1       | 29-01-2024                     | App insights to LA change in data connector and repackage                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
