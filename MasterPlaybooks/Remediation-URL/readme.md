# Master Playbook Block URL Remediation 

Master playbook is integrated with multiple firewall end products like Zscaler ,Forcepoint ,Fortinet-Fortigate, Cisco Meraki and PaloAlto-PAN-OS.

Firewall end products are deployed as child/nested playbooks.

If a malicious URL is detected from the Azure sentinel, master playbook calls all the child/nested playbooks and each firewall product will take remidiation steps needed on that URL and comments will be passed on the master playbook from the child/nested playbooks involving multiple products. 

## Summary
 When a new Azure Sentinel incident is created, this playbook gets triggered and performs the below actions:
 1. Fetches a list of potentially malicious URLs.
 2. Each nested playbook receives the list of URLs and performs respective defined automated actions on it.
 3. Response from individual playbooks are returned to master playbook for incident comment. 

![Master](./Images/PlaybookDesignerLight.png)


 ## Pre-requisites for deployment
At least one of the below mentioned nested playbooks must be deployed prior to deployment of this playbook under same subscription and same resource group and the same location/region. Capture the name of all the deployed playbooks during deployment.

- [Cisco-Meraki-Remediation-URL](./Cisco-Meraki-Remediation-URL/azuredeploy.json) is a nested playbook that handles remidiation for Cisco Meraki.
- [Forcepoint-Remediation-URL](./Forcepoint-Remediation-URL/azuredeploy.json) is a nested playbook that handles remidiation for Forcepoint.
- [Fortinet-FortiGate-Remediation-URL](./Fortinet-FortiGate-Remediation-URL/azuredeploy.json) is a nested playbook that handles remidiation for Fortinet FortiGate.
- [PaloAlto-PAN-OS-Remediation-URL](./PaloAlto-PAN-OS-Remediation-URL/azuredeploy.json) is a nested playbook that handles remidiation for PaloAlto PAN OS.
- [Zscaler-Remediation-URL](./Zscaler-Remediation-URL/azuredeploy.json) is a nested playbook that handles remidiation for Zscaler.


If any one of the above mentioned playbooks are not deployed then default playbook will deploy in its place.

## Nested Playbook Structure

### Input Schema

Each of the nested playbooks of IP Remediation accepts following inputs:
- URLs: List of URLs as entities from azure sentinel incident.
- Workflow: Worklfow is identifier for the nested playbook which points to which subscription and which resource group the nested playbook belongs to.
- Trigger: Tells how the playbook is invoked/triggered.
- Headers: Tells the content type of entity accepting by nested playbook.

The image below shows example of input schema for Zscaler nested playbook.

![Master](./Images/InputSchema.PNG)

### Output Schema

Each of the nested playbooks of URL Remediation gives following outputs:

- Status code: Status code tells the success or failure status of nested playbook run results. The status code value is displayed in incident comment.
- Body: Body provides with all the output values that nested playbook returns. It varies according to the nested playbook. 
- Incident Comment: It contains output body from nested playbook in tabular format. 


## Add new playbook to master playbook

To add new nested playbook to master playbook:
- Hover below action "Initialize variable playbook status Codes".
- Click on symbol '+' for insert a new step and choose add a parallel branch.
- First action is to add scope. Within scope add new action and choose the nested playbook to add.
- Compose Incident Comment.
- Append the status code from nested playbook to Status Codes variable .

![Master](./Images/AddNestedPlaybook.PNG)


 ## Deployment Instructions
 1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FMasterPlaybooks%2FRemediation-URL%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FMasterPlaybooks%2FRemediation-URL%2Fazuredeploy.json)


 2. Fill in the required parameters for deploying the playbook.

 | Parameter  | Description |
| ------------- | ------------- |
| **Master Playbook Name** | Enter the master playbook name here without spaces. |
| **Zscaler Playbook Name**|Enter the name of Zscaler Nested playbook without spaces. |
| **Forcepoint Playbook Name** | Enter the name of Forcepoint Nested playbook without spaces. |
| **Fortinet Playbook Name**| Enter the name of Fortinet Nested playbook without spaces. | 
| **Cisco Meraki Playbook Name**|Enter the name of Meraki Nested playbook without spaces.|
| **Palo Alto PAN-OS Playbook Name**|Enter the name of PaloAlto PAN OS Nested playbook without spaces.|


# Post-Deployment Instructions

### Configurations in Sentinel
- In Azure sentinel analytical rules should be configured to trigger an incident with URLs. 
- Configure the automation rules to trigger the playbook which calls multiple nested playbooks.

# Playbook steps explained
## When Azure Sentinel incident creation rule is triggered
Captures potentially malicious or malware URLs incident information.

##Entities - Get URLs
Get the list of URLs as entities from the Incident.

## For malicious URLs received from the incident
 1. The list of URLs is passed as Entity to each of the nested playbook.
 2. Each nested playbook accepts URLs list as entity from master playbook and respectively performs defined automated actions(Block/Unblock URL) for each URL.
 3. The response from each of the nested playbook is returned to master playbook.
 4. Response from each nested playbook is attached to incident comment and consolidated incident comment is created.
 5. If all the nested playbooks returns success response , the incident will be closed.
