# Master Playbook Block IP Remediation 

Master playbook is integrated with multiple firewall end products like AzureFirewall ,Forcepoint ,Fortinet-Fortigate, Cisco Meraki and PaloAlto-PAN-OS.

Firewall end products are deployed as child/nested playbooks.

If a malicious IP is detected from the Azure sentinel, master playbook calls all the child/nested playbooks and each firewall product will take remidiation steps needed on that Ip Address and comments will be passed on the master playbook from the child/nested playbooks involving multiple products. 

## Summary
 When a new Azure Sentinel incident is created, this playbook gets triggered and performs the below actions:
 1. Fetches a list of potentially malicious IP addresses.
 2. Each nested playbook receives the list of IP addresses and performs respective defined automated actions on it.
 3. Response from individual playbooks are returned to master playbook for incident comment. 

![Master](./Images/PlaybookDesignerLight.png)

![Master](./Images/PlaybookDesignerDark.png)


 ## Pre-requisites for deployment
At least one of the below-mentioned nested playbooks must be deployed prior to deployment of this playbook under same subscription and same resource group and the same location/region. Capture the name of all the deployed playbooks during deployment.

- [AzureFirewall-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/AzureFirewall-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for AzureFirewall.  
- [Forcepoint-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/ForcepointNGFW-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for Forcepoint. 
- [Fortinet-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/Fortinet-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for Fortinet. 
- [Meraki-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/Meraki-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for Meraki. 
- [PaloAlto-PAN-OS-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/PaloAlto-PAN-OS-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for PaloAlto.

- [CiscoASA-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/CiscoASA-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for PaloAlto.
- [CiscoFirepower-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/CiscoFirepower-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for PaloAlto.
- [CiscoUmbrella-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/CiscoUmbrella-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for PaloAlto.
- [F5-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/F5-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for PaloAlto.
- [MDE-BlockIP-Nested-Remediation](/MasterPlaybook-IP-Remediation/MDE-BlockIP-Nested-Remediation/azuredeploy.json) is a nested playbook that handles remidiation for PaloAlto.

If any one of the above-mentioned playbooks are not deployed then default playbook will deploy in its place.

## Nested Playbook Structure

### Input Schema

Each of the nested playbooks of IP Remediation accepts following inputs:
- IPs: List of IPs as entities from azure sentinel incident.
- Workflow: Worklfow is identifier for the nested playbook which points to which subscription and which resource group the nested playbook belongs to.
- Trigger: Tells how the playbook is invoked/triggered.
- Headers: Tells the content type of entity accepting by nested playbook.

The image below shows example of input schema for CiscoMeraki nested playbook.

![Master](./Images/InputSchema.PNG)

### Output Schema

Each of the nested playbooks of IP Remediation gives following outputs:

- Status code: Status code tells the success or failure status of nested playbook run results. The status code value is displayed in incident comment.
- Body: Body provides with all the output values that nested playbook returns. It varies according to the nested playbook. 
- Incident Comment: It contains output body from nested playbook in tabular format. 

For example, taking reference of CiscoMeraki incident comment image below, CiscoMeraki logo is composed for incident comment.
Also, table is populated with values such as Incident IP address, Source, Source Port, Destination, Destination Port, Policy, Protocol, Previous status, Current status and Action.

![Master](./Images/IncidentComment.png)


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

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fmaster%2FMasterPlaybooks%2FRemediation-IP%2Fazuredeploy.json)
[![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fmaster%2FMasterPlaybooks%2FRemediation-IP%2Fazuredeploy.json)


 2. Fill in the required parameters for deploying the playbook.

 | Parameter                          | Description                                                       |
|------------------------------------|-------------------------------------------------------------------|
| **Playbook Name**                  | Enter the master playbook name here without spaces.               |
| **Azure Firewall Playbook Name**   | Enter the name of Azure Firewall Nested playbook without spaces.  |
| **Forcepoint Playbook Name**       | Enter the name of Forcepoint Nested playbook without spaces.      |
| **Fortinet Playbook Name**         | Enter the name of Fortinet Nested playbook without spaces.        |
| **Cisco Meraki Playbook Name**     | Enter the name of Meraki Nested playbook without spaces.          |
| **Palo Alto PAN-OS Playbook Name** | Enter the name of PaloAlto PAN OS Nested playbook without spaces. |
| **CiscoASA Playbook Name**         | Enter the name of CiscoASA Nested playbook without spaces.        |
| **CiscoFirepower Playbook Name**   | Enter the name of CiscoFirepower Nested playbook without spaces.  |
| **CiscoUmbrella Playbook Name**    | Enter the name of CiscoUmbrella Nested playbook without spaces.   |
| **F5Big-IP Playbook Name**         | Enter the name of F5Big-IP Nested playbook without spaces.        |
| **MDE Playbook Name**       | Enter the name of MDE Nested playbook without spaces.             |



# Post-Deployment Instructions

### Configurations in Sentinel
- In Azure sentinel analytical rules should be configured to trigger an incident with IP addresses. 
- Configure the automation rules to trigger the playbook which calls multiple nested playbooks.

# Playbook steps explained
## When Azure Sentinel incident creation rule is triggered
Captures potentially malicious or malware IP addresses incident information.

##Entities - Get IPs
Get the list of IPs as entities from the Incident.

## For malicious IP addresses received from the incident
 1. The list of IP address is passed as Entity to each of the nested playbook.
 2. Each nested playbook accepts IP list as entity from master playbook and respectively performs defined automated actions(Block/Unblock IP) for each IP address.
 3. The response from each of the nested playbook is returned to master playbook.
 4. Response from each nested playbook is attached to incident comment and consolidated incident comment is created.
 5. If all the nested playbooks returns success response , the incident will be closed.

**Incident Comment**

 ![Master](./Images/IncidentCommentLight.png)
  ![Master](./Images/IncidentCommentDark.png)

  **Incident Comment for error handling**

 ![Master](./Images/IncidentCommentLight1.png)
  ![Master](./Images/IncidentCommentDark1.png)