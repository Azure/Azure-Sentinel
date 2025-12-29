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
    [string]$InstanceName = "sentinel-audit-srv",
    
    [Parameter(Mandatory=$false)]
    [string]$CfUsername = $env:CF_USERNAME,
    
    [Parameter(Mandatory=$false)]
    [SecureString]$CfPassword,
    
    [Parameter(Mandatory=$false)]
    [switch]$ExportCredentialsToCsv,
    
    [Parameter(Mandatory=$false)]
    [switch]$ExportCredentialsToKeyVault,
    
    [Parameter(Mandatory=$false)]
    [string]$KeyVaultName,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("CreateNewKey", "Cleanup")]
    [string]$KeyRotationMode = "CreateNewKey"
)

# Import shared helper functions
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\BtpHelpers.ps1" -Force

# Validate Key Vault parameters if exporting to Key Vault
if ($ExportCredentialsToKeyVault) {
    if ([string]::IsNullOrWhiteSpace($KeyVaultName)) {
        Write-Log "KeyVaultName parameter is required when ExportCredentialsToKeyVault is specified" -Level "ERROR"
        exit 1
    }
    
    # Check if Azure CLI is available
    if (-not (Test-AzCli)) {
        Write-Log "Azure CLI is required for Key Vault operations. Exiting." -Level "ERROR"
        exit 1
    }
}

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
Write-Log "Key Rotation Mode: $KeyRotationMode"
if ($ExportCredentialsToCsv) {
    Write-Log "Export Credentials to CSV: Enabled"
    Write-Log "WARNING: Credentials will be stored in plaintext in CSV file" -Level "WARNING"
}
if ($ExportCredentialsToKeyVault) {
    Write-Log "Export Credentials to Key Vault: Enabled"
    Write-Log "Key Vault Name: $KeyVaultName"
}
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
    
    # Initialize variables for this subaccount iteration
    $serviceKey = $null
    $credentials = $null
    
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
    
    # Discover existing auditlog-management instances
    $existingInstances = Get-CfServiceInstancesByOffering -ServiceOffering $ServiceName
    
    # Determine which instance to use - always look for exact match first
    if ($existingInstances.Count -gt 0) {
        # Look for instance matching the specified name (default or custom)
        $matchingInstance = $existingInstances | Where-Object { $_ -eq $InstanceName }
        
        if ($matchingInstance) {
            $instanceName = $matchingInstance
            Write-Log "Using instance: $instanceName" -Level "INFO"
        } else {
            # Instance name not found in discovered instances
            Write-Log "Instance '$InstanceName' not found. Available: $($existingInstances -join ', ')" -Level "WARNING"
            Write-Log "Will create new instance: $InstanceName" -Level "INFO"
            $instanceName = $InstanceName
        }
    }
    else {
        # No existing instances, create new one with configured name
        $instanceName = $InstanceName
        Write-Log "No existing auditlog-management instance found. Will create: $instanceName" -Level "INFO"
    }
    
    $keyName = "$instanceName-key"
    
    # Create service instance (will skip if already exists)
    $serviceCreated = New-CfServiceInstance -InstanceName $instanceName -Service $ServiceName -Plan $ServicePlan
    
    if (-not $serviceCreated) {
        $failureCount++
        continue
    }
    
    # Wait a bit for service to be ready
    Write-Log "Waiting for service instance to be ready..."
    Start-Sleep -Seconds 5
    
    # Handle key rotation based on mode
    $existingKeys = Get-CfServiceKeys -InstanceName $instanceName
    $keyExists = $existingKeys -contains $keyName
    
    if ($KeyRotationMode -eq "Cleanup") {
        # Cleanup mode: Keep only the newest key (last in list), delete all others
        Write-Log "Running in Cleanup mode: Removing old service keys..."
        
        if ($existingKeys.Count -gt 1) {
            # CF returns keys in creation order, last one is newest
            $newestKey = $existingKeys[-1]
            $keysToDelete = $existingKeys[0..($existingKeys.Count-2)]
            
            Write-Log "Keeping newest key: $newestKey" -Level "INFO"
            Write-Log "Deleting $($keysToDelete.Count) old key(s)..." -Level "INFO"
            
            foreach ($oldKey in $keysToDelete) {
                Write-Log "Deleting old service key: $oldKey"
                $deleteResult = cf delete-service-key $instanceName $oldKey -f 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Log "Successfully deleted service key '$oldKey'" -Level "SUCCESS"
                } else {
                    Write-Log "Failed to delete service key '$oldKey': $deleteResult" -Level "WARNING"
                }
            }
            
            $successCount++
            Write-Log "Cleanup completed for subaccount $subaccountId" -Level "SUCCESS"
        } else {
            Write-Log "Only one or no keys exist, nothing to clean up" -Level "INFO"
            $successCount++
        }
        
        # Skip to next subaccount in cleanup mode (no key creation)
        Start-Sleep -Seconds 2
        continue
    }
    
    # For CreateNewKey mode, handle key creation
    if ($keyExists) {
        # CreateNewKey mode with existing key - generate timestamped key name
        $timestamp = Get-Date -Format "yyyyMMddHHmmss"
        $keyName = "$InstanceName-key-$timestamp"
        Write-Log "Key already exists. Creating new key with timestamp: $keyName" -Level "INFO"
    }
    
    # Create service key
    $keyCreated = New-CfServiceKey -InstanceName $instanceName -KeyName $keyName
    
    if (-not $keyCreated) {
        $failureCount++
        continue
    }
    
    # Export credentials to CSV if requested
    if ($ExportCredentialsToCsv) {
        Write-Log "Retrieving service key for CSV export..."
        $serviceKey = Get-CfServiceKey -InstanceName $instanceName -KeyName $keyName
        
        if ($null -ne $serviceKey) {
            $credentials = Get-BtpServiceKeyCredentials -ServiceKey $serviceKey
            
            if ($null -ne $credentials) {
                $exported = Export-ServiceKeyToCsv -CsvPath $CsvPath -SubaccountId $subaccountId -Credentials $credentials
                
                if ($exported) {
                    Write-Log "Credentials exported to CSV for subaccount $subaccountId" -Level "SUCCESS"
                } else {
                    Write-Log "Failed to export credentials to CSV" -Level "WARNING"
                }
            } else {
                Write-Log "Failed to extract credentials from service key" -Level "WARNING"
            }
        } else {
            Write-Log "Failed to retrieve service key for export" -Level "WARNING"
        }
    }
    
    # Export credentials to Key Vault if requested
    if ($ExportCredentialsToKeyVault) {
        Write-Log "Retrieving service key for Key Vault export..."
        
        # Only retrieve service key if not already retrieved for CSV
        if ($null -eq $serviceKey) {
            $serviceKey = Get-CfServiceKey -InstanceName $instanceName -KeyName $keyName
        }
        
        if ($null -ne $serviceKey) {
            # Only extract credentials if not already extracted for CSV
            if ($null -eq $credentials) {
                $credentials = Get-BtpServiceKeyCredentials -ServiceKey $serviceKey
            }
            
            if ($null -ne $credentials) {
                $exported = Export-ServiceKeyToKeyVault -KeyVaultName $KeyVaultName -SubaccountId $subaccountId -Credentials $credentials
                
                if ($exported) {
                    Write-Log "Credentials exported to Key Vault for subaccount $subaccountId" -Level "SUCCESS"
                } else {
                    Write-Log "Failed to export credentials to Key Vault" -Level "WARNING"
                }
            } else {
                Write-Log "Failed to extract credentials from service key" -Level "WARNING"
            }
        } else {
            Write-Log "Failed to retrieve service key for export" -Level "WARNING"
        }
    }
    
    $successCount++
    Write-Log "Subaccount $subaccountId processed successfully" -Level "SUCCESS"
    
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
