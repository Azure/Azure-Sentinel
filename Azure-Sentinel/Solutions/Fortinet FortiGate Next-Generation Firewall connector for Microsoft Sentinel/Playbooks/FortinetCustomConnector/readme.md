#  Fortinet Custom connector

This custom connector connects to Fortinet service end point and perform automated actions on the malicous IP and URL

![Fortinet](./Fortinetlogo.png)<br>

### Authentication criteria for connector

*  API Key authentication

### Prerequisites for deploying Custom Connector
- Fortinet service end point should be known (ex: https://{yourVMIPorTrafficmanagername}/)
- Generate an API key. Refer this link [how to generate the API Key](https://www.insoftservices.uk/fortigate-rest-api-token-authentication)

## Actions supported by Fortinet custom connector

| Component | Description |
| --------- | -------------- |
| **Create an address object** | This action will get an IP/URL and create an address object that can be later be added to an address group|
| **Update address group** | This action allows to add/remove an address object of an IP/URL address to an address group|
| **Add an URL to an address group** | This action allows to add an address object of an URL address to an address group|

### Deployment instructions 
- Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
- Fill the required parameters:
    * Service Endpoint: Enter the Fortinet service end point (ex: https://{YourVMIPorTrafficmanagement})

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FFortinet-FortiGate%2FCustomConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FFortinet-FortiGate%2FCustomConnector%2Fazuredeploy.json)

- Post deployment a logic app custom connector will be created with **FortinetConnector** name
## Usage Examples
* Create an address object to an IP, add to Sentinel blocked IP group and update incident accordingly
* Create an address object to an URL, add to Sentinel blocked URL group and update incident accordingly
*  Un-block IP and update incident accordingly
*  Un-block URL and update incident accordingly
*  Enrich incident with details of address objects and address groups details

