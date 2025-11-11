# Zscaler Block URL Nested Remediation Playbook



## Summary
 When this playbook gets triggered and it performs the below actions:
 1. Gets a list of potentially malicious URLs.
 2. For each URL in the list, adds it to the predefined category.


 ## Pre-requisites for deployment
1. Playbook leverages the Zscaler API. To use the Zscaler capabilities, you need a Zscaler API key. Refer this link: [API Developers Guide: Getting Started](https://help.zscaler.com/zia/api-getting-started)
3. Deploy the [Zscaler Authentication playbook](./Authentication/) before the deployment of this playbook under the same subscription and same resource group. Capture the name of the Authentication playbook during deployment.

### Deploy Authentication Playbook

To deploy Cisco Meraki Custom connector click on the below button.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZscaler%2FAuthentication%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FZscaler%2FAuthentication%2Fazuredeploy.json)

 ## Deployment Instructions
 1. Deploy the playbook by clicking on the "Deploy to Azure" button. This will take you to deploy an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FMasterPlaybooks%2FRemediation-URL%2FZscaler-Remediation-URL%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Ftree%2Fmaster%2FMasterPlaybooks%2FRemediation-URL%2FZscaler-Remediation-URL%2Fazuredeploy.json)


 2. Fill in the required parameters for deploying the playbook.

 | Parameter  | Description |
| ------------- | ------------- |
| **Playbook Name** | Enter the playbook name without spaces |
| **Zscaler Authentation Playbook**|Enter the name of Zscaler Authentation Playbook without spaces |
| **Zscaler Admin Url** | Enter Zscaler Admin Url |
| **Block Category**| Zscaler block category | 
