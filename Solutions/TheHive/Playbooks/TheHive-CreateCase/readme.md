# TheHvie-CreateCase

## Summary

When a new sentinel incident is created, this playbook gets triggered and performs the following actions:

1. Create case in TheHive instance with and enrich it with description and title
2. Gets Hosts, IPs entities.
3. Create task and bind it to case.
4. Creates obsarvebles with hosts and IPs for created case. 

<img src="./playbook_screenshot.PNG" width="50%"/><br>

### Prerequisites

1. Prior to the deployment of this playbook, TheHive  API Connector needs to be deployed under the same subscription.
2. Obtain TheHive API credentials. Refer to TheHive API Custom Connector documentation.


### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here
    * Connector Name: Enter the Logic App connector name for TheHive here
    * onPremiseGatewayName: Provide the On-premises data gateway that will be used with The Hive connector. Data gateway should be deployed under the same subscription and resource group as playbook.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTheHive%2FPlaybooks%2FPlaybooks%2FTheHive-CreateCase%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTheHive%2FPlaybooks%2FPlaybooks%2FTheHive-CreateCase%2Fazuredeploy.json)

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
In the *Entity maping* section of the analytics rule creation workflow, suspicious IP and hostnames should be mapped to **Address** identitfier of the **IP** for IPs entity type and **HostName** for the **Host**. Check the [documentation](https://docs.microsoft.com/azure/sentinel/map-data-fields-to-entities) to learn more about mapping entities.
2. Configure the automation rules to trigger the playbook.