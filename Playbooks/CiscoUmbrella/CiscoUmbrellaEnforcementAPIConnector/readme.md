# Cisco Umbrella Enforcement API Logic Apps Custom connector

This custom connector connects to Cisco Umbrella Enforcement API.

### Authentication methods this connector supports

* API Key authentication

### Prerequisites in Cisco Umbrella

To get Cisco Umbrella Enforcement API credentials follow the instructions:

1. Login to your Cisco Umbrella dashboard.
2. Navigate to Policies > Policy Components > Integrations.
3. Expand an existing integration or click Add to generate a custom integration.
4. Get *customerKey* parameter value.

## Actions supported by Cisco Umbrella Enforcement API custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **Block domains** | Register a list of domain information with Umbrella and optionally add domains to a customer's domain lists. |
| **Get domains** | Get the list of domains added to the shared customer’s domain list. |
| **Delete domain by name** | Delete a domain from the shared customer’s domain list by domain name. |
| **Delete domain by id** | Delete a domain from the shared customer’s domain list by Id. |

### Deployment instructions

1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fcisco_umbrella_playbooks%2FPlaybooks%2FCiscoUmbrella%2FCiscoUmbrellaEnforcementAPIConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsocprime%2FAzure-Sentinel%2Fcisco_umbrella_playbooks%2FPlaybooks%2FCiscoUmbrella%2FCiscoUmbrellaEnforcementAPIConnector%2Fazuredeploy.json)