# Export-BtpSubaccounts.ps1
# Retrieves BTP subaccounts using BTP CLI and exports them to subaccounts.csv
# This script helps populate the CSV file required by Add-BtpSubaccounts.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$BtpUsername = $env:BTP_USERNAME,
    
    [Parameter(Mandatory=$false)]
    [SecureString]$BtpPassword,
    
    [Parameter(Mandatory=$false)]
    [string]$BtpSubdomain = "$env:BTP_SUBDOMAIN",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputCsvPath = ".\subaccounts.csv",
    
    [Parameter(Mandatory=$false)]
    [switch]$Append
)

# Import helper functions
. "$PSScriptRoot\BtpHelpers.ps1"

# Main script execution
try {
    Write-Log "Starting BTP subaccounts export process" -Level "INFO"
    Write-Host ""
    
    # Check prerequisites
    if (-not (Test-BtpCli)) {
        exit 1
    }
    
    # Get and validate BTP credentials
    $credentials = Get-BtpCredentials -Username $BtpUsername -Password $BtpPassword -Subdomain $BtpSubdomain
    if ($null -eq $credentials) {
        Write-Log "Failed to obtain BTP credentials" -Level "ERROR"
        exit 1
    }
    
    $BtpUsername = $credentials.Username
    $BtpPassword = $credentials.Password
    $BtpSubdomain = $credentials.Subdomain
    
    # Check if user is logged in to BTP CLI
    Write-Log "Checking BTP CLI login status..."
    $loginCheck = btp list accounts/global-account 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Not logged in to BTP CLI. Attempting to login..." -Level "WARNING"
        
        # Attempt to login with provided credentials
        if (-not (Invoke-BtpLogin -Username $BtpUsername -Password $BtpPassword -Subdomain $BtpSubdomain)) {
            Write-Log "Failed to login to BTP CLI" -Level "ERROR"
            exit 1
        }
    }
    else {
        Write-Log "Already logged in to BTP CLI" -Level "SUCCESS"
    }
    
    # Get list of all subaccounts
    $btpSubaccounts = Get-BtpSubaccounts
    
    if ($null -eq $btpSubaccounts -or $btpSubaccounts.Count -eq 0) {
        Write-Log "No subaccounts found in BTP global account" -Level "WARNING"
        exit 0
    }
    
    # Collect subaccount information with CF details
    $exportSubaccounts = @()
    $skippedSubaccounts = @()
    $processedCount = 0
    
    foreach ($subaccount in $btpSubaccounts) {
        $processedCount++
        $subaccountId = $subaccount.guid
        $subaccountName = $subaccount.displayName
        
        Write-Log "[$processedCount/$($btpSubaccounts.Count)] Processing subaccount: $subaccountName (ID: $subaccountId)"
        
        # Get Cloud Foundry details
        $cfDetails = Get-BtpSubaccountCfDetails -SubaccountId $subaccountId
        
        if ($null -eq $cfDetails) {
            Write-Log "  WARNING: Subaccount '$subaccountName' does not have Cloud Foundry enabled - cannot be onboarded" -Level "WARNING"
            $skippedSubaccounts += [PSCustomObject]@{
                SubaccountId = $subaccountId
                SubaccountName = $subaccountName
                Reason = "Cloud Foundry not enabled"
            }
            continue
        }
        
        Write-Log "  Cloud Foundry Org: $($cfDetails.OrgName)"
        Write-Log "  CF API Endpoint: $($cfDetails.ApiEndpoint)"
        
        # Note: Space information requires CF CLI authentication
        Write-Log "  Note: Space information requires CF CLI authentication. Using placeholder." -Level "WARNING"
        Write-Log "  Please verify that spaces exist in this org and update CSV if needed." -Level "WARNING"
        
        # Create subaccount entry with default space placeholder
        $subaccountEntry = [PSCustomObject]@{
            SubaccountId = $subaccountId
            DisplayName = $subaccountName
            "cf-api-endpoint" = $cfDetails.ApiEndpoint
            "cf-org-name" = $cfDetails.OrgName
            "cf-space-name" = "dev"  # Common default - user should verify/update
        }
        
        $exportSubaccounts += $subaccountEntry
        Write-Log "  Added subaccount to export list (verify space name in CSV)" -Level "SUCCESS"
    }
    
    # Report summary
    Write-Host ""
    Write-Log "Processing complete!" -Level "INFO"
    Write-Log "  Total subaccounts found: $($btpSubaccounts.Count)" -Level "INFO"
    Write-Log "  Subaccounts ready for export: $($exportSubaccounts.Count)" -Level "SUCCESS"
    Write-Log "  Subaccounts skipped: $($skippedSubaccounts.Count)" -Level "WARNING"
    
    # Display skipped subaccounts
    if ($skippedSubaccounts.Count -gt 0) {
        Write-Host ""
        Write-Log "Skipped subaccounts:" -Level "WARNING"
        foreach ($skipped in $skippedSubaccounts) {
            Write-Host "  - $($skipped.SubaccountName) (ID: $($skipped.SubaccountId)) - $($skipped.Reason)" -ForegroundColor Yellow
        }
    }
    
    # Check if we found any subaccounts to export
    if ($exportSubaccounts.Count -eq 0) {
        Write-Host ""
        Write-Log "No subaccounts available for export" -Level "WARNING"
        exit 0
    }
    
    # Export to CSV using helper function
    Write-Host ""
    if (Export-BtpSubaccountsCsv -Subaccounts $exportSubaccounts -CsvPath $OutputCsvPath -Append:$Append) {
        Write-Host ""
        Write-Log "Export complete!" -Level "SUCCESS"
        Write-Log "CSV file location: $OutputCsvPath" -Level "INFO"
        Write-Host ""
        Write-Host "IMPORTANT:" -ForegroundColor Yellow
        Write-Host "  The exported CSV uses 'dev' as default space name." -ForegroundColor Yellow
        Write-Host "  Please verify and update space names in the CSV before running Add-BtpSubaccounts.ps1" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "  1. Review and edit the CSV file: $OutputCsvPath" -ForegroundColor White
        Write-Host "  2. Verify/update the cf-space-name column for each subaccount" -ForegroundColor White
        Write-Host "  3. Run Add-BtpSubaccounts.ps1 to create Sentinel connections" -ForegroundColor White
        Write-Host ""
    }
    else {
        Write-Log "Failed to export subaccounts to CSV" -Level "ERROR"
        exit 1
    }
}
catch {
    Write-Log "An error occurred during export: $_" -Level "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" -Level "ERROR"
    exit 1
}
