# Cisco ISE API Logic Apps Custom connector

This custom connector connects to Cisco ISE External RESTful Services (ERS) API.

### Authentication methods this connector supports

* Basic authentication

### Prerequisites in Cisco ISE

To get Cisco ISE ERS API credentials [follow the instructions](https://developer.cisco.com/docs/identity-services-engine/#!setting-up).

Cisco ISE connector uses [On-Premises Data Gateway](https://docs.microsoft.com/data-integration/gateway/service-gateway-onprem). Therefore [installation of the On-Premises Data Gateway](https://docs.microsoft.com/azure/logic-apps/logic-apps-gateway-install) and [creation of the On-Premises Data Gateway resource](https://docs.microsoft.com/azure/logic-apps/logic-apps-gateway-connection#create-azure-gateway-resource) are required.

## Actions supported by Cisco Umbrella Management API custom connector

* Suspend guest user by name
* Assign an ANC policy to an endpoint
* Un-apply an ANC policy to an endpoint
* Get an ANC Endpoint
* Get all ANC Endpoints
* Create an ANC Policy
* Update the group of an endpoint
* Get rejected endpoints
* Release rejected endpoint

### Deployment instructions

1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deplyoing an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCisco%2520ISE%2FPlaybooks%2FCiscoISEConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCisco%2520ISE%2FPlaybooks%2FCiscoISEConnector%2Fazuredeploy.json)