# SilentPush-DomainExportEnrichment-Sample

## Summary

Runs every 24 hours, downloads the Silent Push IOFA domains export (`iofa-exports/all_iofas_domains.txt`), takes the first 100 domains and bulk-enriches them with Silent Push. It is a starting point to build your own playbook: it does not write the results anywhere.

### Prerequisites

1. A Silent Push API key ([sign up](https://app.silentpush.com)).
2. **Deploy the [Silent Push custom connector](../../Connector/SilentPushCustomConnector) first.** Installing the solution from Content Hub / Marketplace does **not** create it, and the connector does not appear under *Playbook templates*. Deploy it into the **same resource group** where you will create this playbook and keep its name as `SilentPush-API`. Otherwise *Create playbook* fails with "Connector 'SilentPush-API' not found". Deploy it here:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSilentPush%2FConnector%2FSilentPushCustomConnector%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSilentPush%2FConnector%2FSilentPushCustomConnector%2Fazuredeploy.json)

### Deployment instructions

1. Click **Deploy to Azure** below. This opens the ARM template deployment wizard.
2. Fill in the parameters:
    * **PlaybookName**: name of the playbook (default `SilentPush-DomainExportEnrichment-Sample`).
    * **CustomConnectorName**: name of the Silent Push custom connector deployed as a prerequisite above (default `SilentPush-API`).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSilentPush%2FPlaybooks%2FSilentPush-DomainExportEnrichment-Sample%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FSilentPush%2FPlaybooks%2FSilentPush-DomainExportEnrichment-Sample%2Fazuredeploy.json)

### Post-deployment instructions

#### a. Authorize the Silent Push connection

The playbook deploys with an empty API key for the Silent Push connection.

1. Open the deployed Logic App and go to **API connections**.
2. Select the `<PlaybookName>` connection.
3. Go to **General > Edit API connection**.
4. Enter your Silent Push API key and click **Save**.

#### b. Enable the playbook

The playbook is deployed **Disabled**. Enable it once the connection is authorized.
