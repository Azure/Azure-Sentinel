# VendorProduct-playbookname

## Summary

When a new sentinel incident is created, this playbook gets triggered and performs the following actions:

1. 1.
2. 2.

<img src="./playbook_screenshot.png" width="50%"/><br>

### Prerequisites

1. Prior to the deployment of this playbook, Vendor Product API Connector needs to be deployed under the same subscription.
2. Obtain Vendor Product API credentials. Refer to Vendor Product API Custom Connector documentation.
3. 3.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here
    * params name: param descr

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fbase-playbooks-solution%2FSolutions%2FBasePlaybooksSolution%2FPlaybooks%2FPlaybooks%2FVendorProduct-playbookname%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fbase-playbooks-solution%2FSolutions%2FBasePlaybooksSolution%2FPlaybooks%2FPlaybooks%2FVendorProduct-playbookname%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Azure Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Configurations in Sentinel

1. In Azure sentinel, analytical rules should be configured to trigger an incident with a malicious IP. In the *Entity maping* section of the analytics rule creation workflow, malicious IP should be mapped to **Address** identitfier of the **IP** entity type. Check the [documentation](https://docs.microsoft.com/azure/sentinel/map-data-fields-to-entities) to learn more about mapping entities.
2. Configure the automation rules to trigger the playbook.