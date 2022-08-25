# CheckPhish by Bolster Logic Apps Custom connector

This custom connector connects to CheckPhish API service to run actions that are supported by CheckPhish and gives response back in json format.
### Authentication methods this connector supports

*  API Key authentication

### Prerequisites for deploying Custom Connector
1. CheckPhish host end point or url should be known(ex : https://developers.checkphish.ai)
2. API key. To get API Key, login into CheckPhish portal and select APIKey from the left side menu.

## Actions supported by okta custom connector

| Component | Description |
| --------- | -------------- |
| **Submit URL** | Send URL for CheckPhish scanning |
| **Get Scan Result** | Get the scan result from CheckPhish |


### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.
2. Fill in the required paramteres:
    * Custom Connector Name : Enter the Custom connector name (ex:CheckPhishbyBolsterCustomConnector)
    * OpenCTI Host URL: Enter the CheckPhish URL or Host (ex: https://developers.checkphish.ai)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheckPhish%20by%20Bolster%2FPlaybooks%2FCheckPhishbyBolsterCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheckPhish%20by%20Bolster%2FPlaybooks%2FCheckPhishbyBolsterCustomConnector%2Fazuredeploy.json)

## Usage Examples
* Get URL reputation for a given URL