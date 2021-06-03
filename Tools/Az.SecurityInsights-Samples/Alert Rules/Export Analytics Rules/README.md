# Export Azure Sentinel Analytics Rules
Author: Tiander Turpijn - Microsoft

**Objective:** Export Azure Sentinel analytics rules to a local folder <br/>

**Current supported rule kinds:**
* Scheduled
* Fusion
* MicrosoftSecurityIncidentCreation

> Note: ML Behavior Analytics rules are during this preview not supported, but will be supported upon GA

<br/>

**Prerequisites:**
The following Azure PowerShell modules are required and will be installed if missing:
* Az.Accounts
* Az.SecurityInsights
<br/><br/>

#### Script Parameters
The script will prompt you for the following parameter values:
* *subscriptionId* - the subscription ID where your Azure Sentinel workspace resides in
* *resourceGroupName* - the Azure resource group name where the Azure Sentinel workspace resides in
* *workspaceName* - the name of the Azure Sentinel workspace
* *ruleExportPath* - the name of the folder where your exported rules files will be stored, for example **c:\SentinelRules\Export** if the folder does not exist, the script will create it for you
<br/><br/>

#### Running the script 
After your have downloaded the sample script, you can run the script with parameters as follows:
```powershell
.\exportAzureSentinelRules.ps1 -subscriptionId "382b2a53-c53c-4092-8d4a-7210f6a44a0c" -resourceGroupName "mySentinelRG" -workspaceName "Sentinelworkspace" -ruleExportPath "C:\SentinelRules\Export"
```




