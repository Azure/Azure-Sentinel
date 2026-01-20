# connect-sentinel-to-integration-suite.ps1
# Main script to connect Microsoft Sentinel to SAP Integration Suite runtime instance.
# This script creates data connector connections using the SAPCC connector definition,
# processing destinations from a CSV file to create multiple connections.
#
# Key Features:
# - Supports both Cloud Foundry (CF) and SAP NEO environments
# - CF Mode: Retrieves credentials at runtime via CF CLI (no stored secrets)
# - Direct Mode: Supply credentials directly for SAP NEO or other environments
# - Processes destinations.csv to create connections for each SAP backend
# - Uses shared DCE/DCR across all connections
# - Supports multiple authentication types:
#   - OAuth2: Standard OAuth2 with credentials in request body (default)
#   - Basic: HTTP Basic Auth without OAuth (username/password on every request)
#
# Prerequisites:
# - Azure CLI installed: https://learn.microsoft.com/cli/azure/install-azure-cli
# - Microsoft Sentinel workspace with SAP solution installed
# - SAP Integration Suite with:
#   - Process Integration Runtime service instance
#   - Integration flow deployed at /http/microsoft/sentinel/sap-log-trigger
# - destinations.csv file with SAP backend destinations
#
# For Cloud Foundry environments:
# - Cloud Foundry CLI installed: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html
# - CF CLI logged in: cf login && cf target -o <org> -s <space>
#
# Usage (CF Mode - credentials retrieved at runtime and defaulted to OAuth2):
#   .\connect-sentinel-to-integration-suite.ps1 `
#       -SubscriptionId "<azure-sub-id>" `
#       -ResourceGroupName "<rg-name>" `
#       -WorkspaceName "<sentinel-workspace-name>" `
#       -DestinationsCsvPath ".\destinations.csv"
#
# Usage (Direct Mode with OAuth2):
#   $secret = Read-Host "Enter Client Secret" -AsSecureString
#   .\connect-sentinel-to-integration-suite.ps1 `
#       -SubscriptionId "<azure-sub-id>" `
#       -ResourceGroupName "<rg-name>" `
#       -WorkspaceName "<sentinel-workspace-name>" `
#       -DestinationsCsvPath ".\destinations.csv" `
#       -IntegrationServerUrl "https://tenant.it-cpi023-rt.cfapps.eu20.hana.ondemand.com" `
#       -TokenEndpoint "https://tenant.authentication.eu20.hana.ondemand.com/oauth/token" `
#       -ClientId "sb-xxx" `
#       -ClientSecret $secret `
#       -AuthType "OAuth2"
#
# Usage (Direct Mode with Basic Auth - no OAuth):
#   $secret = Read-Host "Enter Password" -AsSecureString
#   .\connect-sentinel-to-integration-suite.ps1 `
#       -SubscriptionId "<azure-sub-id>" `
#       -ResourceGroupName "<rg-name>" `
#       -WorkspaceName "<sentinel-workspace-name>" `
#       -DestinationsCsvPath ".\destinations.csv" `
#       -IntegrationServerUrl "https://tenant.it-cpi023-rt.cfapps.eu20.hana.ondemand.com" `
#       -ClientId "username" `
#       -ClientSecret $secret `
#       -AuthType "Basic"

