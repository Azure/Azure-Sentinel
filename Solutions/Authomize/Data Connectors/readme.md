## Instructions for Quick Deployment
You will need the following before you start this installation:
- Access to a keyvault with the ability to deploy secrets, note that we suggest authomize as the name, but you can use an existing vault or create a new one with a different name.
- Access to App Registration under AAD (For more secure method you can optionally setup an ID for the function you deploy)
- Access to be able to create azure app functions from your azure portal
- Access to an azure storage account - by default this applocation will create a small table using AzureWebJobsStorage connection string

### Get the Tokens to be stored in Secrets
1. Get an Authomize Token from your tenant
     - ```authomizeToken``` - this is the Token generated in your Authomize tenant. Go to the configurations page, click API Tokens and select a Platform Token. Save this token in a safe place to be used later, ensure you save it as pure text with no formatting.
2. Go to your Logs Analytics Workspace
     - ```CustomerID``` - this is the workspace id in your Logs analytics workspace.
     - ```sharedKey``` - this is the Logs analytics workspace. Go to the configurations page.

### Creating Secrets

1. You will now create the secrets that the Authomize connector for Azure Sentinel will use.
     - Create a secret for the following tokens inserting the value that you saved previously. Use the exact naming convention as outlined here:
          - ```authomizeToken```
          - ```CustomerID```
          - ```sharedKey```
     - This is an Example using Azure CLI to create or you can do this from within the Portal
     ```
          ** First create the vault to use
          az keyvault create --name authomize --resource-group <your resource group name> --location <your location eg eastus>

          ** Now create each of the secrets
          az keyvault secret set --vault-name authomize --name authomizeToken --value "<Enter the Token You Saved from above>"
          az keyvault secret set --vault-name authomize --name CustomerID --value "<Enter the ID You Saved from above>"
          az keyvault secret set --vault-name authomize --name sharedKey --value "<Enter the shared key You Saved from above>"
     ```
- NOTE: Please remember to delete and do not store any of these values anywhere else.

2. At this point, please get your vault URI, it will be needed later in the configuration of the application. You can find it under overview within the keyvault that you created. Here is an example ```https://authomizexxx.vaultxxx.azure.net/```

### Creating your Application within Azure AD
1. Go to Microsoft Azure Default Directory and Create an App Registration
     - On the left menu click on App registrations
     - Click on ```New Registration```
     - Give it a meaning name such as AuthomizeAccess
     - Leave the default settings unless you are sure about changing, then click ```Register```
     - Click on ```Add a certificate or secret```
     - Click ```New Client Secrets```
     - Give a meaningful description and leave defaults
     - Copy the ```Value``` and leave in safe place as we will need this later

### Ensure new principal has access to Kay Vauly Secrets
1. Go to the Key Vault you created previously with the secrets
     - Once you have access click on the left ```Access policies```
     - Click ```create```
     - Under Secret permissions click ```Get``` and ```List``` then click ```next```
     - Find your service principal you defind before e.g. AuthomizeAccess
     - Then click ```next``` and ```Create``` when you get to the review screen

### Deploy the Azure Function app
1. We will do this through the cli, you will need access to the authomizeconnector.zip file and authorization to deploy
     - go to the directory where you have stored the authomizeconnector.zip file
     - Login to you tenant and ensure you have a consumption plan created for 
     - Run the following commands to setup and deploy the application
     ```
     **Note: we are using a consumption plan in this example. I have assumed names for --name and --storage-account

     az functionapp create \
          --resource-group <your resource-group> \
          --name authomize-sentinel-connect \
          --storage-account authomize \
          --consumption-plan-location "EastUS" \
          --runtime python \
          --runtime-version 3.10 \
          --functions-version 4 \
          --os-type Linux
               
     ** From the directory wehere the ZIP file is located run
     az webapp deployment source config-zip \
          --resource-group <your resource-group>  \
          --name authomize-sentinel-connect \
          --src ./authomizeconnector.zip
     
     ```
