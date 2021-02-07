# PAN-OS Logic Apps Custom connector

This custom connector connects to PAN-OS service end point and performs defined automated actions on the PAN-OS firewall

  <img src="./PAN-OS_CustomConnector.png" alt="drawing" width="20%"/>

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

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2FSOAR-connectors-Private-Preview%2FPlaybooks%2FPaloAlto-PAN-OS%2FPaloAltoCustomConnector%2Fazuredeploy.json)[![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2FSOAR-connectors-Private-Preview%2FPlaybooks%2FPaloAlto-PAN-OS%2FPaloAltoCustomConnector%2Fazuredeploy.json)

## Usage Examples
* List security policy rules from PAN-OS through playbook.
* creates address objects of malicious IP/URL on PAN-OS through playbook.
* Add IP to address groups through playbook.



