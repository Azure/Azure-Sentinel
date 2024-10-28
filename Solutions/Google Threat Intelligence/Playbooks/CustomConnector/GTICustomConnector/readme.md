# Google Threat Intelligence - Custom Connector

<img src="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Logos/GoogleThreatIntelligence.svg" alt="Google" style="width:150px; height:150px"/><br>

This custom connector connects to Google Threat Intelligence API to execute actions supported by returns response in JSON format.

## Authentication type

* API Key

## With this connector, you can:

- Analyze suspicious files and URLs: Submit files and URLs to GTI for analysis, retrieving comprehensive reports on potential threats.
- Detect various types of malware: Identify a wide range of malware, including viruses, trojans, ransomware, and more.
- Automatically share threat information: Contribute to the security community by automatically sharing analyzed files and URLs with GTI.
- Streamline security workflows: Automate tasks like malware analysis, and incident response within your Power Platform applications.
- Enhance threat intelligence: Integrate GTI's rich threat data into your existing security systems and processes.


## Pre-requisites
To use this integration, you need:

A GTI account: Follow the steps on https://developers.virustotal.com/v3.0/reference#getting-started to get your API key.

Microsoft Power Platform environment: Access to Power Automate or Power Apps to create and deploy flows or applications.

API documentation
For detailed information on the GTI API, please refer to the official documentation: https://developers.virustotal.com/v3.0/reference

## Deployment

<a href="https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FCustomConnectors%2FGTICustomConnector%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FCustomConnectors%2FGTICustomConnector%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

## Google Threat Intelligence Connector Actions

This document provides detailed descriptions of all actions available in the Google Threat Intelligence connector for Microsoft Power Platform.

### File Analysis

* **Upload File**

    * **Description:** Submits a file to VirusTotal for analysis. This action initiates the analysis process and returns a unique identifier for tracking the analysis progress and retrieving the report later.
    * **Input:** File content (binary data).
    * **Output:** Analysis ID (string).

* **Get File Report**

    * **Description:** Retrieves a detailed analysis report for a specific file identified by its unique ID (SHA-256 hash). The report includes information such as antivirus detection rates, community ratings, behavioral analysis, and more.
    * **Input:** File ID (string).
    * **Output:** File analysis report (object).


### URL Analysis

* **Analyze URL**

    * **Description:**  Submits a URL to VirusTotal for analysis. This action starts the analysis process and returns a unique identifier for tracking the analysis progress and retrieving the report.
    * **Input:** URL (string).
    * **Output:** Analysis ID (string).

* **Get URL Report**

    * **Description:** Retrieves an analysis report for a specific URL. The report contains information such as website safety ratings, malware detection results, phishing indicators, and more.
    * **Input:** URL (string).
    * **Output:** URL analysis report (object).


### IP Address Analysis

* **Get IP Report**

    * **Description:** Retrieves analysis and reputation information for a given IP address. This includes details like geolocation, associated domain names, malware connections, and security assessments.
    * **Input:** IP address (string).
    * **Output:** IP address report (object).


### Domain Analysis

* **Get Domain Report**

    * **Description:** Retrieves analysis and reputation information for a specified domain name. The report includes details such as registration information, associated IP addresses, malware distribution history, and security assessments.
    * **Input:** Domain name (string).
    * **Output:** Domain report (object).


### Analysis Retrieval

* **Retrieve URL/File Analysis**

    * **Description:**  Retrieves information about a specific file or URL analysis request. This action allows you to check the status of an ongoing analysis or fetch the results of a completed analysis.
    * **Input:** Analysis ID (string).
    * **Output:** Analysis information (object) including status and results.

**Note:** All actions require an API key for authentication.  Please refer to the "Pre-requisites" section in the `readme.md` file for instructions on obtaining and using your API key.


