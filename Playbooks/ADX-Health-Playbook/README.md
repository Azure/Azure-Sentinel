# ADX Health Playbook

Author: María de Sousa-Valadas  <br />
Version: 1.0

If you have ADX set up as your long-term retention solution for Azure Sentinel, you may want to use this logic app to make sure that the logs you are ingesting into Azure Sentinel are reaching your ADX cluster, and receive a warning via email if an unexpected delay is detected.
<br />
This Logic App is complementary to the [ADXvsLA workbook](https://github.com/Azure/Azure-Sentinel/blob/master/Workbooks/ADXvsLA.json "ADXvsLA workbook") created by Naomi Christis. It compares the number of logs in your Log Analytics tables with your logs in the ADX Cluster Database tables periodically and sends a warning email if a delay is detected. 

## Deploy to Azure
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FADX-Health-Playbook%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FADX-Health-Playbook%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>                                                                                                                      
                                                                                
## Pre-requisites
You must have set up Azure Data Explorer as your long-term retention solution for Azure Sentinel logs. 
   <br />  
## Post-deployment configuration

### Connections
There are three API connections in this logic app

* **Connection to Azure Data Explorer**: this leverages the system-assigned managed identity that is set up by default in this template. To authorize this conneciton, please assign the Database Reader role to the logic app. To do this, go to *Azure Data Explorer clusters*, select your cluster, select *Databases*, select your database, select *Permissions* > *+Add* > *Viewer*, and finally select the playbook you have just deployed. This will allow the logic app to query the ADX tables that you are using for long-term ingestion
* **Connection to Azure Monitor**: this connector supports user identity or service principal (recommended). The user or service principal you use to create the connection will need to have at least Reader role at RG level, or Azure Sentinel Reader role.
* **Connection to Office 365 Outlook**: this connector only supports user identity, so you will need to connect with a user that has an Exchange Online license assigned. This user will appear as the sender of the warning notification
 
### Other
* By default this logic app runs every 24 hours, you can change this on the Recurrence trigger:
   <img src="https://github.com/mariavaladas/Azure-Sentinel/blob/master/Playbooks/ADX-Health-Playbook/images/1.%20trigger.png">

* The logic app assumes that your tables on Azure Sentinel and your final tables on ADX have the same name. Also, **the query is set to exclude the raw tables (before the mapping), assuming they include the word "Raw", which will be the case if you used the [Azure Data Explorer tool](https://github.com/Azure/Azure-Sentinel/tree/master/Tools/AzureDataExplorer  "Azure Data Explorer for long-term log retention") to set up your long-term solution. Should your tables follow a different naming convention, you would need to update this query**. If you wanted to exclude any tables from your query, you can customize your query for that purpose too:	
    <img src="https://github.com/mariavaladas/Azure-Sentinel/blob/master/Playbooks/ADX-Health-Playbook/images/2.%20adx%20query.png">

* The following query compares the results from your ADX tables against the Log Analytics tables. By default, the logic app **looks at the period between the past 25h and 30min**. We don't recommend making the endTime parameter lower than 20 minutes, as there is delay of a few minutes between the logs hitting Log Analytics and the ADX database.
    <img src="https://github.com/mariavaladas/Azure-Sentinel/blob/master/Playbooks/ADX-Health-Playbook/images/3.%20compare%20adx%20vs%20la.png">

* Finally, on the Azure Monitor queries, **select your subscription, resource group, resource type (Log Analytics Workspace) and resource name (your Azure Sentinel workspace name)**.

If the logic app detects a difference in the number of logs ingested in your Log Analytics and ADX tables, it will send a notification to the mailing list you defined in the parameters. 
**You can modify the text or the threshold**. By default, it will send an email when there is a difference between the tables greater than 0.
    <img src="https://github.com/mariavaladas/Azure-Sentinel/blob/master/Playbooks/ADX-Health-Playbook/images/4.%20condition.png">




 
