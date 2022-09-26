# Elastic Search API Logic Apps Custom connector

This Custom Connector is used for connection to Elastic Search's search API.

### Authentication methods supported by this connector

* API Key authentication

### Prerequisites in Rapid7 InsightVM

To get Elastic Search API key, follow the instructions in the [documentation](https://www.elastic.co/guide/en/kibana/master/api-keys.html).

## Actions supported by Rapid7 InsightVM API Custom Connector

| **Component** | **Description** |
| --------- | -------------- |
| **Run Search** | Returns search hits that match the query defined in the request.|
| **Run Async-Search** | Let you submit a search request asynchronously |
| **Get Async-Search Result** | Retrieves the results of a previously submitted async search request given its id |
| **Get Async-Search Status** | Get async search status, without retrieving search results, shows only the status of a previously submitted async search request given its id |
| **Search Shards** | Returns the indices and shards that a search request would be executed against. |



### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRapid7InsightVM%2FPlaybooks%2FRapid7InsightVMCloudAPIConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRapid7InsightVM%2FPlaybooks%2FRapid7InsightVMCloudAPIConnector%2Fazuredeploy.json)
