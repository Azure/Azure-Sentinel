# discover-destinations.ps1
# Script to discover SAP BTP destinations prepared for Microsoft Sentinel.
# This script queries the BTP Destination Service using BTP CLI to find destinations
# with "Sentinel" in the name and exports them to a CSV file.
#
# Prerequisites:
# - SAP BTP CLI (btp) installed
# - BTP CLI login session established (btp login)
# - Appropriate permissions to read destinations
#
# Usage:
#   1. Run 'btp login' to authenticate
#   2. Execute:
#       .\discover-destinations.ps1 -SubaccountId "my-subaccount-guid"

# Parameters
param(
    [Parameter(Mandatory=$true, HelpMessage="SAP BTP Subaccount ID (GUID)")]
    [string]$SubaccountId,
    
    [Parameter(Mandatory=$false, HelpMessage="Filter pattern for destination names (default: 'Sentinel')")]
    [string]$NameFilter = "Sentinel",
    
    [Parameter(Mandatory=$false, HelpMessage="Path to export CSV file")]
    [string]$CsvPath = ".\destinations.csv",
    
    [Parameter(Mandatory=$false, HelpMessage="Default polling frequency in minutes for discovered destinations")]
    [int]$DefaultPollingFrequency = 1,
    
    [Parameter(Mandatory=$false, HelpMessage="Append to existing CSV instead of overwriting")]
    [switch]$AppendCsv
)

# Import Write-Log function from shared helper module
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\IntegrationSuiteHelpers.ps1" -Force

# Main script execution
Write-Log "======================================================================="
Write-Log "SAP Destination Discovery for Microsoft Sentinel"
Write-Log "======================================================================="
Write-Log "Subaccount ID: $SubaccountId"
Write-Log "Filter Pattern: *$NameFilter*"
Write-Log "Output CSV: $CsvPath"
Write-Log "======================================================================="

# Check if BTP CLI is installed
try {
    $btpVersion = btp --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "BTP CLI is not installed or not in PATH. Please install it first." -Level "ERROR"
        Write-Log "Download from: https://tools.hana.ondemand.com/#cloud" -Level "ERROR"
        exit 1
    }
    Write-Log "BTP CLI is installed: $btpVersion"
}
catch {
    Write-Log "BTP CLI is not installed or not in PATH. Please install it first." -Level "ERROR"
    Write-Log "Download from: https://tools.hana.ondemand.com/#cloud" -Level "ERROR"
    exit 1
}

# Step 1: Query Destinations using BTP CLI
Write-Log "======================================================================="
Write-Log "Step 1: Querying Destinations"
Write-Log "======================================================================="

$destinations = @()
try {
    Write-Log "Running: btp list connectivity/destination --subaccount $SubaccountId"
    
    # Query destinations using BTP CLI with JSON output
    $destListOutput = btp --format json list connectivity/destination --subaccount $SubaccountId 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Failed to query destinations: $destListOutput" -Level "ERROR"
        Write-Log "Please ensure you are logged in (btp login) and have permissions to read destinations." -Level "ERROR"
        exit 1
    }
    
    # Parse JSON output
    $destList = $destListOutput | ConvertFrom-Json
    
    Write-Log "Found $($destList.Count) total destination(s)"
    
    # Filter destinations containing the filter pattern (case-insensitive)
    # BTP CLI returns nested structure with destinationConfiguration.Name
    # Scan both Name and Description fields for the filter pattern
    foreach ($dest in $destList) {
        $destName = $dest.destinationConfiguration.Name
        $destDescription = $dest.destinationConfiguration.Description
        if (($destName -match $NameFilter) -or ($destDescription -match $NameFilter)) {
            $destinations += $dest
            $matchedField = if ($destName -match $NameFilter) { "name" } else { "description" }
            Write-Log "  Found matching destination: $destName (matched in $matchedField)" -Level "SUCCESS"
        }
    }
    
    Write-Log "Found $($destinations.Count) destination(s) matching pattern '*$NameFilter*'"
}
catch {
    Write-Log "Failed to query destinations: $_" -Level "ERROR"
    exit 1
}

if ($destinations.Count -eq 0) {
    Write-Log "No destinations found matching pattern '*$NameFilter*'" -Level "WARNING"
    Write-Log "Please create destinations with '$NameFilter' in the name to use with this tool." -Level "WARNING"
    exit 0
}

# Step 2: Export to CSV
Write-Log "======================================================================="
Write-Log "Step 2: Exporting to CSV"
Write-Log "======================================================================="

$csvData = @()
foreach ($dest in $destinations) {
    # Extract properties from nested destinationConfiguration structure
    $config = $dest.destinationConfiguration
    $destName = $config.Name
    $destType = $config.Type
    $destProxyType = $config.'jco.destination.proxy_type'
    if ([string]::IsNullOrWhiteSpace($destProxyType)) {
        $destProxyType = $config.ProxyType
    }
    $destAuthType = $config.'jco.destination.auth_type'
    if ([string]::IsNullOrWhiteSpace($destAuthType)) {
        $destAuthType = $config.Authentication
    }
    $destLocationId = $config.LocationId
    $destDescription = $config.Description
    
    # Build CSV row
    $csvData += [PSCustomObject]@{
        DestinationName = $destName
        Type = $destType
        LocationID = $destLocationId
        'Authorization Type' = $destAuthType
        ProxyType = $destProxyType
        Description = $destDescription
        PollingFrequencyInMinutes = $DefaultPollingFrequency
    }
}

try {
    if ($AppendCsv -and (Test-Path $CsvPath)) {
        # Load existing data and merge
        $existing = Import-Csv -Path $CsvPath -Delimiter ';'
        $existingNames = $existing | ForEach-Object { $_.DestinationName }
        $newDests = $csvData | Where-Object { $_.DestinationName -notin $existingNames }
        
        if ($newDests.Count -eq 0) {
            Write-Log "No new destinations to add (all already exist in CSV)" -Level "INFO"
        }
        else {
            $combined = $existing + $newDests
            $combined | Export-Csv -Path $CsvPath -Delimiter ';' -NoTypeInformation
            Write-Log "Appended $($newDests.Count) new destination(s) to $CsvPath" -Level "SUCCESS"
        }
    }
    else {
        $csvData | Export-Csv -Path $CsvPath -Delimiter ';' -NoTypeInformation
        Write-Log "Exported $($csvData.Count) destination(s) to $CsvPath" -Level "SUCCESS"
    }
}
catch {
    Write-Log "Failed to export CSV: $_" -Level "ERROR"
    exit 1
}

# Display CSV content
Write-Log ""
Write-Log "Discovered Destinations:"
Write-Log "------------------------"
foreach ($row in $csvData) {
    Write-Log "  $($row.DestinationName) ($($row.Type), $($row.ProxyType))"
}

# Summary
Write-Log "======================================================================="
Write-Log "Discovery Complete"
Write-Log "======================================================================="
Write-Log "Destinations found: $($destinations.Count)"
Write-Log "CSV exported to: $CsvPath"
Write-Log "======================================================================="

# Return discovered destinations for pipeline usage
return $csvData
