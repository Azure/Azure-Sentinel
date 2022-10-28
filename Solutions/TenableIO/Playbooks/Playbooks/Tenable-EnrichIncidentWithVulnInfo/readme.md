# Tenable-EnrichIncidentWithVulnInfo

## Summary

When a new sentinel incident is created, this playbook gets triggered and performs the following actions:

1. Obtains IPs from the incident.
2. Searches asset ids by the IPs.
3. Gets vulnerabilities information.
4. Adds obtained information as a comment to the incident.

<img src="./playbook_screenshot.png" width="50%"/><br>

### Prerequisites

1. Prior to the deployment of this playbook, [TenableIO Data Connector](../../../Data%20Connectors/) should be deployed.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTenableIO%2FPlaybooks%2FPlaybooks%2FTenable-EnrichIncidentWithVulnInfo%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTenableIO%2FPlaybooks%2FPlaybooks%2FTenable-EnrichIncidentWithVulnInfo%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat 1-5 steps for Azure Monitor Logs connection

#### b. Configurations in Sentinel

1. In Microsoft sentinel, analytical rules should be configured to trigger an incident that contains IPs. In the *Entity maping* section of the analytics rule creation workflow, IP should be mapped to **Address** identitfier of the **IP** entity type. Check the [documentation](https://docs.microsoft.com/azure/sentinel/map-data-fields-to-entities) to learn more about mapping entities.
2. Configure the automation rules to trigger the playbook. Check the [documentation](https://docs.microsoft.com/azure/sentinel/tutorial-respond-threats-playbook) to learn more about automation rules.
