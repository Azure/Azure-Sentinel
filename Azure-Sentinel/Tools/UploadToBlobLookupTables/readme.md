# Deploy Function App for Uploading Files to Azure Blob Storage
This function app will download files from Urls and upload to Blob storage for centralized allowedlist or enrichment.

## Architecture
![Diagram](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/Images/azurefunction-uploadtoblob.png)

## Deployment and Configuration

### Deploy the Function App
There are 2 deployment Options.

#### 1: Deploy via Azure ARM Template
1.  Deploy the template.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FUploadToBlobLookupTables%2Fazuredeploy.json)

#### 2: Deploy via VS Code
Note: You will need to prepare VS code for Azure function development.  See https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-powershell#prerequisites
1. Download the [Zip](https://github.com/Azure/Azure-Sentinel/blob/master/Tools/UploadToBlobLookupTables/UploadToBlobLookupTables.zip?raw=true)  file of the Azure Function app from Github.
2. Extract to location on your machine.
3. Open VS Code
4. Click File -> Open Folder
5. Select the Top folder from extracted files.
6. Type Crtl+Shift+P.
7. Click Azure Functions: Deploy to function app.  You maybe asked to sign in to azure.
8. Click Create New function app in Azure (advanced)
9. Provide a unique name like "uploadToBlobLookupTables".  Press Enter
10. Click Windows
11. Click Consumption
12. Click PowerShell
13. Click Create new Resource Group
14. Press enter to accept the name
15. Click Create a new storage Account
16. Press enter to accept the name
17. Click Create new Application Insights resource
18. Press enter to accept the name
19. Pick a location
20. Deployment will begin.
21. Wait for the deployment to complete, then click upload settings in the bottom right
22. Click yes to all to upload.
23. Go to the Azure Portal.
24. Go to the resource group that was created.  Click the Function.
25. Click Stop.
26. Click Platform Features Tab.
27. Click Identity
28. Click On under system assigned.  Click Save.  Click Yes.
