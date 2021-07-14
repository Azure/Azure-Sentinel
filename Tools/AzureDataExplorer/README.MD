## Integrate Azure Data Explorer (ADX) for long-term log retention
**Author : Sreedhar Ande**

Azure Data Explorer (ADX) is a big data analytics platform that is highly optimized for log and data analytics. Since ADX uses Kusto Query Language (KQL) as its query language, it's an excellent cost-effective alternative for long term Azure Sentinel data storage. Using Azure Data Explorer for your data storage enables you to run cross-platform queries and visualize data across both ADX and Azure Sentinel.

For more information, see the Azure Data Explorer [documentation](https://docs.microsoft.com/azure/sentinel/store-logs-in-azure-data-explorer)

To learn about architectural options please refer to my colleague's [Javier Soriano](https://github.com/javiersoriano) excellent [Blog](https://techcommunity.microsoft.com/t5/azure-sentinel/using-azure-data-explorer-for-long-term-retention-of-azure/ba-p/1883947)  

## Prerequisites
1. **Create an ADX Cluster in the same region as your Log Analytics Workspace**  
	https://docs.microsoft.com/azure/data-explorer/create-cluster-database-portal

2. Create ADX Database  

3. Please verify ADXSupportedTables.json file with [SupportedTables Section] (https://docs.microsoft.com/azure/azure-monitor/logs/logs-data-export?tabs=portal#supported-tables)    
   **Note**: If supported table is not listed in ADXSupportedTables.json, please updated your local file

## Azure Data Explorer Architecture

Combining the Log Analytics workspace data export feature, Event Hubs, and ADX, you can stream logs from Log Analytics to Event Hub and then ingest them into ADX. 

The high-level architecture should look like the following:

![ADXArchitecture](./images/AzureDataExplorerArchitecture.png)  

## Challenges
1. Use the Azure Data Explorer Web UI to create the target tables in the Azure Data Explorer database. For each table you need to get the schema and run the following commands which consumes lot of time for production workloads  
  
	A. **Create target table** Table that will have the same schema as the original one in Log Analytics/Sentinel
	
	B. **Create table raw** The data coming from Event Hub is ingested first to an intermediate table where the raw data is stored, manipulated, and expanded. Using an update policy (think of this as a function that will be applied to all new data), the expanded data will then be ingested into the final table that will have the same schema as the original one in Log Analytics/Sentinel. We will set the retention on the raw table to 0 days, because we want the data to be stored only in the properly formatted table and deleted in the raw data table as soon as it’s transformed. Detailed steps for this step can be found [here](https://docs.microsoft.com/azure/data-explorer/ingest-data-no-code?tabs=diagnostic-metrics#create-the-target-tables).    
	
	C. **Create table mapping** Because the data format is json, data mapping is required. This defines how records will land in the raw events table as they come from Event Hub. Details for this step can be found [here](https://docs.microsoft.com/azure/data-explorer/ingest-data-no-code?tabs=diagnostic-metrics#create-table-mappings).    
	
	D. **Create update policy** and attach it to raw records table. In this step we create a function (update policy) and we attach it to the destination table so the data is transformed at ingestion time. See details [here](https://docs.microsoft.com/azure/data-explorer/ingest-data-no-code?tabs=diagnostic-metrics#create-the-update-policy-for-metric-and-log-data). This step is only needed if you want to have the tables with the same schema and format as in Log Analytics  
	
	E.  **Modify retention for target table** The default retention policy is 100 years, which might be too much in most cases. With the following command we will modify the retention policy to be 1 year:    
	```.alter-merge table <tableName> policy retention softdelete = 365d recoverability = disabled  ```  

2.	To stream Log Analytics logs to Event Hub and then ingest them into ADX, you need to create Event Hub namespaces. If you have more than 10 tables, you need to create an Event Hub namespace for every 10 tables.  
 
	A.	Standard Event Hub Namespace supports only 10 Event Hub topics.  
	
	B.	Log Analytics data export rules also support 10 tables per rule.  
	
	C.	You can create 10 data export rules targeting 10 different Event Hub namespaces.
	
	**Note**  
	Only data generated after the data export rule is created will be sent to ADX; the data that existed before the rule creation will not be exported.

3.	Once Raw tables, Mappings tables, and Event Hub namespaces are in place, you need to create data export rules using the Azure CLI or the Azure REST API.  
	**Note:**  
	A. Azure portal and PowerShell cannot create data export rules at this time.    
	B. Data export rules create ***Event Hub topics*** in Event Hub namespaces (~20 min)    
	C. You will see Event Hub topics for each active log stream in those tables. An Event Hub topic will not be created for tables without logs. A topic will be created after data is received.     

4.	Once Event Hub Topics (```am-<<tablename>>```) are available – you need to create **data ingestion** or **data connection rules** in the ADX Cluster for each table by selecting appropriate Event Hub topic, TableRaw and TableMappings    

5.	Once data connection is successful – you will see the data flowing from Log Analytics to ADX (~ 15 min)    


## Download and run the PowerShell script

1. Download the script 
  
   [![Download](./images/Download.png)](https://aka.ms/Sentinel-AzureDataExplorer-Automation)
 
2. Extract the folder and open "Migrate-LA-to-ADX.ps1" either in Visual Studio Code or PowerShell  

   **Note**  
   The script runs from the user's machine. You must allow PowerShell script execution. To do so, run the following command:
   
   ```PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  
   ```  

3. If you do not provide the parameters on the command line, you will be prompted for the following parameter values:
	a.	Log Analytics resource group  
	b.	Log Analytics workspace name  
	c.	ADX resource group   
	d.	ADX Database name  
	e.	ADX Cluster URL (Example: `https://<<ADXClusterName>>.<<region>>.kusto.windows.net` )

4. You are prompted to authenticate with credentials, once the user is authenticated, you will be prompted to chose from the following options: 
	a. Retrieve all the tables from the workspace and then create Raw, Mappings table in ADX (or)  
	b. Provide a list of tables from the workspace  
	
5. Then the following modules are installed, if needed.
	```
	Az.Resources
	Az.OperationalInsights
	Kusto.CLI
	```
6. The table list is checked as to if they are supported by Log Analytics workspace data export. Any un-supported tables will be skipped. To view a list of supported tables navigate to [here](https://docs.microsoft.com/azure/azure-monitor/logs/logs-data-export?tabs=portal#supported-tables). For supported tables, the script will create the following:
	A. **Create target table** ```<<TableName>>```
		
	B. **Create raw table** ```<<TableName>>Raw```
	
	C. **Create table mapping** ```<<TableName>>RawMapping```
	
	D. **Create update policy** 
	
	E. **Modify retention for target table**
	
7. Then Event Hub namespaces are created. In this step, the script create Event Hub namespaces for groups of up to 10 tables.  
   **Note:** Event Hub Standard tier has limitation of having a maximum of 10 Event Hub topics.
	
8. Then data export rules are created in the Azure Log Analytics workspace. In this step, script will create data export rules for each Event Hub namespace with 10 tables each.  

	**Note:**
	a.	Based on the output from Step #4, the script will create data export rules for each 10 tables.  
	b.	Log Analytics supports 10 data export rules targeting 10 different Event Hub namespaces, i.e., you can export 100 tables using 10 data export rules.  
	
9. After successful creation of data export rules - the script prompts the user to wait 30 minutes for the selected tables to be created in the Event Hub namespace.  
	a. If Yes, the script will proceed to create the data connection rules after waiting 30 minutes by specifying the target raw table ```<<TableName>>Raw```, mapping table ```<<TableName>>RawMapping``` and Event Hub topic ```am-<<TableName>>```  
	b. If No, the script will exit, and user has to create data connection for each table in Azure Data Explorer by selecting appropriate Raw, Mapping Tables and Event Hub topic.  

10. A log file is generated at the end of the script named:  ```ADXMigration_<<TimeStamp>>.csv```. The log includes every script action and should be used to identify performance or configuration issues and to gain insights to perform root cause analysis in the case of failures.  
