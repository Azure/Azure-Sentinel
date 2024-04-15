# externaldata project
author: Nathan Swift

The following project will provide the example externaldata()[] KQL queries and schema to use agaisnt Azure Storage, where Data Export rules are sending the Azure Sentinel logs to for long term retention.

To leverage the solution create a Azure storage account where you will store long term retention security logs into. Create and deploy a data export rule to azure storage onto the Log analytics workspace, updating the deployment template to include the table names that need to have the logs stored in log term retention.

[Data Export ARM Template](https://docs.microsoft.com/azure/azure-monitor/logs/logs-data-export?tabs=json#create-or-update-data-export-rule)

Once logs are archiving into the Azure Storage account you can use the following script to operationalize extenal data lookup tasks by generating the Base KQL query that will include the schema and the SAS Uri signatures needed for each blob in start and end time range for 8 hours.

[Generate Storage Lookup KQL Query PowerShel Script](https://github.com/Azure/Azure-Sentinel/blob/master/Tools/externaldata/genstoragectxkql.ps1)

Example input into the script:
```
LAWorkspaceName : azulabs
StorageAcctName : siempipestorage
TableName 	: emailevents
StartDate 	: 09/11/2021 02:00 AM
EndDate 	: 09/12/2021 12:00 PM
```

The script generates a kql query .yaml file and opens the file in notepade.exe.

```
externaldata(TenantId:string, AttachmentCount:int, ConfidenceLevel:string, Connectors:string, DetectionMethods:string, DeliveryAction:string, DeliveryLocation:string, EmailClusterId:long, EmailDirection:string, EmailLanguage:string, EmailAction:string, EmailActionPolicy:string, EmailActionPolicyGuid:string, OrgLevelAction:string, OrgLevelPolicy:string, InternetMessageId:string, NetworkMessageId:string, RecipientEmailAddress:string, RecipientObjectId:string, ReportId:string, SenderDisplayName:string, SenderObjectId:string, SenderIPv4:string, SenderIPv6:string, SenderMailFromAddress:string, SenderMailFromDomain:string, Subject:string, ThreatTypes:string, ThreatNames:string, TimeGenerated:datetime, Timestamp:datetime, UrlCount:int, UserLevelAction:string, UserLevelPolicy:string, SourceSystem:string, Type:string)
[
h@"https://siempipestorage.blob.core.windows.net/am-emailevents/WorkspaceResourceId=/subscriptions/f77542d9-6668-/resourcegroups/rgoperations/providers/microsoft.operationalinsights/workspaces/azulabs/y=2021/m=09/d=11/h=21/m=00/PT1H.json?sv=2019-07-07&sr=b&sig=&se=2021-09-14T03%3A29%3A16Z&sp=r",
h@"https://siempipestorage.blob.core.windows.net/am-emailevents/WorkspaceResourceId=/subscriptions/f77542d9-6668-/resourcegroups/rgoperations/providers/microsoft.operationalinsights/workspaces/azulabs/y=2021/m=09/d=12/h=06/m=00/PT1H.json?sv=2019-07-07&sr=b&sig=&se=2021-09-14T03%3A29%3A16Z&sp=r",
h@"https://siempipestorage.blob.core.windows.net/am-emailevents/WorkspaceResourceId=/subscriptions/f77542d9-6668-/resourcegroups/rgoperations/providers/microsoft.operationalinsights/workspaces/azulabs/y=2021/m=09/d=12/h=11/m=00/PT1H.json?sv=2019-07-07&sr=b&sig=%&se=2021-09-14T03%3A29%3A16Z&sp=r"
]
with(format="json")
```

 ## Usage
[Animated Usage of Script](https://swiftsolvesblog.blob.core.windows.net/images/genstoragectxkql-ps1-animation.gif)