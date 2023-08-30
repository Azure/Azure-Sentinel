# EclecticIQ API Logic Apps Custom connector

This Custom Connector is used for connecting to EclecticIQ platform using Rest API.

### Authentication methods supported by this connector

* API Key authentication

### Prerequisites in Rapid7 InsightVM

To get EclecticIQ API key, follow the instructions in the [documentation](https://developers.eclecticiq.com/docs/authenticate#generate-api-tokens).

## Actions supported by Rapid7 InsightVM API Custom Connector

| **Component** | **Description** |
| --------- | -------------- |
| **Get Observables** | Returns list of observables that matches with filtering criteria. [More Details](https://developers.eclecticiq.com/reference/get_observables) |
| **Create Observables** | Create an observables with the input details. [More Details](https://developers.eclecticiq.com/reference/post_observables) |
| **Create or Update Observables** | Create (or update if the (type, value) pair already exists) based on matching criteria. [More Details](https://developers.eclecticiq.com/reference/put_observables) |
| **Get Observable (by ID)** | Returns list of observables that matches with the ID. [More Details](https://developers.eclecticiq.com/reference/get_observables-id) |
| **Delete Observables (by ID)** | Deletes the observable that matches with the ID. [More Details](https://developers.eclecticiq.com/reference/delete_observables-id) |
| **UpdateObservables (by ID)** | Updates observable that matches with the ID. [More Details](https://developers.eclecticiq.com/reference/patch_observables-id) |
| **Get Sources List** | Returns list of all sources. [More Details](https://developers.eclecticiq.com/reference/get_sources) |
| **Get Sources (by ID)** | Returns source details that matches with the ID. [More Details](https://developers.eclecticiq.com/reference/get_sources-id) |



### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FEclecticIQ%2FPlaybooks%2FCustomConnector%2FEclecticIQCustomConnector%2Fazuredeploy.json) 
[![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FEclecticIQ%2FPlaybooks%2FCustomConnector%2FEclecticIQCustomConnector%2Fazuredeploy.json)
