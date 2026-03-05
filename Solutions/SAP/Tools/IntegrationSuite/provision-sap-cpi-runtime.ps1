# provision-sap-cpi-runtime.ps1
# Script to provision SAP Process Integration Runtime service instance and service key.
#
# This script:
# 1. Checks if the service instance exists, creates it if not
# 2. Checks if the service key exists, creates it if not
# 3. Reads and returns the service key credentials
#
# Prerequisites:
# - Cloud Foundry CLI (cf) installed: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html
# - CF login session established (run 'cf login' before executing this script. Be aware that you may need to use S-User since SAP UID changes)
# - Appropriate permissions in SAP BTP to create services
# - SAP BTP entitlements for 'it-rt' (Process Integration Runtime) service
#
# Usage:
#   1. Run 'cf login -a <cf-api-endpoint>' to authenticate to Cloud Foundry
#   2. Target your org and space: 'cf target -o <org> -s <space>'
#   3. Execute:
#       .\provision-sap-cpi-runtime.ps1"

# Parameters
param(
    # Service Instance Configuration
    [Parameter(Mandatory=$false, HelpMessage="Name for the Process Integration Runtime service instance")]
    [string]$InstanceName = "cpi-sentinel-integration-rt",
    
    [Parameter(Mandatory=$false, HelpMessage="Service plan for Process Integration Runtime")]
    [string]$ServicePlan = "integration-flow",
    
    [Parameter(Mandatory=$false, HelpMessage="Name for the service key")]
    [string]$KeyName = "cpi-sentinel-integration-key"
)

# Import shared helper functions (includes New-CfServiceInstance and New-CfServiceKey)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module "$scriptPath\IntegrationSuiteHelpers.ps1" -Force

# Service name for Process Integration Runtime
$ServiceName = "it-rt"

# Main script execution
Write-Log "======================================================================="
Write-Log "SAP Process Integration Runtime - Service Provisioning"
Write-Log "======================================================================="
Write-Log "Service: $ServiceName"
Write-Log "Plan: $ServicePlan"
Write-Log "Instance Name: $InstanceName"
Write-Log "Key Name: $KeyName"
Write-Log "======================================================================="

# Check if CF CLI is installed
try {
    $cfVersion = cf --version 2>&1
    Write-Log "CF CLI is installed: $cfVersion"
}
catch {
    Write-Log "CF CLI is not installed or not in PATH. Please install it first." -Level "ERROR"
    Write-Log "Download from: https://docs.cloudfoundry.org/cf-cli/install-go-cli.html" -Level "ERROR"
    exit 1
}

# Verify CF is logged in and targeting an org/space
try {
    $cfTarget = cf target 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Not logged in to Cloud Foundry. Please run 'cf login' first." -Level "ERROR"
        exit 1
    }
    Write-Log "CF Target: $cfTarget"
}
catch {
    Write-Log "Error checking CF target: $_" -Level "ERROR"
    exit 1
}

# Step 1: Create service instance (if not exists)
Write-Log "======================================================================="
Write-Log "Step 1: Checking/Creating Service Instance"
Write-Log "======================================================================="

$serviceCreated = New-CfServiceInstance -InstanceName $InstanceName -Service $ServiceName -Plan $ServicePlan

if (-not $serviceCreated) {
    Write-Log "Failed to create or verify service instance '$InstanceName'" -Level "ERROR"
    exit 1
}

# Step 2: Create service key (if not exists)
Write-Log "======================================================================="
Write-Log "Step 2: Checking/Creating Service Key"
Write-Log "======================================================================="

$keyCreated = New-CfServiceKey -InstanceName $InstanceName -KeyName $KeyName

if (-not $keyCreated) {
    Write-Log "Failed to create or verify service key '$KeyName'" -Level "ERROR"
    exit 1
}

# Step 3: Retrieve and parse service key
Write-Log "======================================================================="
Write-Log "Step 3: Retrieving Service Key Credentials"
Write-Log "======================================================================="

$rawKeyOutput = cf service-key $InstanceName $KeyName 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Log "Failed to retrieve service key: $rawKeyOutput" -Level "ERROR"
    exit 1
}

# Extract JSON from the output (skip header lines)
$jsonLines = @()
$jsonStarted = $false

foreach ($line in $rawKeyOutput) {
    if ($line -match '^\s*\{') {
        $jsonStarted = $true
    }
    if ($jsonStarted) {
        $jsonLines += $line
    }
}

if ($jsonLines.Count -eq 0) {
    Write-Log "No JSON found in service key output" -Level "ERROR"
    exit 1
}

$jsonString = $jsonLines -join "`n"
$serviceKey = $null

try {
    $serviceKey = $jsonString | ConvertFrom-Json
    Write-Log "Service key parsed successfully" -Level "SUCCESS"
}
catch {
    Write-Log "Failed to parse service key JSON: $_" -Level "ERROR"
    Write-Log "Raw output: $jsonString" -Level "ERROR"
    exit 1
}

# Validate and extract credentials
$credentials = Get-IntegrationSuiteCredentials -ServiceKeyJson $jsonString

if ($null -eq $credentials) {
    Write-Log "Failed to extract valid credentials from service key" -Level "ERROR"
    exit 1
}

Write-Log "Credentials extracted successfully" -Level "SUCCESS"
Write-Log "  Integration Server URL: $($credentials.IntegrationServerUrl)"
Write-Log "  Token Endpoint: $($credentials.TokenEndpoint)"
Write-Log "  Client ID: $($credentials.ClientId)"

# Summary
Write-Log "======================================================================="
Write-Log "Provisioning Complete"
Write-Log "======================================================================="
Write-Log "Service Instance: $InstanceName"
Write-Log "Service Key: $KeyName"
Write-Log "Integration Server URL: $($credentials.IntegrationServerUrl)"
Write-Log "======================================================================="

# Return credentials object for pipeline usage
return $credentials
