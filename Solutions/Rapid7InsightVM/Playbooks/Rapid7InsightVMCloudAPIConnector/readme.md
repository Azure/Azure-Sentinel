# Rapid7 InsightVM Cloud Integrations API Logic Apps Custom connector

This Custom Connector is used for connection to Rapid7 InsightVM Cloud Integrations API.

### Authentication methods supported by this connector

* API Key authentication

### Prerequisites in Rapid7 InsightVM

To get Rapid7 InsightVM API key, follow the instructions in the [documentation](https://docs.rapid7.com/insight/managing-platform-api-keys/).

## Actions supported by Rapid7 InsightVM API Custom Connector

| **Component** | **Description** |
| --------- | -------------- |
| **Search Assets** | Returns the inventory, assessment, and summary details for a page of assets. |
| **Get Asset** | Returns the assessment and details of an asset (specified by id). |
| **Get Scans** | Retrieves a page of scans. |
| **Start Scan** | Starts a scan. |
| **Get Scan Engines** | Retrieves a page of scan engines. |
| **Get Scan Engine** | Retrieves the scan engine with the specified identifier. |
| **Get Scan** | Retrieves the scan with the specified identifier. |
| **Stop Scan** | Stops the scan with the specified identifier. |
| **List Sites** | Returns the details for sites. |
| **Search Vulnerabilities** | Returns all vulnerabilities that can be assessed. |


### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRapid7InsightVM%2FPlaybooks%2FRapid7InsightVMCloudAPIConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRapid7InsightVM%2FPlaybooks%2FRapid7InsightVMCloudAPIConnector%2Fazuredeploy.json)
