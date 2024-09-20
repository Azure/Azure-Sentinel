## Ingest Customlogs via DCE/DCR
**Author : Sreedhar Ande**

Script to send data to a data collection endpoint which is a unique connection point for your subscription. The payload sent to Azure Monitor must be in JSON format. A data collection rule is needed in your Azure tenant that understands the format of the source data, potentially filters and transforms it for the target table, and then directs it to a specific table in a specific workspace.
You can modify the target table and workspace by modifying the data collection rule without any change to the REST API call or source data.

## Pre-requisites  
1.	Register an Azure Active Directory application to authenticate against the API  
	https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs#configure-application  
	
2. Create Data Collection Endpoint (DCE) on Azure Monitor  
	https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs#create-data-collection-endpoint  
	
3. Create Customlog Table
	https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs#add-custom-log-table  
	
4. Create Data Collection Rule (DCR)  
   https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs-api#create-data-collection-rule

5. Collect DCR-ImmutableId  
	https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs#collect-information-from-dcr  
	
6. Assign Permissions to Data Collection Rule(DCR)  
	https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs-api#assign-permissions-to-dcr  

## Steps to Ingest Customlogs
1. Download the script 
  
   [![Download](/Tools/CustomLogsIngestion-DCE-DCR/images/Download.png)](https://aka.ms/customlogsingestion)

2. Extract the folder and open "Send-AzMonitorCustomLogs.ps1" either in Visual Studio Code/PowerShell

   **Note**  
   The script runs from the user's machine. You must allow PowerShell script execution. To do so, run the following command:
   
   ```PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  
   ```  
3. You are prompted to enter the following value 
	- **LogPath**    
    Path to the log file or folder (JSON|CSV) to read logs from and send them to Azure Monitor  
	- **AADAppId**  
    Azure Active Directory application to authenticate against the API to send logs to Azure Monitor data collection endpoint. This script supports the Client Credential Grant Flow.  
	- **AADAppSecret**  
    Secret text to use with the Azure Active Directory application to authenticate against the API for the Client Credential Grant Flow  
	- **TenantId**  
    ID of Tenant  
	- **DcrImmutableId**    
    Immutable ID of the data collection rule used to process events flowing to an Azure Monitor data table  
	- **DceURI**   
    Uri of the data collection endpoint used to host the data collection rule  
	- **StreamName**   
    Name of stream to send data to before being procesed and sent to an Azure Monitor data table  
    
