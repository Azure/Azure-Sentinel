# Block IP in on-premises Exchange Server
Author: Thijs Lecomte

This playbook block a given IP address on an on-premises Exchange Server

This Logic Apps uses an existing Azure Automation account with a Hybrid Worker Group configured.
The Hybrid Worked Group should be configured to run as an account with the necessary Exchange permissions.

The following actions should be taken before this Logic App can be deployed:
- Create Automation Account (https://docs.microsoft.com/azure/automation/automation-quickstart-create-account)
- Register a new hybrid worker that is installed on an Exchange server (https://docs.microsoft.com/azure/automation/automation-windows-hrw-install#automated-deployment)
- Specify a run as account for the Hybrid Runbook Worker Group (https://docs.microsoft.com/azure/automation/automation-hrw-run-runbooks)
    This account should have sufficient permissions on your Exchange server. (Organization Management/Hygiene Management)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-ExchangeIP%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FBlock-ExchangeIP%2Fazuredeploy.json)
