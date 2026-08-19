<#
.SYNOPSIS
    Sets up data ingestion infrastructure (custom table, DCE, DCR).
.DESCRIPTION
    Creates a custom log table in the LA workspace, provisions a Data Collection
    Endpoint (DCE) and Data Collection Rule (DCR) for ISV data ingestion.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory=$true)]
    [string]$WorkspaceName,

    [Parameter(Mandatory=$true)]
    [string]$TableName,

    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus2",

    [Parameter(Mandatory=$false)]
    [string]$SchemaFile,

    [Parameter(Mandatory=$false)]
    [string]$TransformKql = "source | extend TimeGenerated = now()"
)

$ErrorActionPreference = "Stop"

$fullTableName = "${TableName}_CL"
$dceName = "dce-$($TableName.ToLower())"
$dcrName = "dcr-$($TableName.ToLower())"
$streamName = "Custom-${fullTableName}"

# 1. Create custom table
Write-Host "`n=== Creating Custom Table: $fullTableName ===`n"

if ($SchemaFile -and (Test-Path $SchemaFile)) {
    $schema = Get-Content $SchemaFile -Raw
} else {
    # Default minimal schema
    $schema = @"
{
  "properties": {
    "schema": {
      "name": "$fullTableName",
      "columns": [
        {"name": "TimeGenerated", "type": "datetime"},
        {"name": "RawData", "type": "string"}
      ]
    },
    "retentionInDays": 90,
    "plan": "Analytics"
  }
}
"@
}

$wsResourceId = az monitor log-analytics workspace show `
    --resource-group $ResourceGroupName `
    --workspace-name $WorkspaceName `
    --query "id" -o tsv

az rest --method PUT `
    --url "${wsResourceId}/tables/${fullTableName}?api-version=2022-10-01" `
    --body $schema `
    --output none 2>$null

Write-Host "✅ Table '$fullTableName' created/updated."

# 2. Create Data Collection Endpoint
Write-Host "`n=== Creating Data Collection Endpoint ===`n"

$dceExists = az monitor data-collection endpoint show `
    --name $dceName `
    --resource-group $ResourceGroupName `
    --output json 2>$null

if ($dceExists) {
    $dce = $dceExists | ConvertFrom-Json
    Write-Host "✅ DCE '$dceName' already exists."
} else {
    az monitor data-collection endpoint create `
        --name $dceName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --public-network-access "Enabled" `
        --output none
    $dce = az monitor data-collection endpoint show `
        --name $dceName `
        --resource-group $ResourceGroupName `
        --output json | ConvertFrom-Json
    Write-Host "✅ DCE '$dceName' created."
}

$dceEndpoint = $dce.logsIngestion.endpoint
$dceId = $dce.id
Write-Host "   Endpoint: $dceEndpoint"

# 3. Create Data Collection Rule
Write-Host "`n=== Creating Data Collection Rule ===`n"

$dcrBody = @"
{
  "location": "$Location",
  "properties": {
    "dataCollectionEndpointId": "$dceId",
    "streamDeclarations": {
      "$streamName": {
        "columns": [
          {"name": "TimeGenerated", "type": "datetime"},
          {"name": "RawData", "type": "string"}
        ]
      }
    },
    "destinations": {
      "logAnalytics": [
        {
          "workspaceResourceId": "$wsResourceId",
          "name": "workspace"
        }
      ]
    },
    "dataFlows": [
      {
        "streams": ["$streamName"],
        "destinations": ["workspace"],
        "transformKql": "$TransformKql",
        "outputStream": "$streamName"
      }
    ]
  }
}
"@

az rest --method PUT `
    --url "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$ResourceGroupName/providers/Microsoft.Insights/dataCollectionRules/${dcrName}?api-version=2022-06-01" `
    --body $dcrBody `
    --output none 2>$null

$dcr = az monitor data-collection rule show `
    --name $dcrName `
    --resource-group $ResourceGroupName `
    --output json | ConvertFrom-Json

Write-Host "✅ DCR '$dcrName' created."
Write-Host "   Immutable ID: $($dcr.immutableId)"

# 4. Output summary
Write-Host "`n=== Data Ingestion Setup Complete ===`n"
Write-Host "Table: $fullTableName"
Write-Host "DCE Endpoint: $dceEndpoint"
Write-Host "DCR Immutable ID: $($dcr.immutableId)"
Write-Host "Stream: $streamName"
Write-Host "`nNext step: Use Ingest-SampleData.ps1 to send test data.`n"

return @{
    TableName = $fullTableName
    DCEEndpoint = $dceEndpoint
    DCRImmutableId = $dcr.immutableId
    StreamName = $streamName
}
