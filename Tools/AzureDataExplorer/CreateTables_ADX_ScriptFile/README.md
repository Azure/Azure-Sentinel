## Create Azure Data Explorer Script file for generating Log Analytics Table mappings.
**Author : Alistair ROss**

Azure Data Explorer (ADX) is a big data analytics platform that is highly optimized for log and data analytics. Since ADX uses Kusto Query Language (KQL) as its query language, it's an excellent cost-effective alternative for long term Azure Sentinel data storage. Using Azure Data Explorer for your data storage enables you to run cross-platform queries and visualize data across both ADX and Azure Sentinel.

For more information, see the Azure Data Explorer [documentation](https://docs.microsoft.com/azure/sentinel/store-logs-in-azure-data-explorer)

To learn about architectural options please refer to my colleague's [Javier Soriano](https://github.com/javiersoriano) excellent [Blog](https://techcommunity.microsoft.com/t5/azure-sentinel/using-azure-data-explorer-for-long-term-retention-of-azure/ba-p/1883947)  

For some environments, creating the Log Analytics table mappings in Azure Data explorer isn't alway possbile as a single script, this could be due to technical restrictions, permissions or just a variation of your deployment model. This script, based on the original by [Sreedhar Ande](https://github.com/sreedharande), found [here](https://github.com/Azure/Azure-Sentinel/blob/master/Tools/AzureDataExplorer/CreateTables_ADX/Create-LA-Tables-ADX.ps1) will do the follow:
1. Source the tables from either:
    - All tables with data in the selected Log Analytics Workspace.
    - All tables with or without data in the selected Log Analytics Workspace.
    - A custom list of table names in an array which also exist in the selected Log Analytics Workspace.

2. For each table, it will build the management commands:
    - **Create target table** Table that will have the same schema as the original one in Log Analytics/Sentinel
    
    - **Create table raw** The data coming from Event Hub is ingested first to an intermediate table where the raw data is stored, manipulated, and expanded. Using an update policy (think of this as a function that will be applied to all new data), the expanded data will then be ingested into the final table that will have the same schema as the original one in Log Analytics/Sentinel. We will set the retention on the raw table to 0 days, because we want the data to be stored only in the properly formatted table and deleted in the raw data table as soon as it’s transformed. Detailed steps for this step can be found [here](https://docs.microsoft.com/azure/data-explorer/ingest-data-no-code?tabs=diagnostic-metrics#create-the-target-tables).    
    
    - **Create table mapping** Because the data format is json, data mapping is required. This defines how records will land in the raw events table as they come from Event Hub. Details for this step can be found [here](https://docs.microsoft.com/azure/data-explorer/ingest-data-no-code?tabs=diagnostic-metrics#create-table-mappings).    
    
    - **Create update policy** and attach it to raw records table. In this step we create a function (update policy) and we attach it to the destination table so the data is transformed at ingestion time. See details [here](https://docs.microsoft.com/azure/data-explorer/ingest-data-no-code?tabs=diagnostic-metrics#create-the-update-policy-for-metric-and-log-data). This step is only needed if you want to have the tables with the same schema and format as in Log Analytics  
    
    -  **Modify retention for target table** The default retention policy is 100 years, which might be too much in most cases. With the following command we will modify the retention policy to be 1 year:    
    ```.alter-merge table <tableName> policy retention softdelete = 365d recoverability = disabled  ```  

3. Output the management commands to a local text file for use in Azure Data Explorer database scripts https://learn.microsoft.com/en-us/azure/data-explorer/database-script. 

## Prerequisites

1. Permissions required
	- Azure Log Analytics workspace 'Read' permissions

## Download and run the script

1. Download the script

  **Note**  
   If you run the script on a user's machine. You must allow PowerShell script execution. To do so, run the following command:
   
   ```PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  
   ```  

2. Script will download and install the following modules, if its not installed on your machine
```
Az.Resources
Az.OperationalInsights
```

3. Run the script based on one of the following examples:

**Example 1** - This example queries all tables using 'search *| distinct $table' and creates ADX Raw and Mapping tables for all tables with data in the Log Analytics workspace.
```PowerShell
.\Create-LA-Tables-ADX-ScriptFile.ps1 `
    -LogAnalyticsResourceGroup "la-resgrp1" `
    -LogAnalyticsWorkspaceName "la-workspace-1" `
    -OnlyTablesWithData `
    -OutputFolderPath "C:\Temp\ADXScript"
```
**Example 2** - This example queries all tables using Get-AzOperationalInsightsTable and creates ADX Raw and Mapping tables for all tables in the Log Analytics workspace.
Using the -Force switch, it bypasses any user input, assuming that authentication has already been completed using Connect-AzAccount.
```PowerShell
$TablesList = @("AzureActivity", "SigninLogs")
.\Create-LA-Tables-ADX-ScriptFile.ps1 `
    -LogAnalyticsResourceGroup "la-resgrp1" `
    -LogAnalyticsWorkspaceName "la-workspace-1" `
    -TableNameList $TablesList `
    -Force `
    -OutputFolderPath "C:\Temp\ADXScript"
```

**Example 3** - This example takes the tables from an array and creates ADX Raw and Mapping tables for each table in the Log Analytics workspace.
If the table does not exist, the script does not create the ADX Raw and Mapping tables, but logs the error in the log and script file.
```PowerShell
$Tables = @("AzureActivity", "SigninLogs")
.\Create-LA-Tables-ADX-ScriptFile.ps1 `
    -LogAnalyticsResourceGroup "la-resgrp1" `
    -LogAnalyticsWorkspaceName "la-workspace-1" `
    -TableNameList $Tables `
    -Force `
    -OutputFolderPath "C:\Temp\ADXScript"
```
4. Locate the file found in either in:
   - <OutputFolderPath>\ADXScripts\adxCommandsScriptFile.txt
   - <ScriptRootDirectory>\ADXScripts\adxCommandsScriptFile.txt

5. Review the file contents.

```kusto
//Log Analytics Tables to ADX Tables Mapping
//TimeGenerated: 20240625_151552
//Log Analytics Workspace: a798b94d-acea-4d04-af11-2a517eb60d0f

//TableName: AzureActivity

.create-merge table AzureActivityRaw (Records:dynamic)

.create-or-alter table AzureActivityRaw ingestion json mapping 'AzureActivityRawMapping' '[{"column":"Records","Properties":{"path":"$.records"}}]'

.alter-merge table AzureActivityRaw policy retention softdelete = 0d

.create-merge table AzureActivity (OperationName:string,OperationNameValue:string,Level:string,ActivityStatus:string,ActivityStatusValue:string,ActivitySubstatus:string,ActivitySubstatusValue:string,ResourceGroup:string,SubscriptionId:string,CorrelationId:string,Caller:string,CallerIpAddress:string,Category:string,CategoryValue:string,HTTPRequest:string,Properties:string,EventSubmissionTimestamp:datetime,Authorization:string,ResourceId:string,OperationId:string,ResourceProvider:string,ResourceProviderValue:string,Resource:string,EventDataId:string,TenantId:string,TimeGenerated:datetime,SourceSystem:string,Authorization_d:string,Claims:string,Claims_d:string,Properties_d:string,Hierarchy:string,Type:string,_ResourceId:string)

.create-or-alter function AzureActivityExpand {AzureActivityRaw | mv-expand events = Records | project OperationName = tostring(events.OperationName),OperationNameValue = tostring(events.OperationNameValue),Level = tostring(events.Level),ActivityStatus = tostring(events.ActivityStatus),ActivityStatusValue = tostring(events.ActivityStatusValue),ActivitySubstatus = tostring(events.ActivitySubstatus),ActivitySubstatusValue = tostring(events.ActivitySubstatusValue),ResourceGroup = tostring(events.ResourceGroup),SubscriptionId = tostring(events.SubscriptionId),CorrelationId = tostring(events.CorrelationId),Caller = tostring(events.Caller),CallerIpAddress = tostring(events.CallerIpAddress),Category = tostring(events.Category),CategoryValue = tostring(events.CategoryValue),HTTPRequest = tostring(events.HTTPRequest),Properties = tostring(events.Properties),EventSubmissionTimestamp = todatetime(events.EventSubmissionTimestamp),Authorization = tostring(events.Authorization),ResourceId = tostring(events.ResourceId),OperationId = tostring(events.OperationId),ResourceProvider = tostring(events.ResourceProvider),ResourceProviderValue = tostring(events.ResourceProviderValue),Resource = tostring(events.Resource),EventDataId = tostring(events.EventDataId),TenantId = tostring(events.TenantId),TimeGenerated = todatetime(events.TimeGenerated),SourceSystem = tostring(events.SourceSystem),Authorization_d = tostring(events.Authorization_d),Claims = tostring(events.Claims),Claims_d = tostring(events.Claims_d),Properties_d = tostring(events.Properties_d),Hierarchy = tostring(events.Hierarchy),Type = tostring(events.Type),_ResourceId = tostring(events._ResourceId) }

.alter table AzureActivity policy update @'[{"Source": "AzureActivityRaw", "Query": "AzureActivityExpand()", "IsEnabled": "True", "IsTransactional": true}]'

//TableName: TestTable_CL
//Failed to find table in the Log Analytics Workspace

//TableName: SigninLogs

.create-merge table SigninLogsRaw (Records:dynamic)

.create-or-alter table SigninLogsRaw ingestion json mapping 'SigninLogsRawMapping' '[{"column":"Records","Properties":{"path":"$.records"}}]'

.alter-merge table SigninLogsRaw policy retention softdelete = 0d

.create-merge table SigninLogs (TenantId:string,SourceSystem:string,TimeGenerated:datetime,ResourceId:string,OperationName:string,OperationVersion:string,Category:string,ResultType:string,ResultSignature:string,ResultDescription:string,DurationMs:string,CorrelationId:string,Resource:string,ResourceGroup:string,ResourceProvider:string,Identity:string,Level:string,Location:string,AlternateSignInName:string,AppDisplayName:string,AppId:string,AuthenticationContextClassReferences:string,AuthenticationDetails:string,AppliedEventListeners:string,AuthenticationMethodsUsed:string,AuthenticationProcessingDetails:string,AuthenticationRequirement:string,AuthenticationRequirementPolicies:string,ClientAppUsed:string,ConditionalAccessPolicies:string,ConditionalAccessStatus:string,CreatedDateTime:datetime,DeviceDetail:string,IsInteractive:string,Id:string,IPAddress:string,IsRisky:string,LocationDetails:string,MfaDetail:string,NetworkLocationDetails:string,OriginalRequestId:string,ProcessingTimeInMilliseconds:string,RiskDetail:string,RiskEventTypes:string,RiskEventTypes_V2:string,RiskLevelAggregated:string,RiskLevelDuringSignIn:string,RiskState:string,ResourceDisplayName:string,ResourceIdentity:string,ResourceServicePrincipalId:string,ServicePrincipalId:string,ServicePrincipalName:string,Status:string,TokenIssuerName:string,TokenIssuerType:string,UserAgent:string,UserDisplayName:string,UserId:string,UserPrincipalName:string,AADTenantId:string,UserType:string,FlaggedForReview:string,IPAddressFromResourceProvider:string,SignInIdentifier:string,SignInIdentifierType:string,ResourceTenantId:string,HomeTenantId:string,UniqueTokenIdentifier:string,SessionLifetimePolicies:string,AutonomousSystemNumber:string,AuthenticationProtocol:string,CrossTenantAccessType:string,AppliedConditionalAccessPolicies:string,RiskLevel:string,Type:string)

.create-or-alter function SigninLogsExpand {SigninLogsRaw | mv-expand events = Records | project TenantId = tostring(events.TenantId),SourceSystem = tostring(events.SourceSystem),TimeGenerated = todatetime(events.TimeGenerated),ResourceId = tostring(events.ResourceId),OperationName = tostring(events.OperationName),OperationVersion = tostring(events.OperationVersion),Category = tostring(events.Category),ResultType = tostring(events.ResultType),ResultSignature = tostring(events.ResultSignature),ResultDescription = tostring(events.ResultDescription),DurationMs = tostring(events.DurationMs),CorrelationId = tostring(events.CorrelationId),Resource = tostring(events.Resource),ResourceGroup = tostring(events.ResourceGroup),ResourceProvider = tostring(events.ResourceProvider),Identity = tostring(events.Identity),Level = tostring(events.Level),Location = tostring(events.Location),AlternateSignInName = tostring(events.AlternateSignInName),AppDisplayName = tostring(events.AppDisplayName),AppId = tostring(events.AppId),AuthenticationContextClassReferences = tostring(events.AuthenticationContextClassReferences),AuthenticationDetails = tostring(events.AuthenticationDetails),AppliedEventListeners = tostring(events.AppliedEventListeners),AuthenticationMethodsUsed = tostring(events.AuthenticationMethodsUsed),AuthenticationProcessingDetails = tostring(events.AuthenticationProcessingDetails),AuthenticationRequirement = tostring(events.AuthenticationRequirement),AuthenticationRequirementPolicies = tostring(events.AuthenticationRequirementPolicies),ClientAppUsed = tostring(events.ClientAppUsed),ConditionalAccessPolicies = tostring(events.ConditionalAccessPolicies),ConditionalAccessStatus = tostring(events.ConditionalAccessStatus),CreatedDateTime = todatetime(events.CreatedDateTime),DeviceDetail = tostring(events.DeviceDetail),IsInteractive = tostring(events.IsInteractive),Id = tostring(events.Id),IPAddress = tostring(events.IPAddress),IsRisky = tostring(events.IsRisky),LocationDetails = tostring(events.LocationDetails),MfaDetail = tostring(events.MfaDetail),NetworkLocationDetails = tostring(events.NetworkLocationDetails),OriginalRequestId = tostring(events.OriginalRequestId),ProcessingTimeInMilliseconds = tostring(events.ProcessingTimeInMilliseconds),RiskDetail = tostring(events.RiskDetail),RiskEventTypes = tostring(events.RiskEventTypes),RiskEventTypes_V2 = tostring(events.RiskEventTypes_V2),RiskLevelAggregated = tostring(events.RiskLevelAggregated),RiskLevelDuringSignIn = tostring(events.RiskLevelDuringSignIn),RiskState = tostring(events.RiskState),ResourceDisplayName = tostring(events.ResourceDisplayName),ResourceIdentity = tostring(events.ResourceIdentity),ResourceServicePrincipalId = tostring(events.ResourceServicePrincipalId),ServicePrincipalId = tostring(events.ServicePrincipalId),ServicePrincipalName = tostring(events.ServicePrincipalName),Status = tostring(events.Status),TokenIssuerName = tostring(events.TokenIssuerName),TokenIssuerType = tostring(events.TokenIssuerType),UserAgent = tostring(events.UserAgent),UserDisplayName = tostring(events.UserDisplayName),UserId = tostring(events.UserId),UserPrincipalName = tostring(events.UserPrincipalName),AADTenantId = tostring(events.AADTenantId),UserType = tostring(events.UserType),FlaggedForReview = tostring(events.FlaggedForReview),IPAddressFromResourceProvider = tostring(events.IPAddressFromResourceProvider),SignInIdentifier = tostring(events.SignInIdentifier),SignInIdentifierType = tostring(events.SignInIdentifierType),ResourceTenantId = tostring(events.ResourceTenantId),HomeTenantId = tostring(events.HomeTenantId),UniqueTokenIdentifier = tostring(events.UniqueTokenIdentifier),SessionLifetimePolicies = tostring(events.SessionLifetimePolicies),AutonomousSystemNumber = tostring(events.AutonomousSystemNumber),AuthenticationProtocol = tostring(events.AuthenticationProtocol),CrossTenantAccessType = tostring(events.CrossTenantAccessType),AppliedConditionalAccessPolicies = tostring(events.AppliedConditionalAccessPolicies),RiskLevel = tostring(events.RiskLevel),Type = tostring(events.Type) }

.alter table SigninLogs policy update @'[{"Source": "SigninLogsRaw", "Query": "SigninLogsExpand()", "IsEnabled": "True", "IsTransactional": true}]'

```
You can now deploy the table creation script via your method of choice.
- https://learn.microsoft.com/en-us/azure/data-explorer/database-script
- https://learn.microsoft.com/en-us/azure/data-explorer/kusto/management/execute-database-script
