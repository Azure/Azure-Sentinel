# This script retrieves SAP BTP service keys and creates data connector connections in Microsoft Sentinel for SAP BTP.
# It polls the service keys created by the provision-audit-to-subaccounts.ps1 script and uses Azure API 
# to create SAP BTP connections to subaccounts in the Sentinel for SAP BTP solution.
#
# IMPORTANT: This script does NOT create new data connectors. It adds account connections to the existing
# SAP BTP data connector that must be deployed first via the Microsoft Sentinel Content Hub.
#
# Prerequisites:
# - Azure CLI installed: https://learn.microsoft.com/cli/azure/install-azure-cli
# - Cloud Foundry CLI (cf) installed and configured
# - Successful run of provision-audit-to-subaccounts.ps1
# - SAP BTP Solution installed from Content Hub
# - SAP BTP data connector deployed in the workspace
# - Appropriate Azure permissions to create data connector connections. Learn more: https://learn.microsoft.com/azure/sentinel/sap/deploy-sap-btp-solution
# - Appropriate CloudFoundry permissions to retrieve service keys. Learn more: https://learn.microsoft.com/azure/sentinel/sap/deploy-sap-btp-solution#prerequisites
# - A CSV file named 'subaccounts.csv' with columns: SubaccountId;cf-api-endpoint;cf-org-name;cf-space-name
#
# Usage:
#   1. Run 'az login' to authenticate to Azure
#   2. Run 'az account set --subscription "<azure-sub-id>"' to set the subscription where Sentinel is deployed
#   4. Update 'subaccounts.csv' with your subaccount details
#   5. Execute:
#       $securePassword = Read-Host "Enter CF Password" -AsSecureString
#       .\connect-sentinel-to-btp.ps1 -SubscriptionId "<azure-sentinel-sub-id>" -ResourceGroupName "<rg-name-sentinel-workspace>" -WorkspaceName "<sentinel-workspace-name>" -CfUsername "<cf-username>" -CfPassword $securePassword

