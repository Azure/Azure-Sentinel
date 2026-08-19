<#
.SYNOPSIS
    Ingests sample data into the custom table via DCR ingestion API.
.DESCRIPTION
    Sends sample JSON records to the Data Collection Endpoint using the
    Logs Ingestion API to validate the pipeline works end-to-end.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$DCEEndpoint,

    [Parameter(Mandatory=$true)]
    [string]$DCRImmutableId,

    [Parameter(Mandatory=$true)]
    [string]$StreamName,

    [Parameter(Mandatory=$false)]
    [string]$SampleDataFile,

    [Parameter(Mandatory=$false)]
    [int]$RecordCount = 5
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== Ingesting Sample Data ===`n"
Write-Host "DCE: $DCEEndpoint"
Write-Host "DCR: $DCRImmutableId"
Write-Host "Stream: $StreamName"

# Get access token
$token = az account get-access-token --resource "https://monitor.azure.com/" --query "accessToken" -o tsv

if (-not $token) {
    Write-Host "❌ Failed to get access token. Ensure you are logged in."
    exit 1
}

# Prepare data
if ($SampleDataFile -and (Test-Path $SampleDataFile)) {
    $body = Get-Content $SampleDataFile -Raw
    Write-Host "Using data from file: $SampleDataFile"
} else {
    # Generate sample records
    $records = @()
    for ($i = 1; $i -le $RecordCount; $i++) {
        $records += @{
            TimeGenerated = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
            RawData = "Sample record $i from Sentinel Data Connector and Agent Builder - $(Get-Date -Format 'HH:mm:ss')"
        }
        Start-Sleep -Milliseconds 100
    }
    $body = $records | ConvertTo-Json -AsArray
    Write-Host "Generated $RecordCount sample records."
}

# Send to ingestion API
$uri = "$DCEEndpoint/dataCollectionRules/$DCRImmutableId/streams/${StreamName}?api-version=2023-01-01"

Write-Host "`nSending data to ingestion API..."

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $body
    Write-Host "✅ Data ingested successfully!"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 204) {
        Write-Host "✅ Data ingested successfully (204 No Content)."
    } else {
        Write-Host "❌ Ingestion failed: $($_.Exception.Message)"
        Write-Host "   Status: $statusCode"
        exit 1
    }
}

# Verify with KQL (wait for ingestion lag)
Write-Host "`n⏱️  Data may take 5-10 minutes to appear in the workspace."
Write-Host "Verify with KQL:"
Write-Host "   $($StreamName -replace 'Custom-','') | where TimeGenerated > ago(24h) | take 10"
Write-Host "`n=== Ingestion Complete ===`n"
