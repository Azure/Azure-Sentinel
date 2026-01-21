# This script shows automatic onboarding of multiple SAP BTP subaccounts to the SAP Auditlog Management service.
# This is half-way mark to the full integration with Azure Sentinel for SAP BTP.
# The script provisions the 'auditlog-management' service instance and service key in each specified subaccount.
# The service key contains the necessary credentials to connect SAP BTP Auditlog Management with Microsoft Sentinel for SAP BTP.
#
# Prerequisites:
# - Cloud Foundry CLI (cf) installed and configured
# - CF login session established (run 'cf login' before executing this script)
# - Appropriate permissions in SAP BTP to create services in target orgs/spaces
# - SAP BTP entitlements/quota for 'auditlog-management' service in each subaccount
# - Sentinel Solution for SAP BTP deployed in your Azure environment
# - A CSV file named 'subaccounts.csv' with columns: SubaccountId;cf-api-endpoint;cf-org-name;cf-space-name
#
# Usage: 
#   1. Run 'cf login' first to establish authentication
#   2. Update 'subaccounts.csv' with your subaccount details
#   3. Execute this script in PowerShell from the Tools folder:
#       $securePassword = Read-Host "Enter CF Password" -AsSecureString
#       .\provision-audit-to-subaccounts.ps1 -CfUsername "<your-cf-username>" -CfPassword $securePassword

# Parameters
param(
    [Parameter(Mandatory=$false)]
    [string]$CsvPath = ".\subaccounts.csv",
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "auditlog-management",
    
    [Parameter(Mandatory=$false)]
    [string]$ServicePlan = "default",
    
    [Parameter(Mandatory=$false)]
    [string]$InstanceNamePrefix = "sentinel-audit-srv",
    
    [Parameter(Mandatory=$false)]
    [string]$CfUsername = $env:CF_USERNAME,
    
    [Parameter(Mandatory=$false)]
    [SecureString]$CfPassword
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
Write-Log "Starting SAP BTP Audit Log Management Onboarding Process"
Write-Log "======================================================================="

# Check if CF CLI is installed
if (-not (Test-CfCli)) {
    Write-Log "Exiting script due to missing CF CLI." -Level "ERROR"
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
    
    # Generate instance name (same for all subaccounts)
    $instanceName = $InstanceNamePrefix
    $keyName = "$InstanceNamePrefix-key"
    
    # Create service instance
    $serviceCreated = New-CfServiceInstance -InstanceName $instanceName -Service $ServiceName -Plan $ServicePlan
    
    if (-not $serviceCreated) {
        $failureCount++
        continue
    }
    
    # Wait a bit for service to be ready
    Write-Log "Waiting for service instance to be ready..."
    Start-Sleep -Seconds 5
    
    # Create service key
    $keyCreated = New-CfServiceKey -InstanceName $instanceName -KeyName $keyName
    
    if ($keyCreated) {
        $successCount++
        Write-Log "Subaccount $subaccountId processed successfully" -Level "SUCCESS"
    }
    else {
        $failureCount++
        Write-Log "Subaccount $subaccountId partially completed (service created, key failed)" -Level "WARNING"
    }
    
    # Small delay between subaccounts
    Start-Sleep -Seconds 2
}

# Summary
Write-Log "======================================================================="
Write-Log "Onboarding process completed"
Write-Log "Total subaccounts processed: $($subaccounts.Count)"
Write-Log "Successful: $successCount"
Write-Log "Failed: $failureCount"
Write-Log "======================================================================="
