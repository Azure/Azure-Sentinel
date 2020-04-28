---
page_type: sample
products:
- office-365
- Sentinel
languages:
- powershellcore
extensions:
  contentType: samples
  createdDate: 4/2/2020 3:00:56 AM
description: "This sample can be used to process message traces from an Azure Function."
---


# Ingesting Office 365 Message Traces to Azure Sentinel

Implementing this script as part of an Azure Function will allow you to ingest Office 365 Message traces to Log Analytics.

### Prerequisites

You need to have an Azure Subscription, ability to create an Azure Function App. You need to have an account with permissions to run get-messagetrace in Office 365.
Use a dedicated account with a complex pwd stored in Azure Key Vault.

### Installing

1. Create the Azure Function App with PowerShell. It works well with a consumption plan in most scenarios.  The runtime stack should be PowerShell Core.
2. Create a new function that is timer based. Depending on your need, set it to run on a schedule like every 5 minutes. (For high load consider more often)
3. Paste the code from ingestmsgtrace.ps1 to the code window
4. Select Platform features, by clicking on the Function App name and click the Platform features tab at the top. Click Configuration under General Settings.
5. Provide the following values, if you want to add further protection store the pwd and key in Azure Key Vault. https://docs.microsoft.com/en-us/azure/app-service/app-service-key-vault-references
     - expass  (Exchange password)
     - exuser (User account with the right to run Get-messagetrace)
     - workspaceId (log analytics workspace)
     - workspaceKey (log analytics Key)
     - customLogName (table name in log analytics)
6. From the platform features open Console (CMD / Powershell), run the following command to initiate the file that will keep track of the runs (customize time).  out-file d:\home\timetracker.log -InputObject "2020-04-02T10:22:13.962Z" 

## Running the tests

Verify if the code is generating any errors when running. Verify by clicking the Function and click on Logs at the bottom of the screen.
Review on the Sentinel side if the logs are being ingested.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.