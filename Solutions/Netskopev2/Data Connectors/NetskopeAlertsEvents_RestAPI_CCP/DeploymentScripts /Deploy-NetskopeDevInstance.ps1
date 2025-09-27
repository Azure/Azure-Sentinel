#Requires -Version 5.1
#Requires -Modules Az.Accounts, Az.Resources, Az.OperationalInsights

<#
.SYNOPSIS
    Deploys a second Netskope Alerts and Events data connector instance for DEV environment

.DESCRIPTION
    This script creates a duplicate set of Netskope data pollers with "DEV" prefix to enable
    multiple Netskope environments (PROD and DEV) to send data to the same Microsoft Sentinel workspace.
    
    The script creates 21 separate data collection endpoints (DCEs) and data collection rules (DCRs)
    for all Netskope event types, allowing both PROD and DEV data to coexist in the same tables.

.PARAMETER SubscriptionId
    Azure subscription ID where the resources will be deployed

.PARAMETER ResourceGroupName
    Name of the resource group containing the Log Analytics workspace

.PARAMETER WorkspaceName
    Name of the Log Analytics workspace

.PARAMETER Location
    Azure region where resources will be deployed (e.g., "eastus", "westus2")

.PARAMETER DevPrefix
    Prefix for DEV resources (default: "DEV")

.PARAMETER ProdPrefix
    Prefix for PROD resources (default: "PROD")

.EXAMPLE
    .\Deploy-NetskopeDevInstance.ps1 -SubscriptionId "12345678-1234-1234-1234-123456789012" -ResourceGroupName "rg-sentinel" -WorkspaceName "law-sentinel" -Location "eastus"

.NOTES
    Author: Microsoft Sentinel Community
    Version: 1.0
    Last Modified: 2024-12-24
    
    Prerequisites:
    - Az PowerShell modules installed
    - Authenticated to Azure with appropriate permissions
    - Existing Log Analytics workspace
    - PROD Netskope connector already deployed via Content Hub
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$WorkspaceName,
    
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Location,
    
    [Parameter(Mandatory = $false)]
    [ValidateNotNullOrEmpty()]
    [string]$DevPrefix = "DEV",
    
    [Parameter(Mandatory = $false)]
    [ValidateNotNullOrEmpty()]
    [string]$ProdPrefix = "PROD"
)

# Error handling
$ErrorActionPreference = "Stop"

# Define all Netskope data connector types
$NetskopeConnectorTypes = @(
    "NetskopeAlertsEvents-ApplicationEvents",
    "NetskopeAlertsEvents-AuditEvents", 
    "NetskopeAlertsEvents-ConnectionEvents",
    "NetskopeAlertsEvents-InfrastructureEvents",
    "NetskopeAlertsEvents-NetworkEvents",
    "NetskopeAlertsEvents-PagesEvents",
    "NetskopeAlertsEvents-AlertsEvents",
    "NetskopeAlertsEvents-BehaviorAnalyticsAlertsEvents",
    "NetskopeAlertsEvents-CompromisedCredentialsAlertsEvents",
    "NetskopeAlertsEvents-DLPAlertsEvents",
    "NetskopeAlertsEvents-LegalHoldAlertsEvents",
    "NetskopeAlertsEvents-MalsiteAlertsEvents",
    "NetskopeAlertsEvents-MalwareAlertsEvents",
    "NetskopeAlertsEvents-PolicyAlertsEvents",
    "NetskopeAlertsEvents-QuarantineAlertsEvents",
    "NetskopeAlertsEvents-RemediationAlertsEvents",
    "NetskopeAlertsEvents-SecurityAssessmentAlertsEvents",
    "NetskopeAlertsEvents-UBAAlertsEvents",
    "NetskopeAlertsEvents-WatchlistAlertsEvents",
    "NetskopeAlertsEvents-WebTxAlertsEvents",
    "NetskopeAlertsEvents-CTEPAlertsEvents"
)

