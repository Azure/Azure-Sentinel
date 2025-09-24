#Requires -Modules Az.Accounts, Az.Resources, Az.OperationalInsights
<#
.SYNOPSIS
    Deploys a second instance of Netskope Alerts and Events connector for DEV environment.

.DESCRIPTION
    This script deploys additional Netskope Alerts and Events data connector pollers 
    to support a second Netskope environment (typically DEV) in the same Microsoft Sentinel workspace.
    
    The script creates 21 individual data connector pollers with "Dev" suffix names 
    that point to the DEV Netskope environment while using the same Data Collection Rules 
    and table schemas as the existing PROD instance.

.PARAMETER ParameterFile
    Path to the JSON parameter file containing configuration values.

.PARAMETER ResourceGroupName
    Name of the resource group containing the Microsoft Sentinel workspace.

.PARAMETER WorkspaceName
    Name of the Log Analytics workspace where Microsoft Sentinel is deployed.

.PARAMETER DevOrgUrl
    DEV Netskope organization URL (e.g., company-dev.goskope.com).

.PARAMETER DevApiKey
    DEV Netskope API token for authentication.

.PARAMETER DevIndex
    Optional. Index name for DEV environment API calls. Default: "DevInstance"

.PARAMETER DataCollectionEndpoint
    Data Collection Endpoint URL from existing PROD setup.

.PARAMETER DataCollectionRuleId
    Data Collection Rule Immutable ID from existing PROD setup.

.EXAMPLE
    .\Deploy-NetskopeDevInstance.ps1 -ParameterFile ".\parameters.json"

.EXAMPLE
    .\Deploy-NetskopeDevInstance.ps1 -ResourceGroupName "rg-sentinel" -WorkspaceName "law-sentinel" -DevOrgUrl "company-dev.goskope.com" -DevApiKey "your-dev-api-key" -DataCollectionEndpoint "https://dce-xxx.eastus-1.ingest.monitor.azure.com" -DataCollectionRuleId "dcr-xxx"

.NOTES
    Author: Microsoft Sentinel Engineering
    Version: 1.0
    Requires: Az PowerShell modules, Contributor access to Sentinel workspace
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ParameterFile,

    [Parameter(Mandatory = $false)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory = $false)]
    [string]$WorkspaceName,

    [Parameter(Mandatory = $false)]
    [string]$DevOrgUrl,

    [Parameter(Mandatory = $false)]
    [securestring]$DevApiKey,

    [Parameter(Mandatory = $false)]
    [string]$DevIndex = "DevInstance",

    [Parameter(Mandatory = $false)]
    [string]$DataCollectionEndpoint,

    [Parameter(Mandatory = $false)]
    [string]$DataCollectionRuleId
)

# Function to write colored output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Load parameters from file if provided
if ($ParameterFile -and (Test-Path $ParameterFile)) {
    Write-ColorOutput Green "Loading parameters from file: $ParameterFile"
    $params = Get-Content $ParameterFile | ConvertFrom-Json
    
    if (!$ResourceGroupName) { $ResourceGroupName = $params.ResourceGroupName }
    if (!$WorkspaceName) { $WorkspaceName = $params.WorkspaceName }
    if (!$DevOrgUrl) { $DevOrgUrl = $params.DevOrgUrl }
    if (!$DevApiKey) { $DevApiKey = ConvertTo-SecureString $params.DevApiKey -AsPlainText -Force }
    if (!$DevIndex) { $DevIndex = $params.DevIndex }
    if (!$DataCollectionEndpoint) { $DataCollectionEndpoint = $params.DataCollectionEndpoint }
    if (!$DataCollectionRuleId) { $DataCollectionRuleId = $params.DataCollectionRuleId }
}

# Validate required parameters
if (!$ResourceGroupName -or !$WorkspaceName -or !$DevOrgUrl -or !$DevApiKey -or !$DataCollectionEndpoint -or !$DataCollectionRuleId) {
    Write-ColorOutput Red "ERROR: Missing required parameters. Please provide all required values or use a parameter file."
    Write-Host "Required parameters: ResourceGroupName, WorkspaceName, DevOrgUrl, DevApiKey, DataCollectionEndpoint, DataCollectionRuleId"
    exit 1
}

