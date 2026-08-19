<#
.SYNOPSIS
    Sentinel Data Connector and Agent Builder — sample-data ingestion engine (Phase 3 redesign).

.DESCRIPTION
    End-to-end per-table ingestion engine inspired by sentinel-logseeder but
    purpose-built for this repo. For a single (table, schema, records) triple,
    this script:

      1. Detects whether the target is a custom *_CL table or a native
         LIA-supported table (CommonSecurityLog, Syslog, SecurityEvent,
         WindowsEvent, ASim*, AWS*, GCP*, CrowdStrike*, ThreatIntel*, etc. —
         see https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview#supported-tables).
         * Custom (_CL suffix): PUTs the table schema to /tables API.
         * Native (no _CL):     skips the workspace tables PUT — the table
                                is platform-owned.
      2. Ensures a Data Collection Endpoint (DCE) exists in the resource group.
      3. Deploys a per-table Data Collection Rule (DCR) using the generic
         templates/dcr-per-table.json template. The DCR always declares an
         inbound stream named "Custom-<table>" (Azure requires the 'Custom-'
         prefix on customer-declared streams). The dataFlow's outputStream is:
            * "Custom-<table>"        for custom *_CL targets
            * "Microsoft-<NativeTable>" for native LIA-supported targets
      4. Grants 'Monitoring Metrics Publisher' on the DCR to the current
         signed-in principal (idempotent).
      5. Acquires an AAD bearer token for https://monitor.azure.com/.
      6. POSTs the records (batched) to
         {logsIngestionEndpoint}/dataCollectionRules/{immutableId}/streams/{streamName}?api-version=2023-01-01
         retrying transient 403/404 from DCR propagation.

    The orchestrator (Invoke-AttackScenarioIngestion.ps1) calls this once per
    table after generating synthetic records.

.PARAMETER ResourceGroupName
    Resource group hosting the LA workspace + DCE + DCRs.

.PARAMETER WorkspaceName
    Log Analytics workspace name.

.PARAMETER SchemaPath
    Path to schemas/<Table>.json (column manifest). The 'tableName' field
    determines routing: ends in _CL -> custom table; otherwise -> native
    LIA-supported table (no workspace table PUT, outputStream='Microsoft-<Table>').

.PARAMETER RecordsJsonPath
    Path to a JSON file containing an array of records to ingest. Each record
    must have keys matching the columns in SchemaPath. A TimeGenerated string
    (ISO-8601 UTC) is required on every record.

.PARAMETER DceName
    Data Collection Endpoint name. Created if missing. Default: 'dce-saa-shared'.

.PARAMETER Location
    Azure region. If not specified, loaded from config/workspace.json (Phase 2 onboarding).

.PARAMETER SkipRbac
    Skip the Monitoring Metrics Publisher role assignment step (use when the
    caller has pre-provisioned RBAC, e.g., in CI).

.PARAMETER DryRun
    Build everything (table, DCE, DCR) but skip the records POST. Useful for
    deployment-only validation.

.OUTPUTS
    Hashtable summarizing the operation (table name, dcr id, immutableId,
    endpoint, records sent, status).
#>

param(
    [Parameter(Mandatory=$true)]  [string]$ResourceGroupName,
    [Parameter(Mandatory=$true)]  [string]$WorkspaceName,
    [Parameter(Mandatory=$true)]  [string]$SchemaPath,
    [Parameter(Mandatory=$true)]  [string]$RecordsJsonPath,
    [Parameter(Mandatory=$false)] [string]$DceName  = "dce-saa-shared",
    [Parameter(Mandatory=$false)] [string]$Location,
    [Parameter(Mandatory=$false)] [switch]$SkipRbac,
    [Parameter(Mandatory=$false)] [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Per Phase 2 onboarding: region is persisted in config/workspace.json. Resolve if not passed.
if (-not $Location) {
    $workspaceConfigPath = Join-Path $PSScriptRoot "../config/workspace.json"
    if (Test-Path $workspaceConfigPath) {
        $wsCfg = Get-Content $workspaceConfigPath -Raw | ConvertFrom-Json
        $Location = $wsCfg.region
    }
}
if (-not $Location) { throw "Location is not set. Pass -Location explicitly or populate config/workspace.json." }

# -------- Helpers ------------------------------------------------------------
function Write-Step($msg)   { Write-Host "`n=== $msg ===`n" -ForegroundColor Cyan }
function Write-Ok($msg)     { Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Info($msg)   { Write-Host "   $msg" }
function Write-Warn2($msg)  { Write-Host "⚠️  $msg" -ForegroundColor Yellow }

function Invoke-AzRestJson {
    param([string]$Method, [string]$Url, [string]$Body)
    if ($Body) {
        $tmp = New-TemporaryFile
        try {
            $Body | Out-File -FilePath $tmp.FullName -Encoding utf8 -NoNewline
            $raw = az rest --method $Method --url $Url --body "@$($tmp.FullName)" --headers "Content-Type=application/json" 2>&1
        } finally { Remove-Item $tmp.FullName -ErrorAction SilentlyContinue }
    } else {
        $raw = az rest --method $Method --url $Url 2>&1
    }
    if ($LASTEXITCODE -ne 0) { throw "az rest $Method $Url failed: $raw" }
    if ([string]::IsNullOrWhiteSpace($raw)) { return $null }
    return ($raw | ConvertFrom-Json -ErrorAction SilentlyContinue)
}

# -------- 0. Load + validate schema ------------------------------------------
Write-Step "Loading schema & records"
if (-not (Test-Path $SchemaPath))      { throw "Schema not found: $SchemaPath" }
if (-not (Test-Path $RecordsJsonPath)) { throw "Records not found: $RecordsJsonPath" }

$schema  = Get-Content $SchemaPath      -Raw | ConvertFrom-Json
$records = @(Get-Content $RecordsJsonPath -Raw | ConvertFrom-Json)

if (-not $schema.tableName) { throw "Schema missing 'tableName' field: $SchemaPath" }
if (-not $schema.columns)   { throw "Schema missing 'columns' field:   $SchemaPath" }

$tableName  = $schema.tableName        # e.g. LightningTier0Nodes_CL  OR  CommonSecurityLog (native)
# Detect native LIA-supported tables vs custom *_CL tables.
# Custom tables must end in _CL. Native tables don't.
# For native targets we MUST NOT call the workspace tables PUT (table is platform-owned)
# and the DCR's outputStream must be 'Microsoft-<TableName>' even though the inbound
# stream the orchestrator POSTs to stays 'Custom-<TableName>' (Azure DCR rule:
# customer-declared streams must use 'Custom-' prefix; only the outputStream changes).
# See https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview#supported-tables
$isNativeTable = -not ($tableName -match '_CL$')
$streamName  = "Custom-$tableName"     # inbound stream (POST target) — always Custom-* per Azure
$outputStreamName = if ($isNativeTable) { "Microsoft-$tableName" } else { "" }   # empty -> template defaults to streamName
$dcrName    = "dcr-saa-$($tableName.ToLower())"
$columns    = @($schema.columns)

# Ensure TimeGenerated column exists in schema (DCRs require it)
$hasTimeGen = $columns | Where-Object { $_.name -eq "TimeGenerated" }
if (-not $hasTimeGen) { throw "Schema $tableName is missing required column 'TimeGenerated'" }

$recordCount = @($records).Count
Write-Ok "Schema: $tableName ($($columns.Count) columns)"
Write-Ok "Records to ingest: $recordCount"
Write-Info "Stream name (inbound): $streamName"
if ($isNativeTable) {
    Write-Info "Native target: outputStream='Microsoft-$tableName' (LIA-supported native table — skipping workspace table PUT)"
} else {
    Write-Info "Custom target: outputStream='$streamName' (will PUT custom table schema)"
}
Write-Info "DCR name:    $dcrName"

# -------- 1. Resolve workspace + subscription --------------------------------
Write-Step "Resolving Azure context"
$subId = az account show --query id -o tsv
if (-not $subId) { throw "Not logged in. Run 'az login'." }
Write-Ok "Subscription: $subId"

$wsResourceId = az monitor log-analytics workspace show `
    --resource-group $ResourceGroupName `
    --workspace-name $WorkspaceName `
    --query id -o tsv 2>$null
if (-not $wsResourceId) { throw "Workspace '$WorkspaceName' not found in RG '$ResourceGroupName'." }
Write-Ok "Workspace: $wsResourceId"

# -------- 2. Ensure custom table (skip for native LIA-supported tables) ------
if ($isNativeTable) {
    Write-Step "Skipping workspace table PUT — '$tableName' is a native LIA-supported table (platform-owned)"
} else {
    Write-Step "Ensuring custom table '$tableName'"
    $tableBody = @{
        properties = @{
            schema = @{
                name    = $tableName
                columns = $columns
            }
            retentionInDays = 30
            plan            = "Analytics"
        }
    } | ConvertTo-Json -Depth 20 -Compress

    $tableUrl = "$wsResourceId/tables/${tableName}?api-version=2022-10-01"
    $null = Invoke-AzRestJson -Method PUT -Url $tableUrl -Body $tableBody
    Write-Ok "Table '$tableName' created/updated."
}

# -------- 3. Ensure DCE -------------------------------------------------------
Write-Step "Ensuring DCE '$DceName'"
$dceJson = az monitor data-collection endpoint show `
    --name $DceName --resource-group $ResourceGroupName --output json 2>$null
if (-not $dceJson) {
    az monitor data-collection endpoint create `
        --name $DceName `
        --resource-group $ResourceGroupName `
        --location $Location `
        --public-network-access Enabled `
        --output none
    $dceJson = az monitor data-collection endpoint show `
        --name $DceName --resource-group $ResourceGroupName --output json
    Write-Ok "DCE '$DceName' created."
} else {
    Write-Ok "DCE '$DceName' already exists."
}

# Wait for DCE provisioningState=Succeeded before deploying DCR.
# Without this, DCR deployment can race against an unready DCE and the
# az CLI sits indefinitely on "Provisioning in progress. Waiting for completion."
$dceReadyTimeoutSec = 120
$dceReadyPollSec    = 5
$dceReadyElapsed    = 0
$dceState           = ($dceJson | ConvertFrom-Json).provisioningState
while ($dceState -ne 'Succeeded' -and $dceReadyElapsed -lt $dceReadyTimeoutSec) {
    if ($dceState -in @('Failed','Canceled')) {
        throw "DCE '$DceName' provisioning ended in state '$dceState'."
    }
    Write-Info "DCE '$DceName' provisioningState='$dceState' (waited ${dceReadyElapsed}s); polling..."
    Start-Sleep -Seconds $dceReadyPollSec
    $dceReadyElapsed += $dceReadyPollSec
    $dceJson  = az monitor data-collection endpoint show `
        --name $DceName --resource-group $ResourceGroupName --output json 2>$null
    if (-not $dceJson) { continue }
    $dceState = ($dceJson | ConvertFrom-Json).provisioningState
}
if ($dceState -ne 'Succeeded') {
    throw "DCE '$DceName' not Succeeded after ${dceReadyTimeoutSec}s (last state: '$dceState'). Aborting DCR deployment."
}
Write-Ok "DCE '$DceName' provisioningState=Succeeded."

$dce = $dceJson | ConvertFrom-Json
$dceId       = $dce.id
$dceEndpoint = $dce.logsIngestion.endpoint
Write-Info "DCE id:       $dceId"
Write-Info "DCE endpoint: $dceEndpoint"

# -------- 4. Deploy DCR via T7 template --------------------------------------
Write-Step "Deploying DCR '$dcrName'"
$templatePath = Join-Path $PSScriptRoot "..\templates\dcr-per-table.json"
$templatePath = (Resolve-Path $templatePath).Path
Write-Info "Template: $templatePath"

# Inline parameters file (compact, deterministic)
$paramsObj = @{
    '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#"
    contentVersion = "1.0.0.0"
    parameters     = @{
        dcrName             = @{ value = $dcrName }
        location            = @{ value = $Location }
        workspaceResourceId = @{ value = $wsResourceId }
        dceResourceId       = @{ value = $dceId }
        streamName          = @{ value = $streamName }
        outputStreamName    = @{ value = $outputStreamName }
        columns             = @{ value = $columns }
        tags                = @{ value = @{
            project = "sentinel-data-connector-agent-builder"
            phase   = "3"
            table   = $tableName
        }}
    }
}
$paramsFile = New-TemporaryFile
$paramsPath = "$($paramsFile.FullName).json"
Move-Item $paramsFile.FullName $paramsPath
$paramsObj | ConvertTo-Json -Depth 20 | Out-File -FilePath $paramsPath -Encoding utf8

try {
    $deployName = "saa-dcr-$($tableName.ToLower())-$(Get-Date -Format 'yyyyMMddHHmmss')"
    $deployJson = az deployment group create `
        --name $deployName `
        --resource-group $ResourceGroupName `
        --template-file $templatePath `
        --parameters "@$paramsPath" `
        --output json
    if ($LASTEXITCODE -ne 0) { throw "DCR deployment failed for $dcrName" }
} finally {
    Remove-Item $paramsPath -ErrorAction SilentlyContinue
}

$deploy = $deployJson | ConvertFrom-Json
$dcrId          = $deploy.properties.outputs.dcrId.value
$dcrImmutableId = $deploy.properties.outputs.dcrImmutableId.value
$logsEndpoint   = $deploy.properties.outputs.logsIngestionEndpoint.value
Write-Ok "DCR '$dcrName' deployed."
Write-Info "DCR id:          $dcrId"
Write-Info "Immutable id:    $dcrImmutableId"
Write-Info "Logs endpoint:   $logsEndpoint"

# -------- 5. RBAC: Monitoring Metrics Publisher at RG scope ------------------
# Per BUGFIX-RBAC-RG-Scope: role is granted at RESOURCE GROUP scope, not at
# per-DCR scope. RG-scope grants are inherited by every current and future DCR
# in the RG at creation time, so newly-deployed DCRs never hit the Azure
# data-plane cold-start "no access" negative-cache (which can hold for 15+ min
# and produce a multi-attempt 403 retry storm on fresh DCRs).
#
# The orchestrator (Invoke-AttackScenarioIngestion.ps1) calls Grant-IngestionRbac.ps1
# ONCE before this engine runs, then passes -SkipRbac on every per-table call.
# When -SkipRbac is NOT set (engine invoked standalone), we run the helper
# inline so direct callers also get the RG-scope behaviour.
if (-not $SkipRbac) {
    & "$PSScriptRoot/Grant-IngestionRbac.ps1" -ResourceGroupName $ResourceGroupName | Out-Null
} else {
    Write-Warn2 "SkipRbac set; assuming caller has granted 'Monitoring Metrics Publisher' at RG scope on $ResourceGroupName"
}

# -------- 6. Dry-run exit ----------------------------------------------------
if ($DryRun) {
    Write-Step "DryRun: skipping records POST"
    return @{
        TableName        = $tableName
        StreamName       = $streamName
        DcrId            = $dcrId
        DcrImmutableId   = $dcrImmutableId
        LogsEndpoint     = $logsEndpoint
        RecordsRequested = $recordCount
        RecordsSent      = 0
        Status           = "DryRun"
    }
}

# -------- 7. Acquire AAD token -----------------------------------------------
Write-Step "Acquiring AAD token for monitor.azure.com"
$tokenRaw = az account get-access-token --resource "https://monitor.azure.com/" -o json
if ($LASTEXITCODE -ne 0) { throw "Token acquisition failed" }
$token = ($tokenRaw | ConvertFrom-Json).accessToken
Write-Ok "Token acquired (length=$($token.Length))"

# -------- 8. POST records (with DCR-propagation retry) -----------------------
Write-Step "POSTing $recordCount record(s) to $streamName"
$postUrl = "$logsEndpoint/dataCollectionRules/$dcrImmutableId/streams/${streamName}?api-version=2023-01-01"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type"  = "application/json"
}

# Batch size guardrail (Logs Ingestion API: <=1MB / <=500K records per call).
# 51 records / table fits easily into a single call; chunk at 200 for safety.
$batchSize = 200
$batches   = [System.Collections.ArrayList]::new()
for ($i = 0; $i -lt $recordCount; $i += $batchSize) {
    [void]$batches.Add(@($records[$i..([Math]::Min($i+$batchSize-1, $recordCount-1))]))
}

$sent     = 0
$maxRetry = 18
foreach ($batch in $batches) {
    # Force JSON array shape even for single-record batches (Logs Ingestion API requires array).
    # ConvertTo-Json unwraps single-element arrays by default; manually wrap when count==1.
    if ($batch.Count -eq 1) {
        $bodyJson = "[" + ($batch[0] | ConvertTo-Json -Depth 20 -Compress) + "]"
    } else {
        $bodyJson = ConvertTo-Json -InputObject $batch -Depth 20 -Compress
    }
    $attempt  = 0
    while ($true) {
        $attempt++
        try {
            $resp = Invoke-WebRequest -Method POST -Uri $postUrl -Headers $headers `
                -Body $bodyJson -ContentType "application/json" -UseBasicParsing -ErrorAction Stop
            if ($resp.StatusCode -eq 204 -or $resp.StatusCode -eq 200) {
                $sent += $batch.Count
                Write-Ok "Batch of $($batch.Count) accepted (HTTP $($resp.StatusCode))."
                break
            }
            throw "Unexpected status code $($resp.StatusCode)"
        } catch {
            $errMsg = $_.Exception.Message
            $isPropagating =
                $errMsg -match "403" -or
                $errMsg -match "404" -or
                $errMsg -match "AuthenticationFailed" -or
                $errMsg -match "AuthorizationFailed" -or
                $errMsg -match "DataCollectionRuleNotFound"
            if ($isPropagating -and $attempt -le $maxRetry) {
                $delay = [Math]::Min(60, [Math]::Pow(2, $attempt))
                Write-Warn2 "Attempt $attempt/$maxRetry hit propagation error ($errMsg). Sleeping ${delay}s..."
                Start-Sleep -Seconds $delay
                continue
            }
            throw "POST failed after $attempt attempt(s): $errMsg"
        }
    }
}

# -------- 9. Summary ---------------------------------------------------------
Write-Step "Ingestion complete: $tableName"
Write-Ok "Records sent: $sent / $recordCount"
Write-Info "Visible in workspace after ~2-10 minutes."
Write-Info "Verify with: union ${tableName} | where TimeGenerated > ago(24h) | count"

return @{
    TableName        = $tableName
    IsNativeTable    = $isNativeTable
    StreamName       = $streamName
    OutputStream     = $(if ($isNativeTable) { "Microsoft-$tableName" } else { $streamName })
    DcrId            = $dcrId
    DcrImmutableId   = $dcrImmutableId
    LogsEndpoint     = $logsEndpoint
    RecordsRequested = $recordCount
    RecordsSent      = $sent
    Status           = $(if ($sent -eq $recordCount) { "Success" } elseif ($sent -eq 0) { "Failed" } else { "Partial" })
}
