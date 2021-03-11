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

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://dev.azure.com/SentinelAccenture/Sentinel-Accenture%20Logic%20Apps%20connectors/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FFortinetConnector%2Fazuredeploy.Json&version=GBFortinet) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)
- Post deployment a logic app custom connector will be created with **FortinetConnector** name
## Usage Examples
* Create an address object to an IP, add to Sentinel blocked IP group and update incident accordingly
* Create an address object to an URL, add to Sentinel blocked URL group and update incident accordingly
*  Un-block IP and update incident accordingly
*  Un-block URL and update incident accordingly
*  Enrich incident with details of address objects and address groups details