# Convert SecureString to plain text for API calls
$DevApiKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($DevApiKey))

Write-ColorOutput Green "=== Netskope DEV Instance Deployment Script ==="
Write-Host "Resource Group: $ResourceGroupName"
Write-Host "Workspace: $WorkspaceName"
Write-Host "DEV Org URL: $DevOrgUrl"
Write-Host "DEV Index: $DevIndex"
Write-Host ""

# Check Azure connection
try {
    $context = Get-AzContext
    if (!$context) {
        Write-ColorOutput Yellow "Not connected to Azure. Please run Connect-AzAccount first."
        Connect-AzAccount
    }
    Write-ColorOutput Green "Connected to Azure as: $($context.Account.Id)"
}
catch {
    Write-ColorOutput Red "Failed to connect to Azure: $($_.Exception.Message)"
    exit 1
}

# Verify workspace exists
try {
    $workspace = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    Write-ColorOutput Green "Found workspace: $($workspace.Name)"
}
catch {
    Write-ColorOutput Red "Workspace not found: $($_.Exception.Message)"
    exit 1
}

# Define data connector configurations
$connectorConfigs = @(
    @{ Name = "NetskopeAlertsRemediationDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/remediation"; Index = "remediation" },
    @{ Name = "NetskopeAlertsUbaDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/uba"; Index = "uba" },
    @{ Name = "NetskopeAlertsSecurityAssessmentDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/securityassessment"; Index = "securityassessment" },
    @{ Name = "NetskopeAlertsQuarantineDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/quarantine"; Index = "quarantine" },
    @{ Name = "NetskopeAlertsPolicyDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/policy"; Index = "policy" },
    @{ Name = "NetskopeAlertsMalwareDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/malware"; Index = "malware" },
    @{ Name = "NetskopeAlertsMalsiteDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/malsite"; Index = "malsite" },
    @{ Name = "NetskopeAlertsDlpDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/dlp"; Index = "dlp" },
    @{ Name = "NetskopeAlertsCtepDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/ctep"; Index = "ctep" },
    @{ Name = "NetskopeAlertsWatchlistDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/watchlist"; Index = "watchlist" },
    @{ Name = "NetskopeAlertsCompromisedCredentialsDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/compromisedcredential"; Index = "compromisedcredential" },
    @{ Name = "NetskopeAlertsContentDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/content"; Index = "content" },
    @{ Name = "NetskopeAlertsDeviceDev"; DataType = "NetskopeAlerts_CL"; Stream = "Custom-NetskopeAlerts"; Endpoint = "alerts/device"; Index = "device" },
    @{ Name = "NetskopeEventsApplicationDev"; DataType = "NetskopeEventsApplication_CL"; Stream = "Custom-NetskopeEventsApplication"; Endpoint = "events/application"; Index = "application" },
    @{ Name = "NetskopeEventsAuditDev"; DataType = "NetskopeEventsAudit_CL"; Stream = "Custom-NetskopeEventsAudit"; Endpoint = "events/audit"; Index = "audit" },
    @{ Name = "NetskopeEventsConnectionDev"; DataType = "NetskopeEventsConnection_CL"; Stream = "Custom-NetskopeEventsConnection"; Endpoint = "events/connection"; Index = "connection" },
    @{ Name = "NetskopeEventsDLPDev"; DataType = "NetskopeEventsDLP_CL"; Stream = "Custom-NetskopeEventsDLP"; Endpoint = "events/incident"; Index = "incident" },
    @{ Name = "NetskopeEventsEndpointDev"; DataType = "NetskopeEventsEndpoint_CL"; Stream = "Custom-NetskopeEventsEndpoint"; Endpoint = "events/endpoint"; Index = "endpoint" },
    @{ Name = "NetskopeEventsInfrastructureDev"; DataType = "NetskopeEventsInfrastructure_CL"; Stream = "Custom-NetskopeEventsInfrastructure"; Endpoint = "events/infrastructure"; Index = "infrastructure" },
    @{ Name = "NetskopeEventsNetworkDev"; DataType = "NetskopeEventsNetwork_CL"; Stream = "Custom-NetskopeEventsNetwork"; Endpoint = "events/network"; Index = "network" },
    @{ Name = "NetskopeEventsPageDev"; DataType = "NetskopeEventsPage_CL"; Stream = "Custom-NetskopeEventsPage"; Endpoint = "events/page"; Index = "page" }
)