try {
    Write-Host "Starting Netskope DEV instance deployment..." -ForegroundColor Green
    
    # Connect to Azure
    Write-Host "Setting Azure context..." -ForegroundColor Yellow
    Set-AzContext -SubscriptionId $SubscriptionId
    
    # Verify resource group exists
    Write-Host "Verifying resource group exists..." -ForegroundColor Yellow
    $resourceGroup = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
    if (-not $resourceGroup) {
        throw "Resource group '$ResourceGroupName' not found."
    }
    
    # Verify workspace exists
    Write-Host "Verifying Log Analytics workspace exists..." -ForegroundColor Yellow
    $workspace = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction SilentlyContinue
    if (-not $workspace) {
        throw "Log Analytics workspace '$WorkspaceName' not found in resource group '$ResourceGroupName'."
    }
    
    $workspaceId = $workspace.ResourceId
    Write-Host "Using workspace: $WorkspaceName (ID: $workspaceId)" -ForegroundColor Green
    
    # Deploy each connector type
    $successCount = 0
    $failedCount = 0
    
    foreach ($connectorType in $NetskopeConnectorTypes) {
        try {
            Write-Host "Deploying $connectorType..." -ForegroundColor Yellow
            
            # Create unique names for DEV instance
            $devConnectorName = "$DevPrefix-$connectorType"
            $dceResourceName = "dce-$devConnectorName"
            $dcrResourceName = "dcr-$devConnectorName"
            
            # Create Data Collection Endpoint (DCE)
            Write-Host "  Creating DCE: $dceResourceName" -ForegroundColor Cyan
            $dceProperties = @{
                location = $Location
                properties = @{
                    networkAcls = @{
                        publicNetworkAccess = "Enabled"
                    }
                }
            }
            
            $dce = New-AzResource -ResourceGroupName $ResourceGroupName -ResourceType "Microsoft.Insights/dataCollectionEndpoints" -Name $dceResourceName -Properties $dceProperties.properties -Location $Location -Force
            
            if ($dce) {
                Write-Host "  ✓ DCE created successfully" -ForegroundColor Green
            }
            
            # Create Data Collection Rule (DCR)
            Write-Host "  Creating DCR: $dcrResourceName" -ForegroundColor Cyan
            
            # Determine target table based on connector type
            $targetTable = switch -Regex ($connectorType) {
                "ApplicationEvents" { "NetskopeApplicationEvents_CL" }
                "AuditEvents" { "NetskopeAuditEvents_CL" }
                "ConnectionEvents" { "NetskopeConnectionEvents_CL" }
                "InfrastructureEvents" { "NetskopeInfrastructureEvents_CL" }
                "NetworkEvents" { "NetskopeNetworkEvents_CL" }
                "PagesEvents" { "NetskopePagesEvents_CL" }
                "AlertsEvents$" { "NetskopeAlertsEvents_CL" }
                "BehaviorAnalyticsAlertsEvents" { "NetskopeBehaviorAnalyticsAlertsEvents_CL" }
                "CompromisedCredentialsAlertsEvents" { "NetskopeCompromisedCredentialsAlertsEvents_CL" }
                "DLPAlertsEvents" { "NetskopeDLPAlertsEvents_CL" }
                "LegalHoldAlertsEvents" { "NetskopeLegalHoldAlertsEvents_CL" }
                "MalsiteAlertsEvents" { "NetskopeMalsiteAlertsEvents_CL" }
                "MalwareAlertsEvents" { "NetskopeMalwareAlertsEvents_CL" }
                "PolicyAlertsEvents" { "NetskopePolicyAlertsEvents_CL" }
                "QuarantineAlertsEvents" { "NetskopeQuarantineAlertsEvents_CL" }
                "RemediationAlertsEvents" { "NetskopeRemediationAlertsEvents_CL" }
                "SecurityAssessmentAlertsEvents" { "NetskopeSecurityAssessmentAlertsEvents_CL" }
                "UBAAlertsEvents" { "NetskopeUBAAlertsEvents_CL" }
                "WatchlistAlertsEvents" { "NetskopeWatchlistAlertsEvents_CL" }
                "WebTxAlertsEvents" { "NetskopeWebTxAlertsEvents_CL" }
                "CTEPAlertsEvents" { "NetskopeCTEPAlertsEvents_CL" }
                default { "NetskopeEvents_CL" }
            }
            
            $dcrProperties = @{
                location = $Location
                properties = @{
                    dataCollectionEndpointId = $dce.ResourceId
                    streamDeclarations = @{
                        "Custom-$targetTable" = @{
                            columns = @(
                                @{ name = "TimeGenerated"; type = "datetime" }
                                @{ name = "RawData"; type = "string" }
                            )
                        }
                    }
                    destinations = @{
                        logAnalytics = @(
                            @{
                                workspaceResourceId = $workspaceId
                                name = "law-destination"
                            }
                        )
                    }
                    dataFlows = @(
                        @{
                            streams = @("Custom-$targetTable")
                            destinations = @("law-destination")
                            transformKql = "source | extend TimeGenerated = now()"
                            outputStream = "Custom-$targetTable"
                        }
                    )
                }
            }
            
            $dcr = New-AzResource -ResourceGroupName $ResourceGroupName -ResourceType "Microsoft.Insights/dataCollectionRules" -Name $dcrResourceName -Properties $dcrProperties.properties -Location $Location -Force
            
            if ($dcr) {
                Write-Host "  ✓ DCR created successfully" -ForegroundColor Green
                Write-Host "  ✓ Target table: $targetTable" -ForegroundColor Green
            }
            
            $successCount++
            Write-Host "✓ Successfully deployed $connectorType" -ForegroundColor Green
            
        }
        catch {
            Write-Warning "Failed to deploy $connectorType`: $($_.Exception.Message)"
            $failedCount++
        }
    }
    
    # Summary
    Write-Host "`n" -NoNewline
    Write-Host "=== DEPLOYMENT SUMMARY ===" -ForegroundColor Cyan
    Write-Host "Successfully deployed: $successCount connectors" -ForegroundColor Green
    Write-Host "Failed deployments: $failedCount connectors" -ForegroundColor Red
    Write-Host "Total connectors: $($NetskopeConnectorTypes.Count)" -ForegroundColor Yellow
    
    if ($failedCount -eq 0) {
        Write-Host "`nAll Netskope DEV connectors deployed successfully! 🎉" -ForegroundColor Green
        Write-Host "You can now configure your DEV Netskope tenant to send data using the '$DevPrefix-' prefixed policy names." -ForegroundColor Green
    } else {
        Write-Host "`nDeployment completed with $failedCount failures. Check the logs above for details." -ForegroundColor Yellow
    }
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Configure your DEV Netskope tenant with policy names prefixed with '$DevPrefix-'" -ForegroundColor White
    Write-Host "2. Configure data endpoints to use the newly created DCEs" -ForegroundColor White
    Write-Host "3. Verify data ingestion using the verification queries" -ForegroundColor White
    Write-Host "4. Update your analytics rules to filter by policy name prefixes" -ForegroundColor White
    
}
catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}
