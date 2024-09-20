# Prisma Cloud CSPM Logic Apps Custom connector

This custom connector connects to Prisma Cloud CSPM services end point to runs any Prisma cloud supported API get/post calls and gives response back in json format.
### Authentication methods this connector supports

*  Token generation via api secret key and user id 

### Prerequisites for deploying Custom Connector
1. API URL is needed which you can get that from [here](https://prisma.pan.dev/api/cloud/api-urls) or your Palo Alto vendor will help you to get the same.


## Actions supported by Prisma Cloud CSPM custom connector

| Component | Description |
| --------- | -------------- |
| **Login/Generate Token** | Allows for authorization and access to API commands using an API token |
| **Token Refresh** | Uses a valid, unexpired API access token to issue a new access token with a refreshed expiration time |
| **Asset Inventory View V2** | Returns asset inventory pass/fail data for the specified time period |
| **Asset Inventory Trend View V2** | Returns asset inventory pass/fail trends for the specified time period |
| **Asset Resource Scan** | Returns a full breakdown of passed/failed statistics and associated policies for resources |
| **Assets Enrichment** | Returns detailed information for the asset with the given id |
| **List Alerts** | Returns a list of alerts that match the constraints specified in the query parameters. Max 10k results |
| **Get Alert Info** | Returns information about an alert for the specified ID |
| **Get Anomaly Trusted List** | Returns all entries in the Anomaly Trusted List. |
| **Add Entries To Anomaly Trusted List** | Adds one or more entries to the Anomaly Trusted List |
| **List Remediation Command** | Generates and returns a list of remediation commands for the specified alerts and policies. Data returned for a successful call include fully constructed commands for remediation |
| **Remediate Alert** | Remediates the alert with the specified ID if that alert is associated with a remediable policy |


### Deployment instructions 
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPaloAltoPrismaCloud%2FPlaybooks%2FCustomConnector%2FPrismaCloudCSPMCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FPaloAltoPrismaCloud%2FPlaybooks%2FCustomConnector%2FPrismaCloudCSPMCustomConnector%2Fazuredeploy.json)

## Usage Examples
* Get Compliance posture of your asset and add to Sentinel incident comment through playbook
* Remediate breached policies and vulnerabilities and add status to Sentinel incident comment and teams chat through playbook