2. Create the Function App configurations using the CLI (you can do this in the portal if you wish)
     - You'll need to collect the following information some of this you have already collected
          - Tenant ID: collect the Tenant ID, you can find this in the overview of the default Azure AD environment 
          - Application (Client) ID: this can be found by searching for the app registration you did before, find the display name and it is listed to the right
          - Client Secret: this is the ```Value``` that you created before with the app registration. Look at the above section "Creating your Application within Azure AD", you would have saved these values to be used later
     - Following are the CLI commands to be used to create the configuration for the Function App
     ```
     az functionapp config appsettings set \
          --name authomize-sentinel-connect \
          --resource-group keyvaulttests \
          --settings AZURE_CLIENT_ID="<Application ID as indicated above>"
     az functionapp config appsettings set \
          --name authomize-sentinel-connect \ 
          --resource-group keyvaulttests \
          --settings AZURE_TENANT_ID="<Tenant ID as stated above>"
     az functionapp config appsettings set \
          --name authomize-sentinel-connect \
          --resource-group keyvaulttests \
          --settings AZURE_CLIENT_SECRET="<Client Secret from above>"     
     ```

     - Finally we need to set the URI for the Vault you created previously: 
     ```az functionapp config appsettings set --name authomize-sentinel-connect --resource-group keyvaulttests --settings VAULT_URL="https://exampleVault.vault.azure.net/"```

3. Special call out note - PLEASE READ
     - This application will use the ```AzureWebJobsStorage``` setting which is created by default. The application will create 1 table with the name of ```authomizeDate```. The application will check every time it runs to see if this table exists and will only store a date here. Every time the application executes it will update the date. It uses this date to know when it last collected data from Authomize. If this date is deleted, the application on its next run will collect all open Incidents until the current date. You can also manually create the date time and field yourself if for instance you only want to have the last 3 months of data collected from Authomize.

## Care and Feeding
1. Monitoring the application and expected behavior
     - Viewing the connector monitor screen you should see an output similar to this. This is an example of a single execution with no data being collected:
     ```
     2023-09-05 01:50:00.852       Table already exists                              Error
     2023-09-05 01:50:00.873       Entity already exists                             Error
     2023-09-05 01:50:00.979       Status: Started processing.                       Information
     2023-09-05 01:50:00.979       INFO: --Processing-- [1]                          Information
     2023-09-05 01:50:01.391       Status: Stopped processing.                       Information
     2023-09-05 01:50:01.391       INFO: No data to send, skipping process steps.    Information
     ```
     
     - NOTE: the Error statements above are by design and is part of the checking process for the Table and Fields.

     - When there is data to be processed, you will see multiple INFO statements like the following:
     ```
     2023-09-04T20:50:04Z   [Information]   Data sent to Sentinel.
     2023-09-04T20:50:04Z   [Information]   INFO: --Processing-- [4]
     2023-09-04T20:50:05Z   [Information]   Data sent to Sentinel.
     2023-09-04T20:50:05Z   [Information]   INFO: --Processing-- [5]
     2023-09-04T20:50:05Z   [Information]   Data sent to Sentinel.
     2023-09-04T20:50:05Z   [Information]   INFO: --Processing-- [6]
     2023-09-04T20:50:06Z   [Information]   Data sent to Sentinel.
     2023-09-04T20:50:06Z   [Information]   INFO: --Processing-- [7]
     2023-09-04T20:50:07Z   [Information]   Data sent to Sentinel.
     2023-09-04T20:50:07Z   [Information]   INFO: --Processing-- [8]
     2023-09-04T20:50:07Z   [Information]   Data sent to Sentinel.
     2023-09-04T20:50:07Z   [Information]   INFO: --Processing-- [9]
     ```

     - Regularly check the logs for errors or issues, such as certificates expiring or being deleted from any of the systems being used.