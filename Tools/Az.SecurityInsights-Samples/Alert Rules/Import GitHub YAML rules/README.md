# Import GitHub YAML Analytics Rules
*Author: Tiander Turpijn - Microsoft*
<br/><br/>

**Objective:** Import GitHub YAML rules to an existing Azure Sentinel Workspace <br/>

This sample script allows you to import Azure Sentinel detection rules from GitHub, which are in the format of YAML.<br/>
The most efficient way is to clone the Azure Sentinel GitHub repo so that you have all the rules locally. You can leverage the import sections to import a whole YAML folder<br/>
This sample however is focused on importing specific YAML type detection rules which you specify in the sample script.<br/>
The script will download your YAML files of choice (to be defined in the script's array) and will import these in your Azure Sentinel workspace.

#### Credits
This sample script uses a community PowerShell module called [powershell-yaml](https://www.powershellgallery.com/packages/powershell-yaml/0.4.2) authored by Gabriel Adrian Samfira and Alessandro Pilotti.
<br/><br/>

#### Script Parameters
The script will prompt you for the following parameter values:
* *subscriptionId* - the subscription ID where your Azure Sentinel workspace resides in
* *resourceGroupName* - the Azure resource group name where the Azure Sentinel workspace resides in
* *workspaceName* - the name of the Azure Sentinel workspace
* *YAMLimportPath* - the name of the folder where your YAML files will stored and imported from, for example **C:\SentinelRules\Export**
<br/><br/>

**Prerequisites:**
The following Azure PowerShell modules are required and will be installed if missing:
* Az.Accounts
* Az.SecurityInsights
* powershell-yaml
<br/><br/>

#### Sections to update in the script
For the parameter **$YAMLimportPath**, make sure to specify the raw GitHub URL, including a "/" at the end, like this:
```powershell
 https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Detections/
```
<br/>

Update the array in the script and specify the **subfolder** and **filename**, like the sample below:
```powershell
#Array - containing GitHub detection rules yaml files download - please the subfolder as well
$GitHubYAMLRulesToExport = @(
    "W3CIISLog/HAFNIUMSuspiciousExchangeRequestPattern.yaml",
    "MultipleDataSources/HAFNIUMUmServiceSuspiciousFile.yaml",
    "SecurityEvent/HAFNIUMNewUMServiceChildProcess.yaml",
    "SecurityEvent/HAFNIUMSuspiciousIMServiceError.yaml"
)
```
<br/>

#### Running the script 
After your have downloaded the sample script, you can run the script with parameters as follows:
```powershell
.\ImportGitHubYAMLrules.ps1 -subscriptionId "12345678-c53c-4092-8d4a-12345678900c" -resourceGroupName "myResourceGroupName" -workspaceName "mySentinelworkspaceName" `
-YAMLimportPath "C:\Sentinel\YAMLimport" -GitHubPath "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Detections/"
```









