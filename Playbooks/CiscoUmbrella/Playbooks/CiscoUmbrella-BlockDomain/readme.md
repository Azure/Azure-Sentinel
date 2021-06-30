# CiscoUmbrella-BlockDomain

## Summary

When a new sentinal incident is created, this playbook gets triggered and performs below actions

1. Obtains domains from URL entities in the incident.
2. Optionally adds these domains to a customer's domain lists using [Cisco Umbrella Enforcement API](https://developer.cisco.com/docs/cloud-security/#!enforcement-overview/overview).
3. Adds comment to incident with information about posted domains.

<img src="./playbook_screenshot.png" width="50%"/><br>

### Prerequisites

1. Cisco Umbrella Enforcement Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Obtain Cisco Umbrella API credentials. Refer to Cisco Umbrella Enforcement Custom Connector documentation.

### Deployment instructions

1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fcisco_umbrella_playbooks%2FPlaybooks%2FCiscoUmbrellak%2FPlaybooks%2FCiscoUmbrella-BlockDomain%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fcisco_umbrella_playbooks%2FPlaybooks%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrella-BlockDomain%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, you will need to authorize each connection.

1. Click the Azure Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for Cisco Umbrella Enforcement connector API Connection (For authorizing, the key and the secret need to be provided.)

#### b. Configurations in Sentinel

1. In Azure sentinel analytical rules should be configured to trigger an incident with malware URL. In the *Entity maping* section of the analytics rule creation workflow, user's email should be mapped to **Url** identitfier of the **URL** entity type. Check the [documentation](https://docs.microsoft.com/en-us/azure/sentinel/map-data-fields-to-entities) to learn more about mapping entities.
2. Configure the automation rules to trigger the playbook.
