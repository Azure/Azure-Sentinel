# Akamai Guardicore API Logic Apps Custom Connector

This Custom Connector is used for connection to Akamai Guardicore's API to process security incidents and enrich data for Microsoft Sentinel integration.

### Authentication methods supported by this connector

* User/Password authentication

### Prerequisites in Akamai Guardicore

Make sure to have a username/password with sufficient permissions to access Network Log

## Actions supported by Akamai Guardicore API Custom Connector

| **Component** | **Description**                                                                                                                                      |
| --------- |------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Get Pending Task** | Retrieves a pending task for processing from the connection slot marker.. |
| **Process Incident** | Processes security incidents from Microsoft Sentinel and tag them for enrichment.                                                                    |
| **Process Task** | Handles fetching network log data.                                                                                                                   |
| **Mark Task Failed** | Marks a task as failed in the connection slot marker system for error handling.                                                                      |
| **Incident Data Timer** | Timer-triggered function for scheduled incident data processing and synchronization.                                                                 |
| **Incident Enrichment** | Orchestrates the network log fetching process.                                                                                                       |

### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAkamai%2520Guardicore%2FPlaybooks%2FCustomConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FAkamai%2520Guardicore%2FPlaybooks%2FCustomConnector%2Fazuredeploy.json)
