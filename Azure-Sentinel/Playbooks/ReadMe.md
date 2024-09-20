<img src="logic_app_logo.png" alt="LogicApps Logo" width="350" height="200">

## About
This repo contains sample security playbooks for security automation, orchestration and response (SOAR). Each folder contains a security playbook ARM template that uses Microsoft Sentinel trigger.

## Instructions for deploying a custom template
After selecting a playbook, in the Azure portal:
1. Search for deploy a custom template
2. Click build your own template in the editor
3. Paste the contents from the GitHub playbook 
4. Click **Save**
5. Fill in needed data and click **Purchase**

Once deployment is complete, you will need to authorize each connection.
1. Click the Microsoft Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections
 * For Azure Log Analytics Data Collector,  you will need to add the workspace ID and Key
You can now edit the playbook in Logic apps.

## Instructions for templatizing a playbook  
## Option 1: Azure Logic App/Playbook ARM Template Generator  
1. Download tool and run the PowerShell script  
   [![Download](./Download.png)](https://aka.ms/Playbook-ARM-Template-Generator)  
   
2. Extract the folder and open "Playbook_ARM_Template_Generator.ps1" either in Visual Studio Code/Windows PowerShell/PowerShell Core

   **Note**  
   The script runs from the user's machine. You must allow PowerShell script execution. To do so, run the following command:
   
   ```PowerShell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass  
   ```  
3. Script prompts you to enter your Azure Tenant Id

4. You are prompted to authenticate with credentials, once the user is authenticated, you will be prompted to choose 
	- Subscription	
	- Playbooks

5.	After selecting playbooks, script prompts to select location on your local drive to save ARM Template  
   > Note: Tool converts microsoftsentinel connections to MSI during export  

## Option 2: Manual  

Once you have created a playbook that you want to export to share, go to the Logic App resource in Azure.
> Note: this is the generic instructions there may be other steps depending how complex or what connectors are used for the playbook.
1. Click **Export Template** from the resource menu in Azure Portal.
2. Copy the contents of the template.
3. Using VS code, create a JSON file with the name "azuredeploy.json".
4. Paste the code into the new file.
5. In the parameters section, you can remove all parameters and add the following minimum fields. Users can edit the parameters when deploying your template. You can add more parameters based on your playbook requirements.
```json
    "parameters": {
        "PlaybookName": {
            "defaultValue": "<PlaybookName>",
            "type": "string"
        },
        "UserName": {
            "defaultValue": "<username>@<domain>",
            "type": "string"
        }
    },
```
* Playbook name and username are minimum requirements that will be used for the connections.
6. In the variables section, create a variable for each connection the playbook is using. 
* To construct a string variable, use this following snippet. Make sure to replace the `connectorname` with actual name of the connector.

```
    [concat('<connectorname>-', parameters('PlaybookName'))]
```

* For example, if you are using Azure Active Directory and Microsoft Sentinel connections in the playbook, then create two variables with actual connection names. The variables will be the connection names.  Here we are creating a connection name using the connection (AzureAD) and "-" and the playbook name.

```json
    "variables": {
        "AzureADConnectionName": "[concat('azuread-', parameters('PlaybookName'))]",
        "AzureSentinelConnectionName": "[concat('azuresentinel-', parameters('PlaybookName'))]"
    },
```

7. Next, you will need to add resources to be created for each connection.
```json
   "resources": [
        {
            "type": "Microsoft.Web/connections",
            "apiVersion": "2016-06-01",
            "name": "[variables('AzureADConnectionName')]",
            "location": "[resourceGroup().location]",
            "properties": {
                "displayName": "[parameters('UserName')]",
                "customParameterValues": {},
                "api": {
                    "id": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/azuread')]"
                }
            }
        },
```
* The `name` is using the variable we created.  
* The `location` is using the resource group that was selected as part of the deployment.  
* The `displayname` is using the Username parameter. 
* Lastly, you can build the string for the `id` using strings plus properties of the subscription and resource group. 
* Repeat for each connection needed.

8. In the `Microsoft.Logic/workflows` resource under `parameters / $connections`, there will be a `value` for each connection.  You will need to update each like the following.
```json
"parameters": {
                    "$connections": {
                        "value": {
                            "azuread": {
                                "connectionId": "[resourceId('Microsoft.Web/connections', variables('AzureADConnectionName'))]",
                                "connectionName": "[variables('AzureADConnectionName')]",
                                "id": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/azuread')]"
                            },
                            "azuresentinel": {
                                "connectionId": "[resourceId('Microsoft.Web/connections', variables('AzureSentinelConnectionName'))]",
                                "connectionName": "[variables('AzureSentinelConnectionName')]",
                                "id": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/azuresentinel')]"
                            }
                        }
                    }
                }

```
* The `connectionId` will use a string and variable.  
* The `connectionName` is the variable.  
* The `id` is the string we used early for the id when creating the resource.

9. In the `Microsoft.Logic/workflows` resource, you will also need the `dependsOn` field, which is a list of `resourceId`. The string for each `resourceId` is constructed using this snippet, followed by an example which contains Azure AD and Azure Sentinel connections.

```
    [resourceId('Microsoft.Web/connections', <ConnectionVariableName>)]
``` 

```
    "dependsOn": [
        "[resourceId('Microsoft.Web/connections', variables('AzureADConnectionName'))]",
        "[resourceId('Microsoft.Web/connections', variables('AzureSentinelConnectionName'))]"
    ]
```

10. Save the JSON.
11. Create a Readme.md file with a brief description of the playbook.
12. Test deployment of your template following [Instructions for deploying a custom template](#Instructions-for-deploying-a-custom-template). Make sure the deployment succeeds.
13. If you need samples of a playbook template, refer to an existing playbooks' azuredeploy.json sample file in the repo.
14. Contribute the playbook template to the repository.

# Suggestions and feedback
We value your feedback. Let us know if you run into any problems or share your suggestions and feedback by sending email to AzureSentinel@microsoft.com
