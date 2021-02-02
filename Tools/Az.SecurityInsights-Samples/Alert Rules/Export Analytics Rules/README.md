# Export Azure Sentinel Analytics Rules

**Objective:** Export Analytics Rules to a local folder <br/>

**Current supported rule kinds:**
* Scheduled
* Fusion
* MicrosoftSecurityIncidentCreation

> Note: ML Behavior Analytics rules are during this preview not supported, but will be supported upon GA

<br/>

**Prerequisites:**
* Az.Accounts module
* Az.SecurityInsights module
* Azure Sentinel Reader permissions


**Required script values to update:**
* Azure Subscription Id
* Azure Resource Group name (where the Azure Sentinel workspace resides in)
* Workspace name (the name of the Azure Sentinel workspace)
* Target folder for the exported rules <br/>
<br/>



```powershell
# Sample script to export Azure Sentinel rules
# Author: Tiander Turpijn - Microsoft
# Dependencies: Az.Accounts and Az.SecurityInsights PowerShell modules imported,
# please download from https://www.powershellgallery.com
#
# ToDo:
# 1. Login to Azure
# 2. Provide values for your Azure Sentinel Resource Group and Workspace
# 3. Provide a name for your rule export folder

$ErrorActionPreference = "Stop"

# *** Values to update ***
# Provide your Azure Sentinel connection settings
$subscriptionId = "<yourAzureSubscriptionId>"
$SentinelConnection = @{
    ResourceGroupName = "<yourResourceGroupName>"  #your Resource Group name where your workspace is located
    WorkspaceName = "<yourSentinelWorkspaceName>"  #your Sentinel Workspace name
}
# Configure your rule export folder
$ruleExportPath = "C:\SentinelRules\Export\" # specify your rule export folder

# Login to Azure and selecting your Azure Sentinel subscription -  make sure you have installed the Az.Accounts module
Login-AzAccount
Set-AzContext -SubscriptionId $subscriptionId

# Testing your Azure connection
$azureConnection = Get-AzContext
If([string]::IsNullOrEmpty($azureConnection.Account)) {            
    Write-Host ("You are not connected to Azure, please login") -ForegroundColor Red
    break
} 

# Create folder if it does not exist
if (!(Test-Path -Path $ruleExportPath))
{
    Write-Host ("Folder " + $ruleExportPath + " does not exist, creating the folder for you....") -ForegroundColor Red
    New-Item -itemType Directory -Path $ruleExportPath
}

# Export Scheduled Rules
try {
    $rules = Get-AzSentinelAlertRule @SentinelConnection | Where-Object {$_.Kind -eq "Scheduled"} 
    Write-Host ("Exporting " + $rules.count + " Scheduled rules...") -ForegroundColor Yellow
    $rules | ConvertTo-Json -Depth 15 | Out-File ($myExportPath + "Scheduled.json") -Force
}
catch {
    Write-Host "Either your Azure connection is invalid or your Azure Sentinel settings are incorrect" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    break
}


# Export Fusion Rules
try {
    $rules = Get-AzSentinelAlertRule @SentinelConnection | Where-Object {$_.Kind -eq "Fusion"} 
    Write-Host ("Exporting " + $rules.count + " Fusion rules...") -ForegroundColor Yellow
    $rules | ConvertTo-Json -Depth 15 | Out-File ($myExportPath + "Fusion.json") -Force
}
catch {
    Write-Host "Either your Azure connection is invalid or your Azure Sentinel settings are incorrect" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    break
}

# Export MicrosoftSecurityIncidentCreation Rules
try {
    $rules = Get-AzSentinelAlertRule @SentinelConnection | Where-Object {$_.Kind -eq "MicrosoftSecurityIncidentCreation"} 
    Write-Host ("Exporting " + $rules.count + " MicrosoftSecurityIncidentCreation rules...") -ForegroundColor Yellow
    $rules | ConvertTo-Json -Depth 15 | Out-File ($myExportPath + "MicrosoftSecurityIncidentCreation.json") -Force
}
catch {
    Write-Host "Either your Azure connection is invalid or your Azure Sentinel settings are incorrect" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    break
}

Write-Host ("Azure Analytics Rules are exported to " + $ruleExportPath) -ForegroundColor Yellow
```



