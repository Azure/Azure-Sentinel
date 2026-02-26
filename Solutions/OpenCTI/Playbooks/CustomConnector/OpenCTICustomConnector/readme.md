# OpenCTI Logic Apps Custom connector

This custom connector connects to OpenCTI service end point to runs any OpenCTI supported GraphQL queries and gives response back in json format.
### Authentication methods this connector supports

*  API Key authentication

### Prerequisites for deploying Custom Connector
1. OpenCTI host end point or url should be known(ex : demo.opencti.io)
2. API key. To get API Key, login into your OpenCTI instance dashboard and navigate to User profile page --> API Access.


## Actions supported by OpenCTI custom connector

| Component | Description |
| --------- | -------------- |
| **Run GraphQL query** | Run any supported GraphQL query and get the response in json format |


### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Custom Connector Name : Enter the Custom connector name (ex:OpenCTICustomConnector)
    * OpenCTI Host URL: Enter the OpenCTI URL or Host (ex: demo.opencti.io)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2F%2OpenCTI%2FPlaybooks%2FOpenCTICustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2FSolutions%2F%2OpenCTI%2FPlaybooks%2FOpenCTICustomConnector%2Fazuredeploy.json)

## Usage Examples
* Get indicator information from OpenCTI and add to Sentinel incodent comment through playbook
* Add indicator information to OpenCTI through playbook
* Update indicator data (for example score) in OpenCTI through playbook
