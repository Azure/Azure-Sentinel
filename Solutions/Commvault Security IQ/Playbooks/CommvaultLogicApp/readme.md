# Commvault Logic App Playbook
## Summary
This Logic App executes when called upon by an Automation Rule. Accessing the KeyVault to retrieve various credentials, it executes a specific runbook depending on the use case. 

## Prerequisites
- Administrative access to your Commvault/Metallic environment.
- Administrative access to your Azure Resource Group and Subscription.
- An Azure Sentinel instance in the aforementioned Azure Resource Group.
- A Keyvault and an Automation Account configured as mentioned in the documentation here :- (https://github.com/Cv-securityIQ/Azure-Integration/blob/Commvault/Solutions/Commvault%20Security%20IQ/README.md)

## Deployment Instructions
Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2Commvault%20Security%20IQ%2FPlaybooks%2CommvaultLogicApp%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2Commvault%20Security%20IQ%2FPlaybooks%2CommvaultLogicApp%2Fazuredeploy.json)

Alternatively:-
1. To import the logic app from the azure portal go to "Custom Deployment"
2. "Build your own template in the editor"
3. "Load File" -> Use the json present under **Playbooks/CommvaultLogicApp/azuredeploy.json**.
4. Enter in the required parameters

## Post-deployment Instructions
Steps to follow the instructions are mentioned here :- (https://github.com/Cv-securityIQ/Azure-Integration/blob/Commvault/Solutions/Commvault%20Security%20IQ/README.md)
1. Give the required permissions to the logic app to get the secrets from the keyvault.
2. Setup the Managed Identity
