# CiscoUmbrella-GetDomainInfo

## Summary

When a new sentinel incident is created, this playbook gets triggered and performs the following actions

<img src="./Images/playbook_screenshot_new.png" width="30%"/><br>

1. Get domains from URL entities in the incident.
2. Enriches incident with security information about domains using [Cisco Umbrella Investigate API](https://developer.cisco.com/docs/cloud-security/investigate-investigate/#investigate).

<img src="./Images/playbook_screenshot1.png" width="70%"/><br>

<img src="./Images/playbook_screenshot2.png" width="70%"/><br>

<img src="./Images/playbook_screenshot3.png" width="70%"/><br>

### Prerequisites

1. Login to Cisco Umbrella dashboard and navigating to Admin-->API Keys. Create New API Key if not already created and select the appropriate "Key Scope" with Read/Write permission. Store "Api Key" and "Key Secret" to a safe place. This "Api Key" is a "Client Id" and "Key Secret" is a "Secret" used for this Playbook.
2. Store the "Api Key" and "Key Secret" from previous step to Key vault Secrets.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here
    * Keyvault name: Name of the key vault where secrets are stored.
    * Umbrella API Client Id Key Name: Name of the Secrets field from Keyvault where Cisco Umbrella "API Key" value is stored.
    * Umbrella API Secret Key Name: Name of the Secrets field from Keyvault where Cisco Umbrella "Key Secret" value is stored.
    * Host End Point: Default is "api.umbrella.com" and is used for any API call to Cisco Umbrella REST API's.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooksk%2FCiscoUmbrellaPlaybooks%2FCiscoUmbrella-GetDomainInfo%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrellaPlaybooks%2FCiscoUmbrella-GetDomainInfo%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for Cisco Umbrella Investigate connector API Connection. For authorizing, provide your API key in the following format: "Bearer YOUR_API_KEY".

#### b. Configurations in Sentinel

1. In Microsoft sentinel, analytical rules should be configured to trigger an incident. In the *Entity mapping* section of the analytics rule creation workflow, malicious URL should be mapped to **Url** identifier of the **URL** entity type. Check the [documentation](https://docs.microsoft.com/azure/sentinel/map-data-fields-to-entities) to learn more about mapping entities.
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
 - [Cisco Umbrella API Documentation](https://developer.cisco.com/docs/cloud-security/authentication/#authentication)
 - [Rest API Request And Response Sample to Get Security Score Information for Domain](https://developer.cisco.com/docs/cloud-security/secure-access-api-guides-request-and-response-samples-investigate-investigate/#get-security-score-information-for-domain)
  - [Rest API Request And Response Sample to Get Risk Score for Domain](https://developer.cisco.com/docs/cloud-security/secure-access-api-guides-request-and-response-samples-investigate-investigate/#get-risk-score-for-domain)