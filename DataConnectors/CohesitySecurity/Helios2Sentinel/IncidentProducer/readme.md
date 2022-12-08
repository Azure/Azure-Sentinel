# IncidentProducer Azure Function
This function retrieves ransomware alerts from Cohesity DataHawk and lands them in the queue.

## Deployment Prerequisites
1. Get your Helios API key by following the steps:
* Go to the Cohesity Helios [login page](https://helios.cohesity.com/login).
* Enter your credentials and select _Log In_. The _Summary_ page is displayed.
* Navigate to _Settings > Access Management_. The _Users_ tab is displayed.
* Select _Add API Key_. The API Key Details is displayed.
* Enter a name for the API key.
* Select _Save_. The API Key Token is displayed.
* Put this key to [IncidentProducer/local.settings.json](https://raw.githubusercontent.com/cohesity/Azure-Sentinel/CohesitySecurity.internal/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentProducer/local.settings.json)
`"Values": {
  ...
    "apiKey": "33e44eac-ce99-46df-7f4e-9ac39446a66f",
  ...
  }
`
2. Create your Sentinel [workspace](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/microsoft.securityinsightsarg%2Fsentinel) and save the name in [IncidentProducer/local.settings.json](https://raw.githubusercontent.com/cohesity/Azure-Sentinel/CohesitySecurity.internal/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentProducer/local.settings.json)
`
"Values": {
...
    "workspace": "my-workspace",
...
}
`    
4. [Register](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps) a client application in Azure Active Directory with the Contributor privileges ([steps](https://learn.microsoft.com/en-us/azure/healthcare-apis/register-application)).
* Save _Application (client) ID_, _Directory (tenant) ID_ and _Secret Value_ in [IncidentConsumer/local.settings.json](https://raw.githubusercontent.com/cohesity/Azure-Sentinel/CohesitySecurity.internal/DataConnectors/CohesitySecurity/Helios2Sentinel/IncidentProducer/local.settings.json)
`   
"Values": {
...
    "TenantId": "fa3d34bc-81d6-4a79-ade7-175d3c33c77e",
    "ClientId": "cf58a81b-bfc5-4942-9f5e-9cdc8d1d119c",
    "ClientKey": "Xzf8Q~SxY28H4UA6fd70bt39DB92xoweNC_RRc_x",
...
}
`
5. Create a new queue in [Azure Storage Accounts](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Storage%2FStorageAccounts) ([steps](https://learn.microsoft.com/en-us/azure/storage/queues/storage-quickstart-queues-portal)).
* Save the connection string
`
"Values": {
...
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "apiKey": "11111111-2222-3333-4444-555555555555",
        "startDaysAgo": "-30",
        "connectStr": "your azure redis cache connection string",
        "workspace": "your instance name",
        "FUNCTIONS_WORKER_RUNTIME": "dotnet"
    }
`    
## Deployment instructions
1. Deploy the Custom Connector by clicking on "Deploy to Azure" button. This will take you to deploying an ARM Template wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template)


