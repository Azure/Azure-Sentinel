# Add Action to All Azure Sentinel Analytics Rules
Author: Matt Burrough

**Objective:** Perform a bulk addition of an action to all Azure Sentinel rules <br/>

**Notes:**
* Does not apply actions to rules of Kind "Error"
* Skips any rules that already have an action for the specified Logic App applied

<br/>

**Prerequisites:**
The following Azure PowerShell modules are required and will be installed if missing:
* Az.Accounts
* Az.SecurityInsights
<br/><br/>

#### Script Parameters
The script will prompt you for the following parameter values:
* *subscriptionId* - the subscription ID where your Azure Sentinel workspace resides in
* *sentinelRG* - the Azure resource group name where the Azure Sentinel workspace resides in
* *workspaceName* - the name of the Azure Sentinel workspace
* *logicAppName* - the name of the Logic App to use for the rules
* *logicAppRG* - the Azure resource group name where the Logic App resides [Optional, defaults to the same resource group as specified for Sentinel]
* *triggerName* - name of the Logic App trigger [Optional, if not specified, the default trigger name "When_a_response_to_an_Azure_Sentinel_alert_is_triggered" is used]
<br/><br/>

#### Running the script 
After your have downloaded the sample script, you can run the script with parameters as follows:
```powershell
.\addAzureSentinelAlertAction.ps1 -subscriptionId "0c8c4515-d563-4eb7-96fa-a5a2b8f6806c" -sentinelRG "mySentinelRG" -workspaceName "Sentinelworkspace" -logicAppName "SentinelAlerts"
```
