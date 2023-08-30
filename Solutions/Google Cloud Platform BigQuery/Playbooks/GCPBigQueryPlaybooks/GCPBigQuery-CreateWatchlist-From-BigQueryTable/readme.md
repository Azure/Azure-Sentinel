# GCPBigQuery-CreateWatchlist-From-BigQueryTable

## Summary

This playbook can be run from incident context manually or from automation rule to create a watchlist from GCP BigQuery table data. The playbook performs following actions:

1. Get the table details for the given table.
2. Get the table data and parse the result.
3. Create a watchlist with the parsed data.
3. Add a comment to the incident of success/failure of action. 

<img src="./images/GCPBigQuery-CreateWatchlist-From-BigQueryTable_light.jpg" width="50%"/><br>
<img src="./images/GCPBigQuery-CreateWatchlist-From-BigQueryTableOutput_light.jpg" width="50%"/><br>

### Prerequisites

1. Prior to the deployment of this playbook, [GCPBigQuery Logic App Custom Connector](../../CustomConnector/GCPBigQueryCustomConnector/azuredeploy.json) needs to be deployed under the same subscription.
2. Refer to [GCPBigQuery Logic App Custom Connector](../../CustomConnector/GCPBigQueryCustomConnector/readme.md) documentation for deployment instructions.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name
    * Custom Connector Name
    * GCP Project ID
    * SQL Query String

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Cloud%2520Platform%2520BigQuery%2FPlaybooks%2FGCPBigQueryPlaybooks%2FGCPBigQuery-CreateWatchlist-From-BigQueryTable%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Cloud%2520Platform%2520BigQuery%2FPlaybooks%2FGCPBigQueryPlaybooks%2FGCPBigQuery-CreateWatchlist-From-BigQueryTable%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.

1. Select the Microsoft Sentinel connection resource
2. Click Edit API connection blade
3. Click Authorize/Provide credentials
4. Click Save
5. Repeat these steps for other connections

#### b. Configurations in Sentinel

1. In Microsoft Sentinel, configure the automation rule/analytical rule to trigger the playbook. Check the [documentation](https://docs.microsoft.com/azure/sentinel/tutorial-respond-threats-playbook) to learn more about automation rules.

#### c. Assign Playbook Microsoft Sentinel Responder Role
1. Select the Playbook (Logic App) resource
2. Click on Identity Blade
3. Choose System assigned tab
4. Click on Azure role assignments
5. Click on Add role assignments
6. Select Scope - Resource group
7. Select Subscription - where Playbook has been created
8. Select Resource group - where Playbook has been created
9. Select Role - **Microsoft Sentinel Contributor**
10. Click Save

#  References
 - [BigQuery API Quick Reference](https://cloud.google.com/bigquery/docs/reference/rest)
 - [BigQuery Documentation](https://cloud.google.com/bigquery/docs)