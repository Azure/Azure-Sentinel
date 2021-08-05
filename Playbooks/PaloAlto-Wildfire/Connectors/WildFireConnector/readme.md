# Palo Alto Wildfire Logic Apps Custom Connector

![Palo Alto WildFire](./Wildfire-CustomConnector.png)

# Overview
The WildFire API extends the malware detection capabilities of WildFire through a RESTful
XML-based API. Using the API, we can get file analysis. We can also use the WildFire API
through your script or service to query WildFire for verdicts, samples, and reports.

# Authentication
* API Key authentication.

# Actions supported by Wildfire Custom Connector
| Component | Description |
| --------- | -------------- |
| **Get a WildFire Analysis Report** | Action used to get a WildFire analysis report for a specified sample hash value or web page URL |
| **Get a Sample** | Action used to get sample files based on the MD5 or SHA-256 hash value |
| **Get URL Web Artifacts** | Action used to get the web artifacts found during analysis of the specified web page URL |
| **Get a Packet Capture** |Action used to request a packet capture (PCAP) recorded during analysis of a particular sample |
| **Get a MacOSX Test File** | Action used to get a MacOSX test file, which you can use to test end-to-end WildFire sample processing |
| **Get a Android Application Package Test File** | Action used to get a APK test file, which you can use to test end-to-end WildFire sample processing |
| **Get a Executable Linkable Format Test File** | Action used to get a ELF test file, which you can use to test end-to-end WildFire sample processing |
| **Get a Portable Executable Test File** | Action used to get a PE test file, which you can use to test end-to-end WildFire sample processing |
| **Get a WildFire Verdict** | Action used to get a WildFire verdict for a sample based on the MD5 or SHA-256 hash or a web page based on the URL |
| **Submit a Website Link to WildFire** | Action used to submit a single website link for WildFire analysis |
| **Submit a Remote File to WildFire** | Action used to submit a supported file type on a website for WildFire analysis|

# Prerequisites for deploying WildFire Custom Connector
- Wildfire API end point should be known. ([WildFire Console](https://wildfire.paloaltonetworks.com))

# Deploy WildFire Custom Connector
Click on the below button to deploy WildFire Custom Connector in your Azure subscription.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPaloAlto-Wildfire%2FConnectores%2FWildFireConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FPaloAlto-Wildfire%2FConnectores%2FWildFireConnector%2Fazuredeploy.json)


# Deployment Instructions 
1. Deploy the WildFire custom connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.
2. Fill in the required parameters for deploying WildFire custom connector.

## Deployment Parameters

| Parameter  | Description |
| ------------- | ------------- |
| **Custom Connector Name** | Enter the name of WildFire custom connector |
| **Service End Point** | Enter the Service End Point of Wildfire API [WildFire Console](https://wildfire.paloaltonetworks.com)|