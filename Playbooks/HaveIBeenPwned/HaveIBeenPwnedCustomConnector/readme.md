# HaveIBeenPwned Logic Apps Custom connector

This custom connector connects to HaveIBeenPwned service end point and gets the required information from the HaveIBeenPwned repository.

![HaveIBeenPwned](../HaveIBeenPwned.jpg)<br>

### Authentication methods this connector supports

*  API Key authentication

### Prerequisites for deploying Custom Connector
1. HaveIBeenPwned service end point should be known. (e.g.  https://{haveibeenpwned.com})


## Actions supported by HaveIBeenPwned custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **Get all breaches for an account** | Retrieves list of all breaches for an account|
| **Get breached site/sites Information** | Retrieves list of all breaches for all site/sites|
| **Get all data classes in the system** | Retrieves list of all records that can be compromised in a breach|
| **Get all pastes for an account** | Retrieves list of all pastes for an account|


### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will lead you to the wizard for deploying an ARM Template.
2. Fill in the required parameters:
    * Custom Connector Name : Enter the Custom connector name (e.g. HaveIBeenPwned_connector)
    * Service Endpoint : Enter the HaveIBeenPwned service end point (e.g. https://{haveibeenpwned.com})

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FHaveIBeenPwned%2FHaveIBeenPwnedCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FHaveIBeenPwned%2FHaveIBeenPwnedCustomConnector%2Fazuredeploy.json)

## Usage Examples
* Get all breaches for an account.
* Get all breached sites in the system.



