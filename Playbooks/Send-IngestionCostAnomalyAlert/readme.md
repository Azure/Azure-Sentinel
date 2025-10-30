# Ingestion Anomaly Alert Playbook

This playbook sends you an alert should there be an ingestion spike into your workspace. The playbook uses the <em>series_decompose_anomalies</em> KQL function to determine anomalous ingestion.

## Deployment steps

Scroll to the bottom of this document and click the "Deploy to Azure" button




Fill in the parameters, changing the default values as required for your environment

![02-parameters](../Send-IngestionCostAnomalyAlert/images/02-parameters.png)

Select your newly deployed app from the resource group

![03-selectapp](../Send-IngestionCostAnomalyAlert/images/03-selectapp.png)

Click on edit to make the connections to Log Analytics and Office 365

![04-editapp](../Send-IngestionCostAnomalyAlert/images/04-editapp.png)

Defince the frequency the playbook should execute. Default is daily so you get alerted at the earliest sign of an ingestion anomaly

![05-recurrence](../Send-IngestionCostAnomalyAlert/images/05-recurrence.png)

Make the connections to your Log Analytics workspace using an account with the appropriate permissions. Do the same for Office 365.

![06-connections](../Send-IngestionCostAnomalyAlert/images/06-connections.png)

Save the app

![07-saveapp](../Send-IngestionCostAnomalyAlert/images/07-saveapp.png)

Enable the app

![08-enableapp](../Send-IngestionCostAnomalyAlert/images/08-enableapp.png)


<em> For more information on the anomaly function read this [this document](https://docs.microsoft.com/azure/data-explorer/kusto/query/series-decompose-anomaliesfunction)</em>


<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSend-IngestionCostAnomalyAlert%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton"/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2Send-IngestionCostAnomalyAlert%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>