Write-ColorOutput Green "Starting deployment of $($connectorConfigs.Count) data connector pollers..."
Write-Host ""

$successCount = 0
$failureCount = 0
$deploymentResults = @()

foreach ($config in $connectorConfigs) {
    try {
        Write-Host "Deploying: $($config.Name)..." -NoNewline
        
        # Construct API endpoint
        $apiEndpoint = "https://$DevOrgUrl/api/v2/events/dataexport/$($config.Endpoint)?operation=next&index=$($config.Index)$DevIndex"
        
        # Create resource template
        $template = @{
            '$schema' = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
            contentVersion = "1.0.0.0"
            parameters = @{}
            resources = @(
                @{
                    name = "$WorkspaceName/Microsoft.SecurityInsights/$($config.Name)"
                    apiVersion = "2023-02-01-preview"
                    type = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors"
                    location = $workspace.Location
                    kind = "RestApiPoller"
                    properties = @{
                        connectorDefinitionName = "NetskopeAlertsEvents"
                        dataType = $config.DataType
                        dcrConfig = @{
                            streamName = $config.Stream
                            dataCollectionEndpoint = $DataCollectionEndpoint
                            dataCollectionRuleImmutableId = $DataCollectionRuleId
                        }
                        auth = @{
                            type = "APIKey"
                            ApiKeyName = "Netskope-Api-Token"
                            ApiKey = $DevApiKeyPlain
                        }
                        request = @{
                            apiEndpoint = $apiEndpoint
                            httpMethod = "GET"
                            queryWindowInMin = 1
                            queryTimeFormat = "UnixTimestamp"
                            rateLimitQps = 10
                            retryCount = 3
                            timeoutInSeconds = 60
                            headers = @{
                                Accept = "application/json"
                            }
                        }
                        response = @{
                            eventsJsonPaths = @("$.result")
                        }
                    }
                }
            )
        }
        
        # Deploy the resource
        $deploymentName = "Deploy-$($config.Name)-$(Get-Date -Format 'yyyyMMddHHmmss')"
        $deployment = New-AzResourceGroupDeployment -ResourceGroupName $ResourceGroupName -Name $deploymentName -TemplateObject $template -ErrorAction Stop
        
        Write-ColorOutput Green " SUCCESS"
        $successCount++
        $deploymentResults += @{
            Name = $config.Name
            Status = "SUCCESS"
            DataType = $config.DataType
            Endpoint = $apiEndpoint
        }
    }
    catch {
        Write-ColorOutput Red " FAILED"
        Write-ColorOutput Red "  Error: $($_.Exception.Message)"
        $failureCount++
        $deploymentResults += @{
            Name = $config.Name
            Status = "FAILED"
            Error = $_.Exception.Message
        }
    }
}

Write-Host ""
Write-ColorOutput Green "=== Deployment Summary ==="
Write-ColorOutput Green "Successful deployments: $successCount"
if ($failureCount -gt 0) {
    Write-ColorOutput Red "Failed deployments: $failureCount"
}

Write-Host ""
Write-ColorOutput Yellow "=== Verification Steps ==="
Write-Host "1. Go to Microsoft Sentinel -> Data Connectors"
Write-Host "2. Search for 'Netskope' to see all connector instances"
Write-Host "3. Run the verification queries provided in VerificationQueries.kql"
Write-Host "4. Check that both PROD and DEV data are flowing to the same tables"

if ($successCount -gt 0) {
    Write-Host ""
    Write-ColorOutput Green "=== Sample Verification Query ==="
    Write-Host @"
// Check data from both environments (last 1 hour)
union 
NetskopeAlerts_CL,
NetskopeEventsApplication_CL
| extend Environment = case(
    PolicyName startswith "DEV", "DEV",
    PolicyName startswith "PROD", "PROD",
    "Unknown"
)
| where TimeGenerated > ago(1h)
| summarize Count = count(), LatestEvent = max(TimeGenerated) by Environment, TableName = `$table
| order by Environment, TableName
"@
}

Write-Host ""
Write-ColorOutput Green "Deployment completed!"

# Clear sensitive data
$DevApiKeyPlain = $null
[System.GC]::Collect()