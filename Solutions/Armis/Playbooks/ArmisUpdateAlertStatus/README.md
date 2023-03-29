# ArmisUpdateAlertStatus

## Summary

This playbook can be used to update the status of an Armis alert from the Microsoft Sentinel platform.

### Prerequisites

1. Store Armis API secret key in Key Vault and obtain keyvault name and tenantId.
    a. Create a Key Vault with unique name
    b. Go to KeyVault -> secrets -> Generate/import and create 'ArmisAPISecretKey' for storing Armis API Secret Key

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here
    * Armis Instance Base URL : Base URL of Armis Instance
    * keyvaultname: Name of keyvault where secrets are stored
    * tenantId: TenantId where keyvault is located

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FArmis%2FPlaybooks%2FArmisUpdateAlertStatus%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FArmis%2FPlaybooks%2FArmisUpdateAlertStatus%2Fazuredeploy.json)

### Post-deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection like Microsoft Sentinel, Key vault.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, analytics rules should be configured to trigger an incident. An incident should have the *alertID* - custom entity that contains alertId of each generated Armis alert and *alertStatus* - custom entity that contains alertStatus of each generated Armis alerts. It can be obtained from the corresponding field in Armis Alerts custom logs. Check the [documentation](https://docs.microsoft.com/azure/sentinel/surface-custom-details-in-alerts) to learn more about adding custom entities to incidents.
2. Configure the automation rules to trigger the playbook.
#### Sample analytics rule query
```
<Armis Alerts Table Name> | where Type == "<Type field of the custom log table>" and status_s == "<Armis Alert Status>" and severity_s != "Low"