# Parameters
param(
    # Azure Configuration
    [Parameter(Mandatory=$true, HelpMessage="Azure Subscription ID where Microsoft Sentinel is deployed")]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$true, HelpMessage="Resource Group name containing the Sentinel workspace")]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true, HelpMessage="Log Analytics workspace name with Sentinel enabled")]
    [string]$WorkspaceName,
    
    # Destinations Configuration
    [Parameter(Mandatory=$false, HelpMessage="Path to destinations CSV file")]
    [string]$DestinationsCsvPath = ".\destinations.csv",
    
    [Parameter(Mandatory=$false, HelpMessage="Prefix for connection names (default: SAP)")]
    [string]$ConnectionPrefix = "SAP",
    
    # Direct Credential Parameters (for SAP NEO or environments without CF CLI)
    # When these are provided, CF CLI is not required
    [Parameter(Mandatory=$false, HelpMessage="Integration Server URL (e.g., https://tenant.it-cpi023-rt.cfapps.eu20.hana.ondemand.com)")]
    [string]$IntegrationServerUrl,
    
    [Parameter(Mandatory=$false, HelpMessage="OAuth Token Endpoint URL (e.g., https://oauthasservices-xxx.hana.ondemand.com/oauth2/api/v1/token for NEO)")]
    [string]$TokenEndpoint,
    
    [Parameter(Mandatory=$false, HelpMessage="OAuth Client ID")]
    [string]$ClientId,
    
    [Parameter(Mandatory=$false, HelpMessage="OAuth Client Secret (SecureString)")]
    [SecureString]$ClientSecret,
    
    [Parameter(Mandatory=$false, HelpMessage="Path to service key JSON file (alternative to direct credentials)")]
    [string]$ServiceKeyPath,
    
    # Cloud Foundry Configuration (used when direct credentials are not provided)
    [Parameter(Mandatory=$false, HelpMessage="Name of the CPI service instance in Cloud Foundry")]
    [string]$InstanceName = "cpi-sentinel-integration-rt",
    
    [Parameter(Mandatory=$false, HelpMessage="Name of the service key for the CPI instance")]
    [string]$KeyName = "cpi-sentinel-integration-key",
    
    # Authentication Type (for direct credentials mode)
    [Parameter(Mandatory=$false, HelpMessage="Authentication type: OAuth2 or Basic")]
    [ValidateSet("OAuth2", "Basic")]
    [string]$AuthType = "OAuth2",
    
    # Optional Configuration
    [Parameter(Mandatory=$false, HelpMessage="API path suffix after /http (default: /microsoft/sentinel/sap-log-trigger)")]
    [string]$ApiPathSuffix = "/microsoft/sentinel/sap-log-trigger",
    
    [Parameter(Mandatory=$false, HelpMessage="Azure Management API version")]
    [string]$ApiVersion = "2025-07-01-preview"
)

# Import shared helper functions
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\IntegrationSuiteHelpers.ps1" -Force

# Main script execution
Write-Log "======================================================================="
Write-Log "SAP Integration Suite - Microsoft Sentinel Connector"
Write-Log "======================================================================="
Write-Log "This script creates data connector connections for SAP Integration Suite"
Write-Log "Data will flow to standard Microsoft SAP tables:"
Write-Log "  - ABAPAuditLog"
Write-Log "  - ABAPChangeDocsLog"
Write-Log "  - ABAPUserDetails"
Write-Log "  - ABAPAuthorizationDetails"
Write-Log "  - SentinelHealth (connector health)"
Write-Log "======================================================================="

# Check if Azure CLI is installed
if (-not (Test-AzCli)) {
    Write-Log "Exiting script due to missing Azure CLI." -Level "ERROR"
    exit 1
}

# Check Azure login
try {
    $accountInfo = az account show 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Not logged in to Azure. Please run 'az login' first." -Level "ERROR"
        exit 1
    }
    $account = $accountInfo | ConvertFrom-Json
    Write-Log "Azure account: $($account.user.name)"
    Write-Log "Current subscription: $($account.name) ($($account.id))"
}
catch {
    Write-Log "Error checking Azure account: $_" -Level "ERROR"
    exit 1
}

# Determine credential mode: Direct (NEO/manual) vs Cloud Foundry
$useDirectCredentials = $false
$credentials = $null

# Check if direct credentials are provided
# For Basic auth, TokenEndpoint is not required
$tokenEndpointRequired = $AuthType -ne "Basic"

