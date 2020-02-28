![alt text](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/Logic_Apps.svg "Azure Logic Apps")
# About
This repo contains sample security playbooks for security automation, orchestration and response (SOAR)

## Each folder contains a security playbook ARM template that uses Microsoft Azure Sentinel trigger.
After selecting a playbook, in the Azure portal:
1. Search for deploy a custom template
2. Click build your own template in the editor
3. Paste the conents from the GitHub playbook 
4. Click Save
5. Fill in needed data and click purchase

Once deployment is complete, you will need to authorize each connection.
1. Click the Azure Sentinel connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections
 * For Azure Log Analytics Data Collector,  you will need to add the workspace ID and Key
You can now edit the playbook in Logic apps.

## Instructions for templatizing a playbook
Once you have created a playbook that you want to export to share, go to the Logic App resource in Azure.
> Note: this is the generic instructions there may be other steps depending how complex or what connectors are used for the playbook.
1. Click Export Template from the resource menu
2. Copy the contents of the template
3. Usig VS code, create a new JSON file
4. Paste the code into the new file
5. In the parameters section, you can remove all parameters and add the following:
```json
    "parameters": {
        "PlaybookName": {
            "defaultValue": "PlaybookName",
            "type": "string"
        },
        "UserName": {
            "defaultValue": "<username>@<domain>",
            "type": "string"
        }
    },
```
* You need a playbook name and username that will be used for the connections.
6. In the variables section, you will need to create a variable for each connection the playbook is using like,
```json
    "variables": {
        "AzureADConnectionName": "[concat('azuread-', parameters('PlaybookName'))]",
        "AzureSentinelConnectionName": "[concat('azuresentinel-', parameters('PlaybookName'))]"
    },
```
* The variables will be the connection names.  Here we are creating a connection name using the connection (AzureAD) and "-" and the playbook name.
7. Next,, you will need to add resources to be created for each connection.
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
* The name is using the variable we created.  The location is using the resource group that was selected as part of the deployment.  The displayname is using the Username parameter. Lastly, you can build the string for the id using strings plus properties of the subscription and resource group. Repeat for each connection needed.
8. In the `Microsoft.Logic/workflows` resource under `paramters / $connections`, there will be a `value` for each connection.  You will need to update each like the following.
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
* The connectionId will use a string and variable.  The Connection name is the variable/.  The id is the string we used early for the id when creating the resource.
9.  Save the JSON and contribute to the repository.

# Suggestions and feedback
We value your feedback. Let us know if you run into any problems or share your suggestions and feedback by sending email to AzureSentinel@microsoft.com
