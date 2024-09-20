# Check Point Software Technologies Logic Apps Connector
<br>
<br>
<p align="center">  
<img width="800" src="../images/check_point_logo.png"> </a>
</p>
<br>

# Table of Contents

1. [Overview](#overview)
1. [Deploy Connector](#deployall)
1. [Deployment instructions](#deployinstr)

<br>

<a name="overview">

# Overview

<p align="left">  
<img width="800" src="../images/cp_connector_detail.png"> </a>
</p>

The Check Point Logic App Connector allows you to connect to a Cloud or On-Prem Check Point Management Server using Check Point Managmeent API. The Function App Proxy is to overcome the platform limitation. 

For more information see

[Check Point Management API](https://sc1.checkpoint.com/documents/latest/APIs/#introduction~v1.6%20)  
[Logic App Overview](https://azure.microsoft.com/services/logic-apps/) 

<br>

<a name="deployall">

# Deploy Connector

## This package includes: 

1. Custom Connector which is based on Check Point Management API v1.6
2. FunctionApp Proxy

   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FCheckPointConnector%2FdeployCP.json)
   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FCheckPointConnector%2FdeployCPgov.json)
 

<br>

<a name="deployinstr">

# Deployment instructions

1. Create an API key from Check Point management console

    <p align="left">  
    <img width="400" src="../images/cp_create_api_key.png"> </a>
    </p>

2. Launch the template
<br>

   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FCheckPointConnector%2FdeployCP.json)
   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FCheckPointConnector%2FdeployCPgov.json)
 

3. Fill in the template - Make sure you include the backslash of API extension /web_api/ 

    <p align="left">  
    <img width="400" src="../images/cp_template.png"> </a>
    </p>

4. Copy the API key from the function app

    <p align="left">  
    <img width="400" src="../images/cp_copy_function_key.png"> </a>
    </p>

5. Paste function API key into the API management

    <p align="left">  
    <img width="400" src="../images/cp_copy_apimgmt_key.png"> </a>
    </p>