if (-not [string]::IsNullOrWhiteSpace($ServiceKeyPath)) {
    # Service key file provided
    $useDirectCredentials = $true
    Write-Log "======================================================================="
    Write-Log "Using Direct Credentials Mode (Service Key File)"
    Write-Log "======================================================================="
    $credentials = Get-IntegrationSuiteCredentials -ServiceKeyPath $ServiceKeyPath
}
elseif (-not [string]::IsNullOrWhiteSpace($IntegrationServerUrl) -and
        (-not $tokenEndpointRequired -or -not [string]::IsNullOrWhiteSpace($TokenEndpoint)) -and
        -not [string]::IsNullOrWhiteSpace($ClientId) -and
        $null -ne $ClientSecret) {
    # Direct credentials provided via parameters
    $useDirectCredentials = $true
    Write-Log "======================================================================="
    Write-Log "Using Direct Credentials Mode (Parameters)"
    Write-Log "======================================================================="
    Write-Log "Authentication Type: $AuthType"
    if ($AuthType -eq "Basic") {
        Write-Log "This mode uses HTTP Basic Auth (username/password on every request)"
    }
    else {
        Write-Log "This mode supports SAP NEO and other non-CF environments"
    }
    
    $credentials = Get-IntegrationSuiteCredentials `
        -ClientId $ClientId `
        -ClientSecret $ClientSecret `
        -IntegrationServerUrl $IntegrationServerUrl `
        -TokenEndpoint $TokenEndpoint `
        -AuthType $AuthType
}

if ($useDirectCredentials) {
    if ($null -eq $credentials) {
        Write-Log "Failed to obtain valid credentials. Exiting." -Level "ERROR"
        exit 1
    }
    Write-Log "Credentials validated successfully" -Level "SUCCESS"
    Write-Log "  Authentication Type: $($credentials.AuthType)"
    Write-Log "  Integration Server URL: $($credentials.IntegrationServerUrl)"
    if ($credentials.AuthType -ne "Basic") {
        Write-Log "  Token Endpoint: $($credentials.TokenEndpoint)"
    }
    Write-Log "  Client ID: $($credentials.ClientId)"
}
else {
    # Cloud Foundry mode - retrieve credentials at runtime
    Write-Log "======================================================================="
    Write-Log "Using Cloud Foundry Mode (Runtime Credential Retrieval)"
    Write-Log "======================================================================="
    
    # Check CF CLI login status
    if (-not (Test-CfCliLogin)) {
        Write-Log "CF CLI not logged in and no direct credentials provided." -Level "ERROR"
        Write-Log "" -Level "ERROR"
        Write-Log "Options:" -Level "ERROR"
        Write-Log "  1. Login to CF: cf login -a <api-endpoint> && cf target -o <org> -s <space>" -Level "ERROR"
        Write-Log "  2. Provide direct credentials: -IntegrationServerUrl, -TokenEndpoint, -ClientId, -ClientSecret" -Level "ERROR"
        Write-Log "  3. Provide service key file: -ServiceKeyPath" -Level "ERROR"
        exit 1
    }
    
    # Get Integration Suite credentials at runtime
    $credentials = Get-IntegrationSuiteCredentialsFromCf -InstanceName $InstanceName -KeyName $KeyName
    
    if ($null -eq $credentials) {
        Write-Log "Failed to obtain valid credentials from Cloud Foundry. Exiting." -Level "ERROR"
        exit 1
    }
    
    Write-Log "Credentials retrieved successfully (no secrets stored)" -Level "SUCCESS"
}

# Load destinations from CSV
Write-Log "======================================================================="
Write-Log "Loading Destinations from CSV"
Write-Log "======================================================================="

$destinations = Import-DestinationsCsv -CsvPath $DestinationsCsvPath

if ($null -eq $destinations -or $destinations.Count -eq 0) {
    Write-Log "No valid destinations found. Exiting." -Level "ERROR"
    exit 1
}

Write-Log "Found $($destinations.Count) destination(s) to process"

# Get workspace details for DCE/DCR setup
Write-Log "======================================================================="
Write-Log "Setting up Data Collection Endpoint (DCE) and Data Collection Rule (DCR)"
Write-Log "======================================================================="

$workspaceDetails = Get-SentinelWorkspaceDetails `
    -SubscriptionId $SubscriptionId `
    -ResourceGroupName $ResourceGroupName `
    -WorkspaceName $WorkspaceName

if ($null -eq $workspaceDetails) {
    Write-Log "Failed to get workspace details. Exiting." -Level "ERROR"
    exit 1
}

# First try to find existing DCR - if found, we can get DCE from its properties
$dcrInfo = Get-OrCreateSapccDataCollectionRule `
    -SubscriptionId $SubscriptionId `
    -ResourceGroupName $ResourceGroupName `
    -WorkspaceShortId $workspaceDetails.ShortId `
    -WorkspaceResourceId $workspaceDetails.ResourceId `
    -Location $workspaceDetails.Location

$dceInfo = $null

if ($null -ne $dcrInfo -and -not [string]::IsNullOrWhiteSpace($dcrInfo.DataCollectionEndpointId)) {
    # DCR exists - get DCE details from the DCR's referenced endpoint
    Write-Log "Found existing DCR with DCE reference, retrieving DCE details..."
    $dceInfo = Get-DataCollectionEndpointById -DataCollectionEndpointId $dcrInfo.DataCollectionEndpointId
}

if ($null -eq $dceInfo) {
    # DCE not found via DCR - create new DCE first, then create DCR
    Write-Log "No existing DCE found, creating new Data Collection Endpoint..."
    
    $dceInfo = Get-OrCreateSapccDataCollectionEndpoint `
        -SubscriptionId $SubscriptionId `
        -ResourceGroupName $ResourceGroupName `
        -WorkspaceShortId $workspaceDetails.ShortId `
        -Location $workspaceDetails.Location
    
    if ($null -eq $dceInfo) {
        Write-Log "Failed to get or create DCE. Exiting." -Level "ERROR"
        exit 1
    }
    
    # Now create DCR with the new DCE
    $dcrInfo = Get-OrCreateSapccDataCollectionRule `
        -SubscriptionId $SubscriptionId `
        -ResourceGroupName $ResourceGroupName `
        -WorkspaceShortId $workspaceDetails.ShortId `
        -WorkspaceResourceId $workspaceDetails.ResourceId `
        -DataCollectionEndpointId $dceInfo.ResourceId `
        -Location $workspaceDetails.Location
    
    if ($null -eq $dcrInfo) {
        Write-Log "Failed to get or create DCR. Exiting." -Level "ERROR"
        exit 1
    }
}

# Build DcrConfig for connections
$dcrConfig = @{
    DataCollectionEndpoint = $dceInfo.LogsIngestionEndpoint
    DataCollectionRuleImmutableId = $dcrInfo.ImmutableId
}

Write-Log "DCE/DCR setup completed successfully" -Level "SUCCESS"
Write-Log "  DCE Name: $($dceInfo.Name)"
Write-Log "  DCE Logs Ingestion: $($dceInfo.LogsIngestionEndpoint)"
Write-Log "  DCR Name: $($dcrInfo.Name)"
Write-Log "  DCR Immutable ID: $($dcrInfo.ImmutableId)"

# Create Sentinel connections for each destination
Write-Log "======================================================================="
Write-Log "Creating Data Connector Connections"
Write-Log "======================================================================="

$successCount = 0
$failureCount = 0
$results = @()

foreach ($destination in $destinations) {
    $connectionName = "$ConnectionPrefix-$($destination.DestinationName)"
    $rfcDestinationName = $destination.DestinationName
    $pollingFrequency = $destination.PollingFrequencyInMinutes
    
    Write-Log "-----------------------------------------------------------------------"
    Write-Log "Processing: $connectionName"
    Write-Log "  RFC Destination: $rfcDestinationName"
    Write-Log "  Polling Frequency: $pollingFrequency minute(s)"
    
    $connectionCreated = New-SentinelIntegrationSuiteConnection `
        -SubscriptionId $SubscriptionId `
        -ResourceGroupName $ResourceGroupName `
        -WorkspaceName $WorkspaceName `
        -ConnectionName $connectionName `
        -Credentials $credentials `
        -DcrConfig $dcrConfig `
        -ApiPathSuffix $ApiPathSuffix `
        -RfcDestinationName $rfcDestinationName `
        -PollingFrequencyMinutes $pollingFrequency `
        -ApiVersion $ApiVersion
    
    $result = [PSCustomObject]@{
        ConnectionName = $connectionName
        DestinationName = $rfcDestinationName
        PollingFrequency = $pollingFrequency
        Success = $connectionCreated
    }
    $results += $result
    
    if ($connectionCreated) {
        $successCount++
        Write-Log "Connection '$connectionName' created successfully" -Level "SUCCESS"
    }
    else {
        $failureCount++
        Write-Log "Failed to create connection '$connectionName'" -Level "ERROR"
    }
}

# Summary
Write-Log "======================================================================="
Write-Log "Connection Creation Summary"
Write-Log "======================================================================="
Write-Log "Total Destinations: $($destinations.Count)"
Write-Log "Successful: $successCount" -Level $(if ($successCount -gt 0) { "SUCCESS" } else { "INFO" })
Write-Log "Failed: $failureCount" -Level $(if ($failureCount -gt 0) { "ERROR" } else { "INFO" })
Write-Log ""

if ($successCount -gt 0) {
    Write-Log "Successfully created connections:"
    foreach ($result in $results | Where-Object { $_.Success }) {
        Write-Log "  - $($result.ConnectionName) -> $($result.DestinationName) (every $($result.PollingFrequency) min)"
    }
}

if ($failureCount -gt 0) {
    Write-Log ""
    Write-Log "Failed connections:" -Level "WARNING"
    foreach ($result in $results | Where-Object { -not $_.Success }) {
        Write-Log "  - $($result.ConnectionName) -> $($result.DestinationName)" -Level "WARNING"
    }
}

Write-Log ""
Write-Log "Integration Server: $($credentials.IntegrationServerUrl)"
Write-Log "API Endpoint: $($credentials.IntegrationServerUrl)/http$ApiPathSuffix"
Write-Log ""

if ($failureCount -eq 0) {
    Write-Log "======================================================================="
    Write-Log "SUCCESS - All connections created!"
    Write-Log "======================================================================="
    Write-Log "Next steps:"
    Write-Log "  1. Verify connections appear in Microsoft Sentinel > Data Connectors"
    Write-Log "  2. Check SentinelHealth table for connector heartbeat"
    Write-Log "  3. Verify SAP data in ABAPAuditLog table after polling interval"
    Write-Log "======================================================================="
}
elseif ($successCount -gt 0) {
    Write-Log "======================================================================="
    Write-Log "PARTIAL SUCCESS - Some connections created"
    Write-Log "======================================================================="
    Write-Log "Please review the failed connections above and verify:"
    Write-Log "  1. Azure RBAC permissions for data connector creation"
    Write-Log "  2. Connection names don't already exist"
    Write-Log "  3. SAP solution is installed in the Sentinel workspace"
    Write-Log "======================================================================="
    exit 1
}
else {
    Write-Log "======================================================================="
    Write-Log "FAILED - No connections created"
    Write-Log "======================================================================="
    Write-Log "Please check the error messages above and verify:"
    Write-Log "  1. Azure RBAC permissions for data connector creation"
    Write-Log "  2. Integration Suite credentials are correct"
    Write-Log "  3. SAP solution is installed in the Sentinel workspace"
    Write-Log "======================================================================="
    exit 1
}
