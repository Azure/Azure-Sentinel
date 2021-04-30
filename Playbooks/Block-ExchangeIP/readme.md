This playbook block a given IP address on an on-premises Exchange Server

This Logic Apps uses an existing Azure Automation account with a Hybrid Worker Group configured.
The Hybrid Worked Group should be configured to run as an account with the necessary Exchange permissions.

The following actions should be taken before this Logic App can be deployed:
- Create Automation Account (https://docs.microsoft.com/en-us/azure/automation/automation-quickstart-create-account)
- Register a new hybrid worker that is installed on an Exchange server (https://docs.microsoft.com/en-us/azure/automation/automation-windows-hrw-install#automated-deployment)
- Specify a run as account for the Hybrid Runbook Worker Group (https://docs.microsoft.com/en-us/azure/automation/automation-hrw-run-runbooks)
    This account should have sufficient permissions on your Exchange server. (Organization Management/Hygiene Management)