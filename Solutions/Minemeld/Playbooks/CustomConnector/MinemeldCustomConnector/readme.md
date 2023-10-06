# Minemeld Logic Apps Custom connector

This custom connector connects to Minemeld service end point to runs any Minemeld supported API queries and gives response back in json format.
### Authentication methods this connector supports

*  Basic authentication

### Prerequisites for deploying Custom Connector
1. Minemeld host end point or url should be known(ex : soar.minemeld.net)
2. Basic authentication of user and password is required for accessing Minemeld API.


## Actions supported by Minemeld custom connector

| Component | Description |
| --------- | -------------- |
| **Add Delete Update indicators** | Add Delete and update indicators available in minemeld |
| **Get indicators** | Fetch the detailed enriched data of indicators available at minemeld |


### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters:
    * Custom Connector Name : Enter the Custom connector name (ex:MinemeldCustomConnector)
    * Minemeld Host URL: Enter the Minemeld URL or Host (ex: soar.minemeld.net)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FMinemeld%2FPlaybooks%2FCustomConnector%2FMinemeldCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2FSolutions%2F%Minemeld%2FPlaybooks%2FCustomConnector%2FMinemeldCustomConnector%2Fazuredeploy.json)

## Usage Examples
* Get indicator information from Minemeld and add to Sentinel incident comment through playbook
* Add indicator information to Minemeld through playbook
* Update indicator data (for example score) in Minemeld through playbook
