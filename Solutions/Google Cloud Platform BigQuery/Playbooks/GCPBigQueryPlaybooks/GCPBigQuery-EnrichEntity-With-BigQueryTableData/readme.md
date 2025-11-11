# GCPBigQuery-EnrichEntity-With-BigQueryTableData

## Summary

This playbook can be run from incident context manually or from automation rule to query the GCP BigQuery table and enrich the incident with query results. Query result is filtered based on provided entities. The playbook performs following actions:

1. Gets all the entities from the incident.
2. Create the SQL query string based on the entities.
2. Runs the SQL query as Query job and gets the result.
3. Parse the result and format as table.
3. Add the result as comment to the incident. 

<img src="./images/GCPBigQuery-EnrichEntity-With-BigQueryTableData_light.jpg" width="50%"/><br>
<img src="./images/GCPBigQuery-EnrichEntity-With-BigQueryTableDataOutput_light.jpg" width="50%"/><br>

### Prerequisites

1. Prior to the deployment of this playbook, [GCPBigQuery Logic App Custom Connector](../../CustomConnector/GCPBigQueryCustomConnector/azuredeploy.json) needs to be deployed under the same subscription.
2. Refer to [GCPBigQuery Logic App Custom Connector](../../CustomConnector/GCPBigQueryCustomConnector/readme.md) documentation for deployment instructions.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name
    * Custom Connector Name
    * GCP Project ID
    * SQL Base Query 
    * BigQuery Table Column Name to be used for filtering 

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Cloud%2520Platform%2520BigQuery%2FPlaybooks%2FGCPBigQueryPlaybooks%2FGCPBigQuery-EnrichEntity-With-BigQueryTableData%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Cloud%2520Platform%2520BigQuery%2FPlaybooks%2FGCPBigQueryPlaybooks%2FGCPBigQuery-EnrichEntity-With-BigQueryTableData%2Fazuredeploy.json)

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
9. Select Role - Microsoft Sentinel Responder
10. Click Save

#  References
 - [BigQuery API Quick Reference](https://cloud.google.com/bigquery/docs/reference/rest)
 - [BigQuery Documentation](https://cloud.google.com/bigquery/docs)