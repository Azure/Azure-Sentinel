# THeHive API Logic Apps Custom connector

This Custom Connector is used for connection to TheHive API.

### Authentication methods supported by this connector

* Basic Authentication

### Prerequisites in Vendor Product

When creating the connection for the custom connector, you will be asked to provide user and password which you generated in
TheHive web interface.
TheHive connector uses [On-Premises Data Gateway](https://docs.microsoft.com/data-integration/gateway/service-gateway-onprem).
Therefore, [installation of the On-Premises Data Gateway](https://docs.microsoft.com/azure/logic-apps/logic-apps-gateway-install) and [creation of the On-Premises Data Gateway resource](https://docs.microsoft.com/azure/logic-apps/logic-apps-gateway-connection#create-azure-gateway-resource) are required.


## Actions supported by TheHive API Custom Connector

| **Component**                     | **Description**                     |
|-----------------------------------|-------------------------------------|
| **Create Alert**                  | Creates and alert                   |
| **Create Case**                   | Creates case                        |
| **Create Task**                   | Creates a task for a case           |
| **List observables**              | List last 30 observables for a case |
| **Lock user**                     | Lock a user                         |
| **Create observable for a case**  | Creates an observable which can be linked to a case                   |
| **Create observable for a alert** | Creates an observable which can be linked to a case                   |



### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTheHive%2FPlaybooks%2FTheHiveConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FTheHive%2FPlaybooks%2FTheHiveConnector%2Fazuredeploy.json)