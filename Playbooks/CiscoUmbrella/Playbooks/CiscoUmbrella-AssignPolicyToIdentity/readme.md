# CiscoUmbrella-AssignPolicyToIdentity

## Summary

When a new sentinal incident is created, this playbook gets triggered and performs below actions

1. Assigns a new DNS or web policy (*PolicyId* is provided on the playbook deplyment step) to an identity (*originId* of the identity provided in the alert custom entities).
2. Adds comment to incident with information about assigned policies.

<img src="./playbook_screenshot.png" width="50%"/><br>

### Prerequisites

1. Cisco Umbrella Network Device Management Connector needs to be deployed prior to the deployment of this playbook under the same subscription.
2. Obtain Cisco Umbrella API credentials. Refer to Cisco Umbrella Network Device Management Custom Connector documentation.

### Deployment instructions

1. Deploy the playbook by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Playbook Name: Enter the playbook name here
    * PolicyId: ID of the DNS or web policy to act upon

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fcisco_umbrella_playbooks%2FPlaybooks%2FCiscoUmbrellak%2FPlaybooks%2FCiscoUmbrella-AssignPolicyToIdentity%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fcisco_umbrella_playbooks%2FPlaybooks%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrella-AssignPolicyToIdentity%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, you will need to authorize each connection.

1. Click the Azure Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for Cisco Umbrella Network Device Management connector API Connection (For authorizing, the key and the secret need to be provided.)

#### b. Configurations in Sentinel

1. In Azure sentinel analytical rules should be configured to trigger an incident. An incident should have *originId* custom entity. OriginId is Umbrella wide unique identifier for this traffic source (origin), it can be obtained from the corresponding field in Cisco Umbrella logs. Check the [documentation](https://docs.microsoft.com/en-us/azure/sentinel/surface-custom-details-in-alerts) to learn more about adding custom entities to incidents.
2. Configure the automation rules to trigger the playbook.
