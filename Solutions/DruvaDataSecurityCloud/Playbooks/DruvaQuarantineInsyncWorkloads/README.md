# Druva Quarantine Insync Workload Resource

## Summary

This playbook uses Druva-Ransomware-Response capabilities to stop the spread of ransomware and avoid reinfection or contamination spread to your environment.

### Prerequisites

1. Verify ARR (Accelerated Ransomware Recovery) should be enabled for the respective Device using Resource ID on the [Druva Security Cloud Platform](https://console.druva.com/).
2. Generate Druva API Client Credentials
    * Use the following link to navigate to Druva's documentation page and refer the steps to generate API Client Credentials.
    * [Druva's Documentation Page](https://help.druva.com/en/articles/8580838-create-and-manage-api-credentials)
    * Copy/Paste or Store the creds for future use.
3. Store Service account credentials in Key Vault Secrets and obtain keyvault name.
    * Create a Key Vault with name as Druva-ClientCredential
    * Go to KeyVault -> secrets -> Generate/import and create 'Druva-ClientID' & 'Druva-ClientSecret' for storing client_id and client_secret respectively.
    * Store the secrets obtained for your organization and user from Druva Console UI in the previous step.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * PlaybookName: Name by which you want to deploy the playbook.
    * keyvaultName: Name of keyvault where secrets are stored.
3. Validate the deployment:
    * Check if the resources (e.g., Key Vault, API connections, Logic Apps) are created successfully.
    * Verify the deployment logs for any errors.
4. Authorize connections:
    * Follow the steps in the 'postDeployment' section to authorize connections.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDruvaDataSecurityCloud%2FPlaybooks%2FDruvaQuarantineInsyncWorkload%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDruvaDataSecurityCloud%2FPlaybooks%2FDruvaQuarantineInsyncWorkload%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection keyvault.

1. Login to the Microsoft Azure portal and in the search box type API Connections.
2. Find API connection option.
3. Check for your created API connection exists. eg. <playbookname>-KeyVault-Connection
4. Check Status should be ready for the same API Connection.

#### b. Grant permissions

Make sure that this playbook and your user has the IAM role permission granted as 'Key Vault Secrets User'

### Execute the playbook:

1. Trigger the playbook manually by using the dropdown option as 'run_with_payload'.
2. On triggering a side screen will appear in which there will be a section named as 'Body'.
3. Inside body paste the json obtained from the below with respective edited values according to your resources.
    ```json
    {
        "username" : "<username_in_which_devices_are_registered_to_quarantine>",
        "fromDate" : "<2024-12-01>",
        "toDate" : "<2024-12-18>"
    }
4. Hit the 'run' button at the bottom.
5. Navigate to the playbook home page and check the run history if the run was successful or not.
