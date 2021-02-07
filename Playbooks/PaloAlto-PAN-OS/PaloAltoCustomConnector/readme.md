# PAN-OS Logic Apps Custom connector

This custom connector connects to PAN-OS service end point and performs defined automated actions on the PAN-OS firewall

![PAN-OS](./PAN-OS_CustomConnector.png)<br>

### Authentication methods this connector supports

*  API Key authentication

### Prerequisites for deploying Custom Connector
1. PAN-OS service end point should be known. (e.g.  https://{paloaltonetworkdomain})
2. Generate an API key. [Refer this link on how to generate the API Key](https://paloaltolactest.trafficmanager.net/restapi-doc/#tag/key-generation)


## Actions supported by Palo-Alto custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **List security rules** | Retrieves a list of all security rules within a specified location in the firewall|
| **Create a security policy rule** | Creates a new security policy rule in the firewall|
| **Reference an address object in a security policy rule** | References the address object in the security rule as a source or a destination member |
| **List custom url categories** | Retrieves a list of all URL filtering category information within a specified location in the firewall|
| **List address objects** | Retrieves a list of all address objects within a specified location in the firewall|
| **Create an address object** |Creates an address object depending on type : IP address or URL address|
| **Edit an address object** |Edits an address object depending on type : IP address or URL address|
| **List address groups** | Retrieves a list of all address object groups within a specified location in the firewall|
| **Create an address object group** | Creates an address object group in the firewall |
| **Edit an address object group** | Edits an address object group in the firewall (add/remove)  |
| **List URL filtering security profiles** | Retrieves a list of all URL filtering security profiles in the firewall (add/remove)  |
| **Edit URL filtering security profiles** | Edits URL filtering security profiles in the firewall (add/remove)  |
### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required parameters:
    * Custom Connector Name : Enter the Custom connector name (e.g. contoso PAN-OS connector)
    * Service Endpoint : Enter the PAN-OS service end point (e.g. https://{paloaltonetworkdomain}.net)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https://dev.azure.com/SentinelAccenture/Sentinel-Accenture%20Logic%20Apps%20connectors/_git/Sentinel-Accenture%20Logic%20Apps%20connectors?path=%2FPaloAltoCustomConnector%2Fazuredeploy&version=GBPaloAlto-PAN-OS)[![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://login.microsoftonline.us/organizations/oauth2/v2.0/authorize?client_id=c836cbdb-7a5b-44cc-a54f-564b4b486fc6&response_type=code%20id_token&scope=https%3A%2F%2Fmanagement.core.usgovcloudapi.net%2F%2Fuser_impersonation%20openid%20email%20profile&state=OpenIdConnect.AuthenticationProperties%3DaURMJdv8OOjkos8hJrPp2UR3SiCuzPqKSCojZXlvmudMu2wCQivYUBL-PUpm2VklFejdDnBr9Us32MzfuH8tith-XldC_OIlCqCjwB950H9ELHA76IfBBh19cTzh9-nsHhkQkk8wQDSE6bot7rUuEQB8IDVJgDMCfv1HYuUg9brFyPen2T4DF7f3SxN7Wwxfj87B5iDMqyoU1AHKentIKfwHsDQCVmhbtWdvSgPbWWABKGY-a7b1vkmjWNmo8x5v&response_mode=form_post&nonce=637443070124899368.YjM5MDcwYzMtODJkZC00MzRmLTgxNDctMjhhZjY0MWRmNjcxZGRiOWNmMmItMDAyNS00MTIxLWE4MDUtMjdiOTE4MWJhMjg0&redirect_uri=https%3A%2F%2Fportal.azure.us%2Fsignin%2Findex%2F&site_id=501430&msafed=0&client-request-id=5cc07576-a6f1-4a94-b26f-830ed1c4ad77&x-client-SKU=ID_NET45&x-client-ver=5.3.0.0)

## Usage Examples
* List security policy rules from PAN-OS through playbook.
* creates address objects of malicious IP/URL on PAN-OS through playbook.
* Add IP to address groups through playbook.