# Parameters
param(
    [Parameter(Mandatory=$true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceName,
    
    [Parameter(Mandatory=$false)]
    [string]$CsvPath = ".\subaccounts.csv",
    
    [Parameter(Mandatory=$false)]
    [string]$InstanceNamePrefix = "sentinel-audit-srv",
    
    [Parameter(Mandatory=$false)]
    [string]$CfUsername = $env:CF_USERNAME,
    
    [Parameter(Mandatory=$false)]
    [SecureString]$CfPassword,
    
    [Parameter(Mandatory=$false)]
    [string]$ApiVersion = "2025-09-01"
)

# Import shared helper functions
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\BtpHelpers.ps1" -Force

# Validate and get CF credentials using helper function
$credentials = Get-CfCredentials -Username $CfUsername -Password $CfPassword
if ($null -eq $credentials) {
    exit 1
}
$CfUsername = $credentials.Username
$CfPassword = $credentials.Password

# Main script execution
Write-Log "======================================================================="
Write-Log "Starting Sentinel Solution for SAP BTP Connection Creation Process"
Write-Log "IMPORTANT: This adds connections to the existing SAP BTP data connector"
Write-Log "Make sure the SAP BTP solution is installed from Content Hub first!"
Write-Log "======================================================================="

# Check if Azure CLI is installed
if (-not (Test-AzCli)) {
    Write-Log "Exiting script due to missing Azure CLI." -Level "ERROR"
    exit 1
}

# Check if CF CLI is installed
if (-not (Test-CfCli)) {
    Write-Log "Exiting script due to missing CF CLI." -Level "ERROR"
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

# Set Azure subscription context
try {
    $setSubResult = az account set --subscription $SubscriptionId 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Failed to set Azure subscription: $setSubResult" -Level "ERROR"
        exit 1
    }
    Write-Log "Set Azure subscription context to: $SubscriptionId" -Level "SUCCESS"
}
catch {
    Write-Log "Failed to set Azure subscription context: $_" -Level "ERROR"
    exit 1
}

# Load subaccounts from CSV using helper function
$subaccounts = Import-BtpSubaccountsCsv -CsvPath $CsvPath
if ($null -eq $subaccounts) {
    exit 1
}

# Process each subaccount
$successCount = 0
$failureCount = 0
$currentApiEndpoint = $null

foreach ($subaccount in $subaccounts) {
    $subaccountId = $subaccount.SubaccountId
    $subaccountName = $subaccount.DisplayName
    $apiEndpoint = $subaccount.'cf-api-endpoint'
    $orgName = $subaccount.'cf-org-name'
    $spaceName = $subaccount.'cf-space-name'
    
    if ([string]::IsNullOrWhiteSpace($subaccountId)) {
        Write-Log "Skipping row with empty SubaccountId" -Level "WARNING"
        continue
    }
    
    Write-Log "======================================================================="
    Write-Log "Processing Subaccount: $subaccountId"
    Write-Log "API Endpoint: $apiEndpoint"
    Write-Log "Org: $orgName | Space: $spaceName"
    Write-Log "======================================================================="
    
    # Switch API endpoint if needed
    if ($currentApiEndpoint -ne $apiEndpoint) {
        if (-not (Set-CfApiEndpoint -ApiEndpoint $apiEndpoint -Username $CfUsername -Password $CfPassword -OrgName $orgName -SpaceName $spaceName)) {
            Write-Log "Failed to switch API endpoint. Skipping subaccount." -Level "ERROR"
            $failureCount++
            continue
        }
        $currentApiEndpoint = $apiEndpoint
    }
    
    # Target the org and space
    if (-not (Set-CfTarget -OrgName $orgName -SpaceName $spaceName)) {
        Write-Log "Failed to target org/space. Skipping subaccount." -Level "ERROR"
        $failureCount++
        continue
    }
    
    # Define instance and key names
    $instanceName = $InstanceNamePrefix
    $keyName = "$InstanceNamePrefix-key"
    
    # Get service key
    $serviceKey = Get-CfServiceKey -InstanceName $instanceName -KeyName $keyName
    
    if ($null -eq $serviceKey) {
        Write-Log "Failed to retrieve service key for subaccount $subaccountId. Skipping." -Level "ERROR"
        $failureCount++
        continue
    }
    
    # Extract and validate credentials from service key
    $btpCredentials = Get-BtpServiceKeyCredentials -ServiceKey $serviceKey
    
    if ($null -eq $btpCredentials) {
        Write-Log "Failed to extract valid credentials from service key for subaccount $subaccountId. Skipping." -Level "ERROR"
        $failureCount++
        continue
    }
    
    Write-Log "Successfully extracted credentials from service key:" -Level "SUCCESS"
    Write-Log "  Client ID: $($btpCredentials.ClientId)" -Level "SUCCESS"
    Write-Log "  Token Endpoint: $($btpCredentials.TokenEndpoint)" -Level "SUCCESS"
    Write-Log "  API URL: $($btpCredentials.ApiUrl)" -Level "SUCCESS"
    Write-Log "  Subdomain: $($btpCredentials.Subdomain)" -Level "SUCCESS"
    
    # Generate connection name from subdomain or subaccount ID
    $connectionName = Get-BtpConnectionName -BtpCredentials $btpCredentials -SubaccountId $subaccountId
    
    # Create Sentinel SAP BTP connection
    $connectionCreated = New-SentinelBtpConnection `
        -SubscriptionId $SubscriptionId `
        -ResourceGroupName $ResourceGroupName `
        -WorkspaceName $WorkspaceName `
        -ConnectionName $connectionName `
        -BtpCredentials $btpCredentials `
        -SubaccountId $subaccountId `
        -SubaccountName $subaccountName `
        -ApiVersion $ApiVersion
    
    if ($connectionCreated) {
        $successCount++
        Write-Log "Subaccount $subaccountId connected to Sentinel successfully" -Level "SUCCESS"
    }
    else {
        $failureCount++
        Write-Log "Failed to connect subaccount $subaccountId to Sentinel" -Level "ERROR"
    }
    
    # Small delay between operations
    Start-Sleep -Seconds 2
}

# Summary
Write-Log "======================================================================="
Write-Log "Connection process completed"
Write-Log "Total subaccounts processed: $($subaccounts.Count)"
Write-Log "Successful: $successCount"
Write-Log "Failed: $failureCount"
Write-Log "======================================================================="
