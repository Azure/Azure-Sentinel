# CiscoUmbrella-AddIpToDestinationList

## Summary

When a new sentinel incident is created, this playbook gets triggered and performs the following actions:

<img src="./Images/playbook_screenshot.png" width="28%"/><br>

1. Sends an adaptive card to the Teams channel where the analyst can choose an action to be taken.

<img src="./Images/teams_screenshot.png" width="50%"/><br>

2. Adds an IP to the destination list chosen in the adaptive card.
3. Changes incident status and severity depending on the action chosen in the adaptive card.
4. Adds comment to the incident with information about the actions taken.

<img src="./Images/commentOnIncident.png" width="50%"/><br>

### Prerequisites

1. Login to Cisco Cloud Security dashboard and navigating to Admin-->API Keys. Create New API Key if not already created and select the appropriate "Key Scope" with Read/Write permission. Store "Api Key" and "Key Secret" to a safe place. This "Api Key" is a "Client Id" and "Key Secret" is a "Secret" used for this Playbook.
2. Store the "Api Key" and "Key Secret" from previous step to Key vault Secrets.
3. To send notification to Microsoft Teams, Teams group id and channel id is needed at the time of playbook creation.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here
    * Teams Group Id: Id of the Teams Group where the adaptive card will be posted
    * Teams Channel Id: Id of the Teams Channel where the adaptive card will be posted
    * Keyvault name: Name of the key vault where secrets are stored.
    * Cloud Security API Client Id Key Name: Name of the Secrets field from Keyvault where Cisco Cloud Security "API Key" value is stored.
    * Cloud Security API Secret Key Name: Name of the Secrets field from Keyvault where Cisco Cloud Security "Key Secret" value is stored.
    * Host End Point: Default is "api.umbrella.com" and is used for any API call to Cisco Cloud Security REST API's.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooksk%2FCiscoUmbrellaPlaybooks%2FCiscoUmbrella-AddIpToDestinationList%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrellaPlaybooks%2FCiscoUmbrella-AddIpToDestinationList%2Fazuredeploy.json)

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

1. In Microsoft sentinel, analytical rules should be configured to trigger an incident with a malicious IP. In the *Entity mapping* section of the analytics rule creation workflow, malicious IP should be mapped to **Address** identifier of the **IP** entity type. Check the [documentation](https://docs.microsoft.com/azure/sentinel/map-data-fields-to-entities) to learn more about mapping entities.
2. Configure the automation rules to trigger the playbook.

#### c. Assign Playbook Microsoft Sentinel Responder Role
1. Select the Playbook (Logic App) resource
2. Click on Identity Blade
3. Choose System assigned tab
4. Click on Azure role assignments
5. Click on Add role assignments
6. Select Scope - Resource group
7. Select Subscription - where Playbook has been created
8. Select Resource group - where Playbook has been created
9. Select Role - Microsoft Sentinel Responder
10. Click Save (It takes 3-5 minutes to show the added role.)

#### d. Assign access policy on key vault for Playbook to fetch the secret key
1. Select the Key vault resource where you have stored the secret
2. Click on Access policies Blade
3. Click on Create
4. Under Secret permissions column , Select Get , List from "Secret Management Operations"
5. Click next to go to Principal tab and choose your deployed playbook name
6. Click Next leave application tab as it is .
7. Click Review and create
8. Click Create

#  References
 - [Cisco Cloud Security API Documentation](https://developer.cisco.com/docs/cloud-security/authentication/#authentication)
 - [Rest API Request And Response Sample](https://developer.cisco.com/docs/cloud-security/destination-lists/#destination-lists)