---
name: asim-parser-la-deployer
description: Gets the ASIM parser of interest and deploys it to the customer's LA workspace.
---

# Context
You are responsible for deploying the ASIM parser to the customer's LA workspace. This involves using the az cli to deploy the parser and ensuring that it is properly configured to work with the customer's environment.

## Requirements
You will use the az cli to deploy the ASIM parser to the customer's LA workspace. You will need the following information:
- **Workspace ID** — If you do not have this from the customer or this skill was not called by the `asim-parser-creator-orchestrator` skill, ask the customer for it.
- **ASIM parser files to deploy** — Typically two files: the parameter-less parser (`ASim<Schema><Vendor><Product>.kql`) and the parameterized parser (`vim<Schema><Vendor><Product>.kql`). Each file requires its own deployment.

## Step 1: Verify Azure CLI authentication
Run `az account show` to verify the user is authenticated. If this fails, ask the user to run `az login` before continuing.

## Step 2: Query for workspace information
Use the following CLI command to get the workspace name, resource group, and location needed for deployment:
```powershell
az monitor log-analytics workspace list --query "[?customerId=='<workspaceId>'].{name:name, resourceGroup:resourceGroup, location:location, id:id}" -o json 2>&1
```

## Step 3: Set up parser and ARM deployment template
Before embedding the KQL query into the ARM template, escape the following special characters in the query string:
- `\` → `\\` (backslashes)
- `"` → `\"` (double quotes)
- Newlines → `\n` (replace line breaks with literal `\n`)
- Tabs → `\t` (replace tabs with literal `\t`)

Save the ARM template JSON file alongside the parser `.kql` files (e.g., `deploy_<parserName>.json`).

Repeat this process for **each** parser file. The ARM template should contain a resource entry for each parser. Note that the `functionParameters` value will differ between the two parsers — the parameterized version (`vim...`) includes additional filter parameters defined by the schema.

An example ARM template with two parser resources:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-08-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "Workspace": {
      "type": "string",
      "metadata": {
        "description": "The Microsoft Sentinel workspace into which the function will be deployed."
      }
    },
    "WorkspaceRegion": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]",
      "metadata": {
        "description": "The region of the selected workspace."
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
      "apiVersion": "2020-08-01",
      "name": "[concat(parameters('Workspace'), '/<name of the parameter-less ASIM parser>')]",
      "location": "[parameters('WorkspaceRegion')]",
      "properties": {
        "etag": "*",
        "displayName": "<name of the parameter-less ASIM parser>",
        "category": "ASIM",
        "FunctionAlias": "<name of the parameter-less ASIM parser>",
        "query": "<escaped KQL query>",
        "version": 1,
        "functionParameters": "disabled:bool=false,pack:bool=false"
      }
    },
    {
      "type": "Microsoft.OperationalInsights/workspaces/savedSearches",
      "apiVersion": "2020-08-01",
      "name": "[concat(parameters('Workspace'), '/<name of the parameterized ASIM parser>')]",
      "location": "[parameters('WorkspaceRegion')]",
      "properties": {
        "etag": "*",
        "displayName": "<name of the parameterized ASIM parser>",
        "category": "ASIM",
        "FunctionAlias": "<name of the parameterized ASIM parser>",
        "query": "<escaped KQL query>",
        "version": 1,
        "functionParameters": "<parameters as defined by the schema, including disabled:bool=false,pack:bool=false>"
      }
    }
  ]
}
```

## Step 4: Deploy the parser
Deploy the ARM template using the following command:

```powershell
az deployment group create --resource-group <resourceGroup> --template-file <templateFilePath> --parameters Workspace=<workspaceName> WorkspaceRegion=<location>
```

If the deployment fails:
1. Check the error message for details (common issues: authentication errors, incorrect resource group, KQL escaping problems).
2. Fix the identified issue (re-escape the query, correct the resource group, etc.).
3. Retry the deployment.

## Step 5: Test the parser
Use the `log-analytics-workspace-queryer` skill to verify the parser works in the customer's LA workspace. Run the following query for each deployed parser:

```kql
<FunctionAlias>() | take 10
```

If the query returns results, the deployment was successful.