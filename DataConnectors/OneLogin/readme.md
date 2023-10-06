# Deploy a Function App for collecting OneLogin data into Azure Sentinel

This function app will listen for **OneLogin API** events leveraging OneLogin Webhooks and write them to a Log Analytics workspace on arrival.

## Deploy the Function App Automatically

The easiest way is via the provided ARM templates

### Deploy via Azure ARM Template

1. Deploy the template

	[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FDataConnectors%2FOneLogin%2Fazuredeploy.json)

2. After you completed the ARM template Deployment [Configure your One Login WebHook](#configure-your-one-login-webhook)

## Configure your One Login WebHook

You need to configure your OneLogin account to send events to your Function App. To do this go to https://Your-Tenant-Name.onelogin.com and log in with a user who has admin access to your OneLogin account.

1. Select **Developer** in the top right hand corner

2. Select **Webhooks** on the drop-down.

3. Press **New Webhooks**.

4. Select **Event Webhook for log management**.

5. Under the **New Broadcaster** Window gave it friendly name such as **send-to-sentinel**, select in the format **JSON array**.

6. Open a new browser tab and navigate to your **function app** > **Functions** > **Select the Function Name (OneLogin)**

8. Select **Get Function URL** from the top bar > Copy the function URL which contains the function key

	* Ensure that default (function key) is selected in the dropdown box

9. In the **Listener URL** paste the function url

10. For the **Format** select **JSON Array**

10. Click **Save** and wait for the new broadcast channel to be healthy and green.

If successfully deployed you should start to see events appear in your Azure Sentinel workspace as soon as they are generated from OneLogin to the custom table OneLogin_CL. An easy method to generate new events is to initiate a new login request to OneLogin. The first run may take up to 5 minutes before events appear in Sentinel.

## Deploy the Function App Manually

### Step 1 - Deploy via VS Code

Note: You will need to prepare VS code for Azure function development. See https://docs.microsoft.com/azure/azure-functions/functions-create-first-function-powershell#prerequisites


1. Download the [Zip](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/OneLogin/OneLogin_logs_template.zip?raw=true) file of the Azure Funciton app from Github.

2. Extract to a location on your local host.

3. Open VS Code.

4. Click File -> Open Folder.

5. Select the top level folder from extracted files.

6. Type Crtl+Shift+P.

7. Click Azure Functions: Deploy to function app. You maybe asked to sign in to Azure.

8. Click Create New function app in Azure (advanced).

9. Provide a unique name like "OneLoginEvents". Press Enter

10. Click Windows

11. Click Consumption

12. Click PowerShell

13. Click Create new Resource Group

14. Press enter to accept the name

15. Click Create a new storage Account

16. Press enter to accept the name

17. Click Create new Application Insights resource

18. Press enter to accept the name

19. Pick a location to deploy in

20. Deployment will begin

21. Wait for the deployment to complete, then click upload settings in the bottom right

22. Click yes to all to upload

23. Go to the Azure Portal

24. Go to the resource group that was created. Click the Function

26. Click Identity under Settings > Configuration

28. Click On under system assigned. Click Save. Click Yes

  

### Step 2 - Create a Key Vault

1. Go to the Azure Portal.

2. Go to the resource group that was created. Click Add.

3. Type Key Vault.

4. Create a Key vault.

5. Go to the resource created.

6. Click **Access Policies**.

7. Select **Azure role-based access control** under **Permission Model**

8. Click **Save**

9. Click **Access Control (IAM)**

10. Click the **Add** button > **Add role assignment**

11. In the role lists select **Key Vault Reader**

12. Click **Next**.

13. Select **Managed Identity** under **Assign access to**

14. Click Select **Memebers**

15. Select the correct Subscription and Function App under the Managed identity drop down

16. Select **OneLoginYourFunctionName** function app managed identity that was created

17. Click **Select**

18. Click **Review + assign**

  

### Step 3 - Configure Settings for the Function

1. Go to the Azure Portal

2. Go to the resource group that was created. Click the Function

3. Click **Configuration** under **Settings**

4. Click **edit** next to **workspaceKey**

6. Update the value using the below format

	* @Microsoft.KeyVault(VaultName=oneloginlogs<name>;SecretName=workspaceKey)

7. Click **Ok**

8. Click **edit** next to **workspaceId**

9. Update the value with your Sentinel Workspace Id

10. Click **Ok**

11. Click **Save**

12. After you completed the manual Deployment [Configure your One Login WebHook](#configure-your-one-login-webhook)

If you run into issues there are a number of options for [functions monitoring](https://docs.microsoft.com/azure/azure-functions/functions-monitoring?tabs=cmd) and [functions deugging powershell](https://docs.microsoft.com/azure/azure-functions/functions-debug-powershell-local) your Function App.