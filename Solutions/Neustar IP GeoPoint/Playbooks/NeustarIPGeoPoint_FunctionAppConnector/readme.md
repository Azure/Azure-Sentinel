# Neustar IP GeoPoint API Function App Connector

This Function App Connector is to connect Neustar IP GeoPoint API.

### Authentication methods supported by this connector

* Custom Authentication

### Prerequisites For Neustar IP GeoPoint API Function App Connector

Neustar IP GeoPoint API Key and Share Secret are required. 

1. Sign in to [Neustar IP GeoPoint](https://ipintelligence.neustar.biz/apps/login/?CL=gp.od.dev.nsr) Portal.
2. Go to Licences tab.
3. Click on the listed asset name to get the Key and Shared Secret.



## Actions supported by Neustar IP GeoPoint API Function App Connector

| **Component** | **Description** |
| --------- | -------------- |
| **GetIPGeoInfo** | Get geographical location information for the specified pubilc IPv4 and IPv6 addresses. |
||



### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - NeustarIPGeoPointAPIUrl 
    - NeustarIPGeoPointAPIKey
    - NeustarIPGeoPointSecret

==TODO==
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS_IAM%2FPlaybooks%2FAWS_IAM_FunctionAppConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAWS_IAM%2FPlaybooks%2FAWS_IAM_FunctionAppConnector%2Fazuredeploy.json) 
