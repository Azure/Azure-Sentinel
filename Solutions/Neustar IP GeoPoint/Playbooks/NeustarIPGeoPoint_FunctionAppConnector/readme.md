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



### Deployment Instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - Neustar IP GeoPoint API Url 
    - Neustar IP GeoPoint API Key
    - Neustar IP GeoPoint Secret
    - Function App Name

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FNeustar%2520IP%2520GeoPoint%2FPlaybooks%2FNeustarIPGeoPoint_FunctionAppConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FNeustar%2520IP%2520GeoPoint%2FPlaybooks%2FNeustarIPGeoPoint_FunctionAppConnector%2Fazuredeploy.json) 

### Function App Settings (API Url, Key and Secret) Update Instruction
1. Select the Function App.
2. Click on the Configuration blade under Settings.
3. Select the Application settings tab.
4. Click on the Edit for a setting.
5. Update the Value.
6. Click Ok to save.
