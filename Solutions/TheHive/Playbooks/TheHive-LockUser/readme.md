# TheHive-LockUser

## Summary

When a new sentinel incident created, this playbook gets triggered and performs the following actions:

1. Parse alerts custom details
2. Locks Users by UserId or UserLogin passed from alert.

<img src="./playbook_screenshot.png" width="50%"/><br>

### Prerequisites

1. Prior to the deployment of this playbook, TheHive API Connector needs to be deployed under the same subscription.
2. Obtain TheHive API credentials. Refer to TheHive API Custom Connector documentation.


### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here
    * Connector Name: Enter the Logic App connector name for TheHive here
    * onPremiseGatewayName: Provide the On-premises data gateway that will be used with The Hive connector. Data gateway should be deployed under the same subscription and resource group as playbook.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTheHive%2FPlaybooks%2FPlaybooks%2FTheHive-LockUser%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTheHive%2FPlaybooks%2FPlaybooks%2FTheHive-LockUser%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Configurations in Sentinel

1. In Microsoft Sentinel, analytical rules should be configured to trigger an incident.
An alert should contain *UserId* or/and *UserLogin* custom entities.
2. Configure the automation rules to trigger the playbook.