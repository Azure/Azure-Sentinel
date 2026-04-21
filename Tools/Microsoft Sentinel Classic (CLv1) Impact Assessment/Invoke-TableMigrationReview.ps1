#Requires -Version 7.0
#Requires -Modules @{ ModuleName = 'Az.Accounts'; ModuleVersion = '2.13.0' }

<#
.SYNOPSIS
    Discover classic custom log tables, assess dependency impact, and map to Content Hub solutions.

.DESCRIPTION
    Interactive PowerShell script that mirrors the Table Migration Manager web app.

    Step 1 - Discover classic V1 custom log tables (CLv1) in a Microsoft Sentinel workspace.
    Step 2 - Assess impact across Analytics Rules, Workbooks, Hunting Queries, Parsers,
             Saved Searches, SOAR Playbooks, and Data Collection Rules.
    Step 3 - Map classic tables to Content Hub solutions and classify each connector as
             CCF (Codeless Connector Framework), Azure Functions, Platform, or Unknown.
             Flag legacy Azure Functions connectors that have no CCF equivalent.

    Outputs: pipeline objects, per-step CSV files, a combined JSON file, and a
    self-contained HTML report.

.PARAMETER SubscriptionId
    Azure subscription containing the Sentinel workspace. Prompted if omitted.

.PARAMETER ResourceGroupName
    Resource group of the Log Analytics workspace. Prompted if omitted.

.PARAMETER WorkspaceName
    Log Analytics workspace name. Prompted if omitted.

.PARAMETER OutputPath
    Directory for CSV / JSON / HTML output. Defaults to ./migration-report.

.PARAMETER NonInteractive
    Skip all prompts — fails if required parameters are missing.

.EXAMPLE
    ./Invoke-TableMigrationReview.ps1

    Interactive mode — prompts for subscription, resource group, and workspace.

.EXAMPLE
    ./Invoke-TableMigrationReview.ps1 `
        -SubscriptionId '00000000-0000-0000-0000-000000000000' `
        -ResourceGroupName 'rg-sentinel' `
        -WorkspaceName 'ws-sentinel' `
        -OutputPath './reports/2026-04'

    Scripted mode — outputs all reports to ./reports/2026-04.

.NOTES
    Version: 0.1.0

    Contributors:
        Toby G      — Developer, Co-Designer, Tester
                       https://github.com/noodlemctwoodle
        Sreedhar A  — Co-Designer, Tester
                       https://github.com/sreedharande

    Data source:
        Azure-Sentinel Solutions Analyzer
        https://github.com/Azure/Azure-Sentinel/tree/master/Tools/Solutions%20Analyzer

.LINK
    https://github.com/noodlemctwoodle/Sentinel-CLv1-Analyzer
#>
[CmdletBinding()]
param(
    [string]$SubscriptionId,
    [string]$ResourceGroupName,
    [string]$WorkspaceName,
    [string]$OutputPath = (Join-Path (Get-Location) 'migration-report'),
    [switch]$NonInteractive
)

$ErrorActionPreference = 'Stop'
$ProgressPreference     = 'Continue'

# -------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------

$script:ArmBaseUrl    = 'https://management.azure.com'
$script:ApiTables     = '2023-09-01'
$script:ApiSentinel   = '2024-03-01'
$script:ApiSavedLogs  = '2020-08-01'
$script:ApiInsights   = '2023-06-01'
$script:ApiDcr        = '2022-06-01'
$script:ApiLogic      = '2019-05-01'

# Solution mapping — bundled in data/ subfolder
$script:MappingPath = Join-Path $PSScriptRoot 'data' 'solution-mapping.json'
$script:MappingStaleDays = 7

# -------------------------------------------------------------------------
# UI helpers
# -------------------------------------------------------------------------

function Write-Step {
    param([string]$Message)
    Write-Host ''
    Write-Host "══ $Message " -ForegroundColor Cyan -NoNewline
    Write-Host ('═' * [Math]::Max(0, 70 - $Message.Length)) -ForegroundColor Cyan
}

function Write-Info  { param($m) Write-Host "  $m" -ForegroundColor Gray }
function Write-Ok    { param($m) Write-Host "  ✓ $m" -ForegroundColor Green }
function Write-Warn2 { param($m) Write-Host "  ⚠ $m" -ForegroundColor Yellow }
function Write-Err   { param($m) Write-Host "  ✗ $m" -ForegroundColor Red }

function Read-Required {
    param([string]$Prompt, [string]$Current)
    if ($Current) { return $Current }
    if ($NonInteractive) { throw "Parameter '$Prompt' is required in non-interactive mode." }
    do {
        $value = Read-Host -Prompt "  $Prompt"
    } while (-not $value)
    return $value.Trim()
}

# -------------------------------------------------------------------------
# Authentication
# -------------------------------------------------------------------------

function Initialize-AzContext {
    param([string]$SubscriptionId)

    Write-Info 'Checking Az.Accounts module...'
    Import-Module Az.Accounts -ErrorAction Stop

    $ctx = Get-AzContext -ErrorAction SilentlyContinue
    if (-not $ctx) {
        Write-Info 'No Azure context found — running Connect-AzAccount...'
        $null = Connect-AzAccount -ErrorAction Stop
        $ctx = Get-AzContext
    }

    if ($SubscriptionId -and $ctx.Subscription.Id -ne $SubscriptionId) {
        Write-Info "Switching to subscription $SubscriptionId"
        $null = Set-AzContext -SubscriptionId $SubscriptionId -ErrorAction Stop
        $ctx = Get-AzContext
    }

    Write-Ok "Authenticated as $($ctx.Account.Id) in subscription $($ctx.Subscription.Name)"
    return $ctx
}

function Get-ArmToken {
    $token = Get-AzAccessToken -ResourceUrl $script:ArmBaseUrl -ErrorAction Stop
    # Handle Az >=12 which returns SecureString
    if ($token.Token -is [System.Security.SecureString]) {
        return [System.Net.NetworkCredential]::new('', $token.Token).Password
    }
    return $token.Token
}

# -------------------------------------------------------------------------
# REST helpers
# -------------------------------------------------------------------------

function Invoke-ArmRequest {
    param(
        [Parameter(Mandatory)][string]$Path,
        [hashtable]$Query = @{}
    )
    $token = Get-ArmToken
    $headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }

    $qs = ($Query.GetEnumerator() | ForEach-Object { "$($_.Key)=$([uri]::EscapeDataString($_.Value))" }) -join '&'
    $url = "$script:ArmBaseUrl$Path" + ($(if ($qs) { "?$qs" } else { '' }))

    $results = @()
    do {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get
        if ($response.value) { $results += $response.value }
        elseif ($response -is [array]) { $results += $response }
        else { $results += $response }
        $url = $response.nextLink
    } while ($url)
    return $results
}

# -------------------------------------------------------------------------
# Step 1 — Discover tables
# -------------------------------------------------------------------------

function Get-ClassicCustomLogTable {
    param(
        [Parameter(Mandatory)][string]$SubscriptionId,
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName
    )
    $path = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName/tables"
    $tables = Invoke-ArmRequest -Path $path -Query @{ 'api-version' = $script:ApiTables }

    # AzureDiagnostics can appear as CustomLog/Classic but is a Microsoft-managed
    # table that should never be shown as a migration candidate.
    $EXCLUDED_TABLES = @('AzureDiagnostics')

    $classic = $tables | Where-Object {
        $_.properties.schema.tableType    -eq 'CustomLog' -and
        $_.properties.schema.tableSubType -eq 'Classic' -and
        $_.name -notin $EXCLUDED_TABLES
    }

    foreach ($t in $classic) {
        [PSCustomObject]@{
            Name            = $t.name
            TableType       = $t.properties.schema.tableType
            TableSubType    = $t.properties.schema.tableSubType
            Plan            = $t.properties.plan
            RetentionInDays = $t.properties.retentionInDays
            TotalRetention  = $t.properties.totalRetentionInDays
            ColumnCount     = $t.properties.schema.columns.Count
            ResourceId      = $t.id
        }
    }
}

# -------------------------------------------------------------------------
# Workspace content loaders
# -------------------------------------------------------------------------

function Get-WorkspaceContent {
    param(
        [Parameter(Mandatory)][string]$SubscriptionId,
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName
    )

    $sentinelBase = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName/providers/Microsoft.SecurityInsights"
    $opLogsBase   = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName"

    Write-Info 'Loading Analytics Rules...'
    $alertRules = Invoke-ArmRequest -Path "$sentinelBase/alertRules" -Query @{ 'api-version' = $script:ApiSentinel }

    Write-Info 'Loading Saved Searches (hunting + parsers)...'
    $savedSearches = Invoke-ArmRequest -Path "$opLogsBase/savedSearches" -Query @{ 'api-version' = $script:ApiSavedLogs }

    Write-Info 'Loading Workbooks...'
    $workbookPath = "/subscriptions/$SubscriptionId/providers/Microsoft.Insights/workbooks"
    try {
        $workbooks = Invoke-ArmRequest -Path $workbookPath -Query @{
            'api-version' = $script:ApiInsights
            'category'    = 'sentinel'
        }
    } catch {
        Write-Warn2 "Workbook load failed: $($_.Exception.Message)"
        $workbooks = @()
    }

    Write-Info 'Loading Data Collection Rules...'
    $dcrPath = "/subscriptions/$SubscriptionId/providers/Microsoft.Insights/dataCollectionRules"
    try {
        $dcrs = Invoke-ArmRequest -Path $dcrPath -Query @{ 'api-version' = $script:ApiDcr }
    } catch {
        Write-Warn2 "DCR load failed: $($_.Exception.Message)"
        $dcrs = @()
    }

    Write-Info 'Loading Logic Apps (playbooks)...'
    $logicPath = "/subscriptions/$SubscriptionId/providers/Microsoft.Logic/workflows"
    try {
        $logicApps = Invoke-ArmRequest -Path $logicPath -Query @{ 'api-version' = $script:ApiLogic }
    } catch {
        Write-Warn2 "Logic App load failed: $($_.Exception.Message)"
        $logicApps = @()
    }

    [PSCustomObject]@{
        AlertRules    = @($alertRules)
        SavedSearches = @($savedSearches)
        HuntingQueries = @($savedSearches | Where-Object { $_.properties.category -eq 'Hunting Queries' })
        Parsers        = @($savedSearches | Where-Object { $_.properties.functionAlias })
        Workbooks     = @($workbooks)
        Dcrs          = @($dcrs)
        Playbooks     = @($logicApps)
    }
}

# -------------------------------------------------------------------------
# KQL scanning
# -------------------------------------------------------------------------

function Test-KqlReferencesTable {
    param([string]$Query, [string]$TableName)
    if (-not $Query) { return $false }
    # Word-boundary match on the table name, case-insensitive
    return $Query -match "(?i)(?<![a-zA-Z0-9_])$([regex]::Escape($TableName))(?![a-zA-Z0-9_])"
}

function Get-MatchedTables {
    param([string]$Query, [string[]]$TableNames)
    if (-not $Query) { return @() }
    $matched = @()
    foreach ($t in $TableNames) {
        if (Test-KqlReferencesTable -Query $Query -TableName $t) { $matched += $t }
    }
    return $matched
}

function Get-WorkbookQueryText {
    param([string]$SerializedData)
    if (-not $SerializedData) { return @() }
    try {
        $parsed = $SerializedData | ConvertFrom-Json -Depth 20
    } catch { return @() }

    $queries = @()
    function Walk($node) {
        if ($null -eq $node) { return }
        if ($node -is [System.Collections.IEnumerable] -and -not ($node -is [string])) {
            foreach ($c in $node) { Walk $c }
            return
        }
        if ($node -is [PSCustomObject] -or $node -is [hashtable]) {
            $props = if ($node -is [hashtable]) { $node.Keys } else { $node.PSObject.Properties.Name }
            foreach ($p in $props) {
                $val = $node.$p
                if ($p -eq 'query' -and $val -is [string]) { $script:__queries += $val }
                Walk $val
            }
        }
    }
    $script:__queries = @()
    Walk $parsed
    return $script:__queries
}

# -------------------------------------------------------------------------
# Step 2 — Impact analysis
# -------------------------------------------------------------------------

function Get-TableImpactAnalysis {
    param(
        [Parameter(Mandatory)][string]$TableName,
        [Parameter(Mandatory)]$Content
    )

    $result = [ordered]@{
        TableName       = $TableName
        AnalyticsRules  = @()
        HuntingQueries  = @()
        Parsers         = @()
        SavedSearches   = @()
        Workbooks       = @()
        Playbooks       = @()
        Dcrs            = @()
    }

    foreach ($rule in $Content.AlertRules) {
        $query = $rule.properties.query
        if (Test-KqlReferencesTable -Query $query -TableName $TableName) {
            $result.AnalyticsRules += [PSCustomObject]@{
                Name       = ($rule.properties.displayName ?? $rule.name)
                Enabled    = $rule.properties.enabled
                Severity   = $rule.properties.severity
                ResourceId = $rule.id
            }
        }
    }

    foreach ($hq in $Content.HuntingQueries) {
        $query = $hq.properties.query
        if (Test-KqlReferencesTable -Query $query -TableName $TableName) {
            $result.HuntingQueries += [PSCustomObject]@{
                Name       = ($hq.properties.displayName ?? $hq.name)
                Category   = $hq.properties.category
                ResourceId = $hq.id
            }
        }
    }

    foreach ($parser in $Content.Parsers) {
        $query = $parser.properties.query
        if (Test-KqlReferencesTable -Query $query -TableName $TableName) {
            $result.Parsers += [PSCustomObject]@{
                Name          = ($parser.properties.functionAlias ?? $parser.properties.displayName ?? $parser.name)
                FunctionAlias = $parser.properties.functionAlias
                ResourceId    = $parser.id
            }
        }
    }

    foreach ($ss in $Content.SavedSearches) {
        # Exclude items already counted as hunting queries or parsers
        if ($ss.properties.category -eq 'Hunting Queries' -or $ss.properties.functionAlias) { continue }
        $query = $ss.properties.query
        if (Test-KqlReferencesTable -Query $query -TableName $TableName) {
            $result.SavedSearches += [PSCustomObject]@{
                Name       = ($ss.properties.displayName ?? $ss.name)
                Category   = $ss.properties.category
                ResourceId = $ss.id
            }
        }
    }

    foreach ($wb in $Content.Workbooks) {
        $queries = Get-WorkbookQueryText -SerializedData $wb.properties.serializedData
        $hits = $queries | Where-Object { Test-KqlReferencesTable -Query $_ -TableName $TableName }
        if ($hits) {
            $result.Workbooks += [PSCustomObject]@{
                Name       = ($wb.properties.displayName ?? $wb.name)
                QueryCount = @($hits).Count
                ResourceId = $wb.id
            }
        }
    }

    foreach ($pb in $Content.Playbooks) {
        $defJson = $pb.properties.definition | ConvertTo-Json -Depth 100 -Compress -WarningAction SilentlyContinue
        if ($defJson -and $defJson -match "(?i)(?<![a-zA-Z0-9_])$([regex]::Escape($TableName))(?![a-zA-Z0-9_])") {
            $result.Playbooks += [PSCustomObject]@{
                Name       = $pb.name
                State      = $pb.properties.state
                ResourceId = $pb.id
            }
        }
    }

    foreach ($dcr in $Content.Dcrs) {
        $flows = $dcr.properties.dataFlows
        if (-not $flows) { continue }
        $matchedFlowCount = 0
        foreach ($flow in $flows) {
            if (-not $flow.transformKql -or $flow.transformKql -eq 'source') { continue }
            if (Test-KqlReferencesTable -Query $flow.transformKql -TableName $TableName) { $matchedFlowCount++ }
        }
        if ($matchedFlowCount -gt 0) {
            $result.Dcrs += [PSCustomObject]@{
                Name       = $dcr.name
                FlowCount  = $matchedFlowCount
                ResourceId = $dcr.id
            }
        }
    }

    $totalImpacted = $result.AnalyticsRules.Count + $result.HuntingQueries.Count +
                     $result.Parsers.Count + $result.SavedSearches.Count +
                     $result.Workbooks.Count + $result.Playbooks.Count + $result.Dcrs.Count

    [PSCustomObject]([ordered]@{
        TableName      = $TableName
        TotalImpacted  = $totalImpacted
        AnalyticsRules = $result.AnalyticsRules
        HuntingQueries = $result.HuntingQueries
        Parsers        = $result.Parsers
        SavedSearches  = $result.SavedSearches
        Workbooks      = $result.Workbooks
        Playbooks      = $result.Playbooks
        Dcrs           = $result.Dcrs
    })
}

# -------------------------------------------------------------------------
# Step 3 — Content Hub & CCF classification
# -------------------------------------------------------------------------

function Get-ContentHubPackage {
    param(
        [Parameter(Mandatory)][string]$SubscriptionId,
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName
    )
    $path = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$WorkspaceName/providers/Microsoft.SecurityInsights/contentProductPackages"
    Invoke-ArmRequest -Path $path -Query @{ 'api-version' = $script:ApiSentinel }
}

function Update-SolutionMappingData {
    param([string]$OutputFile)

    $baseUrl = 'https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Tools/Solutions%20Analyzer'

    Write-Info 'Downloading simplified mapping CSV from Azure-Sentinel...'
    $simplifiedRaw = Invoke-RestMethod -Uri "$baseUrl/solutions_connectors_tables_mapping_simplified.csv" -ErrorAction Stop

    Write-Info 'Downloading full mapping CSV for solution metadata...'
    $fullRaw = Invoke-RestMethod -Uri "$baseUrl/solutions_connectors_tables_mapping.csv" -ErrorAction Stop

    $tablesToSolutions = [System.Collections.Specialized.OrderedDictionary]::new([StringComparer]::Ordinal)
    foreach ($line in (($simplifiedRaw.Trim() -split "`n") | Select-Object -Skip 1)) {
        if ($line -match '"([^"]*)","([^"]*)","([^"]*)"') {
            $solutionName = $Matches[1]
            $tableName    = $Matches[3]
            if (-not $tablesToSolutions.Contains($tableName)) {
                $tablesToSolutions[$tableName] = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
            }
            [void]$tablesToSolutions[$tableName].Add($solutionName)
        }
    }
    foreach ($key in @($tablesToSolutions.Keys)) {
        $sorted = [string[]]@($tablesToSolutions[$key])
        [Array]::Sort($sorted, [StringComparer]::Ordinal)
        $tablesToSolutions[$key] = $sorted
    }

    $solutionMetadata = [ordered]@{}
    foreach ($line in (($fullRaw.Trim() -split "`n") | Select-Object -Skip 1)) {
        $fields  = [System.Collections.Generic.List[string]]::new()
        $inQuote = $false
        $current = [System.Text.StringBuilder]::new()
        for ($i = 0; $i -lt $line.Length; $i++) {
            $ch = $line[$i]
            if ($ch -eq '"')                    { $inQuote = -not $inQuote; continue }
            if ($ch -eq ',' -and -not $inQuote) { $fields.Add($current.ToString()); [void]$current.Clear(); continue }
            [void]$current.Append($ch)
        }
        $fields.Add($current.ToString())
        $name = $fields[1]
        if (-not $name -or $solutionMetadata.Contains($name)) { continue }
        $meta = [ordered]@{}
        if ($fields[4]) { $meta['publisherId'] = $fields[4] }
        if ($fields[5]) { $meta['offerId']     = $fields[5] }
        if ($fields[3]) { $meta['githubUrl']   = $fields[3] }
        $solutionMetadata[$name] = $meta
    }

    $output = [ordered]@{
        generatedAt       = (Get-Date -Format 'yyyy-MM-dd')
        sourceUrl         = 'https://github.com/Azure/Azure-Sentinel/tree/master/Tools/Solutions%20Analyzer'
        tableCount        = $tablesToSolutions.Count
        solutionCount     = $solutionMetadata.Count
        tablesToSolutions = $tablesToSolutions
        solutionMetadata  = $solutionMetadata
    }

    $dir = Split-Path $OutputFile -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    ($output | ConvertTo-Json -Depth 10) + "`n" | Set-Content -Path $OutputFile -Encoding UTF8 -NoNewline
    Write-Ok "Solution mapping generated — $($output.tableCount) tables / $($output.solutionCount) solutions"
}

function Get-SolutionMapping {
    $needsRefresh = $false
    $exists       = Test-Path $script:MappingPath

    if (-not $exists) {
        Write-Info 'Solution mapping file not found — will generate from upstream CSVs'
        $needsRefresh = $true
    }
    else {
        $raw = Get-Content $script:MappingPath -Raw | ConvertFrom-Json -Depth 20 -AsHashtable
        if ($raw.generatedAt) {
            $age = (Get-Date) - [datetime]::ParseExact($raw.generatedAt, 'yyyy-MM-dd', $null)
            if ($age.TotalDays -gt $script:MappingStaleDays) {
                Write-Info "Solution mapping is $([int]$age.TotalDays) days old — refreshing from upstream CSVs"
                $needsRefresh = $true
            }
        }
    }

    if ($needsRefresh) {
        try {
            Update-SolutionMappingData -OutputFile $script:MappingPath
        }
        catch {
            Write-Warn2 "Failed to generate solution mapping: $($_.Exception.Message)"
            if (-not $exists) {
                Write-Warn2 'Continuing without solution mapping — Content Hub columns will be empty'
                return $null
            }
            Write-Info 'Falling back to existing (stale) mapping file'
        }
    }

    if (-not (Test-Path $script:MappingPath)) { return $null }
    $raw = Get-Content $script:MappingPath -Raw | ConvertFrom-Json -Depth 20 -AsHashtable

    $normalized = [System.Collections.Generic.Dictionary[string,object]]::new(
        [System.StringComparer]::OrdinalIgnoreCase)
    foreach ($entry in $raw.tablesToSolutions.GetEnumerator()) {
        $normalized[$entry.Key] = $entry.Value
    }
    $raw['_normalizedLookup'] = $normalized
    return $raw
}

function Resolve-ConnectorKind {
    param([string]$ConnectorId, [string]$SolutionName)

    # Heuristic classification based on connector ID naming conventions observed
    # in the Azure-Sentinel Solutions Analyzer data.
    $id = $ConnectorId
    if (-not $id) { return 'Unknown' }

    # CCF (Codeless Connector Framework) — new framework, identified by specific suffixes
    # or prefixes set by Microsoft. CCP was the older name for the same concept.
    if ($id -match '(CCP|CCF|Definition|_Ccp_|_Ccf_)$' -or
        $id -match '(?i)CCPDefinition') { return 'CCF' }

    # Azure Functions-based connectors — typically have "(Serverless)" suffix,
    # or deploy an Azure Function app (identified by AzureFunction* / Func / Polling suffixes).
    if ($id -match '(?i)(Serverless|AzureFunction|Polling|PollingAuth|Func$|_API_FunctionApp)') {
        return 'AzureFunctions'
    }

    # AMA (Azure Monitor Agent) — modern replacement for MMA, uses DCRs
    if ($id -match '(?i)Ama$') { return 'AMA' }

    # Platform-native connectors (Microsoft services) — usually short IDs matching
    # the service name without suffix (e.g. "AzureActiveDirectory", "Office365")
    if ($id -match '^(Azure|Office|Microsoft|Defender|ThreatIntelligence|WindowsEvent|SecurityEvents)') {
        return 'Platform'
    }

    # CEF / Syslog — agent-based
    if ($id -match '(?i)^(CEF|Syslog|CefAma)$') { return 'Agent' }

    return 'Legacy'
}

function Get-SolutionMatchForTable {
    param(
        [Parameter(Mandatory)][string]$TableName,
        [Parameter()]$StaticMapping,
        [Parameter()]$Packages
    )

    # Index packages by displayName (case-insensitive)
    $pkgByName = @{}
    foreach ($p in $Packages) {
        if ($p.properties -and $p.properties.contentKind -eq 'Solution') {
            $pkgByName[$p.properties.displayName.ToLower()] = $p
        }
    }

    $matchedSolutions = @()

    if ($StaticMapping -and $StaticMapping._normalizedLookup) {
        # Case-insensitive lookup with _CL fallback (matches TS lookupSolutionsForTable)
        $lookup = $StaticMapping._normalizedLookup
        $solutionNames = $lookup[$TableName]
        if (-not $solutionNames) {
            $withoutCL = $TableName -replace '_CL$',''
            $solutionNames = $lookup[$withoutCL]
        }
        if ($solutionNames) {
            foreach ($name in $solutionNames) {
                $pkg = $pkgByName[$name.ToLower()]
                $installed = if ($pkg) { [bool]$pkg.properties.installedVersion } else { $false }
                $meta = $StaticMapping.solutionMetadata[$name]
                $githubUrl = if ($meta) { $meta.githubUrl } else { $null }
                $matchedSolutions += [PSCustomObject]@{
                    SolutionName   = $name
                    IsInstalled    = $installed
                    IsInContentHub = [bool]$pkg
                    GithubUrl      = $githubUrl
                    DisplayName    = if ($pkg) { $pkg.properties.displayName } else { $name }
                }
            }
        }
    }

    [PSCustomObject]@{
        TableName        = $TableName
        MatchCount       = $matchedSolutions.Count
        Solutions        = @($matchedSolutions)
    }
}

function Get-ConnectorClassification {
    param(
        [Parameter(Mandatory)][string]$TableName,
        [Parameter()]$StaticMapping,
        [Parameter()]$Packages
    )

    $result = @()
    if (-not ($StaticMapping -and $StaticMapping._normalizedLookup)) { return $result }

    $lookup = $StaticMapping._normalizedLookup
    $solutionNames = $lookup[$TableName]
    if (-not $solutionNames) {
        $withoutCL = $TableName -replace '_CL$',''
        $solutionNames = $lookup[$withoutCL]
    }
    if (-not $solutionNames) { return $result }

    # Index Content Hub packages to check for DataConnector dependency kinds
    $pkgByName = @{}
    foreach ($p in $Packages) {
        if ($p.properties -and $p.properties.contentKind -eq 'Solution') {
            $pkgByName[$p.properties.displayName.ToLower()] = $p
        }
    }

    foreach ($name in $solutionNames) {
        $pkg = $pkgByName[$name.ToLower()]
        $kind = 'Unknown'
        if ($pkg -and $pkg.properties.dependencies.criteria) {
            # Check if any DataConnector dependency exists in the package
            $connectorIds = @()
            foreach ($c in $pkg.properties.dependencies.criteria) {
                if ($c.kind -eq 'DataConnector' -and $c.contentId) {
                    $connectorIds += $c.contentId
                }
            }
            if ($connectorIds.Count -gt 0) {
                # Use Resolve-ConnectorKind on the first connector ID
                $kind = Resolve-ConnectorKind -ConnectorId $connectorIds[0] -SolutionName $name
            }
        }

        $result += [PSCustomObject]@{
            SolutionName  = $name
            ConnectorKind = $kind
        }
    }
    return $result
}

# -------------------------------------------------------------------------
# Output generators
# -------------------------------------------------------------------------

function Export-ReportCsv {
    param($Tables, $Impacts, $SolutionMatches, [string]$OutDir)

    $Tables | Export-Csv -Path (Join-Path $OutDir 'tables.csv') -NoTypeInformation -Encoding UTF8

    $impactFlat = foreach ($i in $Impacts) {
        foreach ($type in 'AnalyticsRules','HuntingQueries','Parsers','SavedSearches','Workbooks','Playbooks','Dcrs') {
            foreach ($item in $i.$type) {
                [PSCustomObject]@{
                    TableName   = $i.TableName
                    ContentType = $type
                    Name        = $item.Name
                    ResourceId  = $item.ResourceId
                }
            }
        }
    }
    $impactFlat | Export-Csv -Path (Join-Path $OutDir 'impact.csv') -NoTypeInformation -Encoding UTF8

    $matchFlat = foreach ($m in $SolutionMatches) {
        foreach ($s in $m.Solutions) {
            [PSCustomObject]@{
                TableName      = $m.TableName
                SolutionName   = $s.SolutionName
                IsInstalled    = $s.IsInstalled
                IsInContentHub = $s.IsInContentHub
                GithubUrl      = $s.GithubUrl
            }
        }
    }
    $matchFlat | Export-Csv -Path (Join-Path $OutDir 'solution-matches.csv') -NoTypeInformation -Encoding UTF8
}

function Export-ReportJson {
    param($Tables, $Impacts, $SolutionMatches, $Context, [string]$OutDir)
    $combined = [ordered]@{
        generatedAt       = (Get-Date).ToString('o')
        subscription      = $Context.SubscriptionId
        resourceGroup     = $Context.ResourceGroupName
        workspace         = $Context.WorkspaceName
        classicTables     = $Tables
        impactAnalysis    = $Impacts
        solutionMatches   = $SolutionMatches
    }
    $combined | ConvertTo-Json -Depth 20 | Out-File -FilePath (Join-Path $OutDir 'report.json') -Encoding utf8
}

function Export-ReportHtml {
    param($Tables, $Impacts, $SolutionMatches, $Context, [string]$OutDir)

    $templatePath = Join-Path $PSScriptRoot 'Templates' 'report.html.template'
    if (-not (Test-Path $templatePath)) {
        Write-Warn2 "HTML template missing at $templatePath — skipping HTML report"
        return
    }
    $template = Get-Content $templatePath -Raw

    $data = [ordered]@{
        GeneratedAt     = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
        Subscription    = $Context.SubscriptionId
        ResourceGroup   = $Context.ResourceGroupName
        Workspace       = $Context.WorkspaceName
        TotalTables     = $Tables.Count
        TotalImpacted   = ($Impacts | Measure-Object -Property TotalImpacted -Sum).Sum
        Tables          = $Tables
        Impacts         = $Impacts
        SolutionMatches = $SolutionMatches
    }

    $dataJson = ($data | ConvertTo-Json -Depth 20 -Compress)
    $html = $template.Replace('{{DATA_JSON}}', [System.Web.HttpUtility]::JavaScriptStringEncode($dataJson))

    # Fallback for systems without System.Web
    if ($html -eq $template) {
        Add-Type -AssemblyName System.Web -ErrorAction SilentlyContinue
        $escaped = $dataJson -replace '\\','\\\\' -replace "'","\'" -replace '"','\"' `
                             -replace "`n",'\n' -replace "`r",'\r' -replace "`t",'\t'
        $html = $template.Replace('{{DATA_JSON}}', $escaped)
    }

    $outFile = Join-Path $OutDir 'report.html'
    $html | Out-File -FilePath $outFile -Encoding utf8
    Write-Ok "HTML report: $outFile"
}

# -------------------------------------------------------------------------
# Main flow
# -------------------------------------------------------------------------

try {
    Write-Host ''
    Write-Host '┌────────────────────────────────────────────────────────────────────────┐' -ForegroundColor Cyan
    Write-Host '│                  Microsoft Sentinel Classic (CLv1) Impact Assessment │' -ForegroundColor Cyan
    Write-Host '└────────────────────────────────────────────────────────────────────────┘' -ForegroundColor Cyan

    # Auth + inputs
    Write-Step 'Authentication'
    $SubscriptionId    = Read-Required -Prompt 'Subscription ID' -Current $SubscriptionId
    $null = Initialize-AzContext -SubscriptionId $SubscriptionId
    $ResourceGroupName = Read-Required -Prompt 'Resource group' -Current $ResourceGroupName
    $WorkspaceName     = Read-Required -Prompt 'Workspace name' -Current $WorkspaceName

    if (-not (Test-Path $OutputPath)) {
        New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null
    }
    Write-Ok "Output directory: $OutputPath"

    $contextInfo = [PSCustomObject]@{
        SubscriptionId    = $SubscriptionId
        ResourceGroupName = $ResourceGroupName
        WorkspaceName     = $WorkspaceName
    }

    # Step 1 — Discover
    Write-Step 'Step 1: Discover classic custom log tables (CLv1)'
    $classicTables = @(Get-ClassicCustomLogTable `
        -SubscriptionId $SubscriptionId `
        -ResourceGroupName $ResourceGroupName `
        -WorkspaceName $WorkspaceName)

    Write-Ok "Found $($classicTables.Count) classic custom log tables"
    if ($classicTables.Count -eq 0) {
        Write-Info 'Nothing to migrate — workspace has no classic V1 tables.'
        return
    }
    $classicTables | Select-Object Name, Plan, RetentionInDays, ColumnCount | Format-Table | Out-String | Write-Host

    # Step 2 — Impact
    Write-Step 'Step 2: Assess dependency impact'
    $content = Get-WorkspaceContent `
        -SubscriptionId $SubscriptionId `
        -ResourceGroupName $ResourceGroupName `
        -WorkspaceName $WorkspaceName

    Write-Info "Scanning $($classicTables.Count) tables against:"
    Write-Info "  Analytics Rules : $($content.AlertRules.Count)"
    Write-Info "  Hunting Queries : $($content.HuntingQueries.Count)"
    Write-Info "  Parsers         : $($content.Parsers.Count)"
    Write-Info "  Saved Searches  : $($content.SavedSearches.Count)"
    Write-Info "  Workbooks       : $($content.Workbooks.Count)"
    Write-Info "  Playbooks       : $($content.Playbooks.Count)"
    Write-Info "  DCRs            : $($content.Dcrs.Count)"

    $impacts = @()
    $i = 0
    foreach ($t in $classicTables) {
        $i++
        Write-Progress -Activity 'Impact analysis' -Status $t.Name -PercentComplete (($i / $classicTables.Count) * 100)
        $impacts += Get-TableImpactAnalysis -TableName $t.Name -Content $content
    }
    Write-Progress -Activity 'Impact analysis' -Completed

    $totalImpacted = ($impacts | Measure-Object -Property TotalImpacted -Sum).Sum
    Write-Ok "Scan complete — $totalImpacted dependent items across $($classicTables.Count) tables"

    # Step 3 — Content Hub + CCF
    Write-Step 'Step 3: Map to Content Hub solutions (with CCF classification)'
    Write-Info 'Loading Content Hub package catalog...'
    try {
        $packages = Get-ContentHubPackage `
            -SubscriptionId $SubscriptionId `
            -ResourceGroupName $ResourceGroupName `
            -WorkspaceName $WorkspaceName
        Write-Ok "Loaded $($packages.Count) Content Hub packages"
    } catch {
        Write-Warn2 "Content Hub query failed: $($_.Exception.Message)"
        $packages = @()
    }

    Write-Info 'Loading static solution mapping (Azure-Sentinel Solutions Analyzer)...'
    $mapping = Get-SolutionMapping
    if ($mapping) { Write-Ok "Mapping loaded — $($mapping.tableCount) tables / $($mapping.solutionCount) solutions" }

    $solutionMatches = foreach ($t in $classicTables) {
        $match = Get-SolutionMatchForTable -TableName $t.Name -StaticMapping $mapping -Packages $packages
        $match | Add-Member -NotePropertyName ConnectorClassification `
                            -NotePropertyValue @(Get-ConnectorClassification -TableName $t.Name -StaticMapping $mapping -Packages $packages) -PassThru
    }

    $unmatched = @($solutionMatches | Where-Object { $_.MatchCount -eq 0 })
    Write-Ok "Matched $($solutionMatches.Count - $unmatched.Count) of $($solutionMatches.Count) tables"
    if ($unmatched.Count -gt 0) {
        Write-Warn2 "$($unmatched.Count) tables have no Content Hub match — consider raising a feature request with your CSAM/SSP:"
        foreach ($u in $unmatched) { Write-Host "    • $($u.TableName)" -ForegroundColor Yellow }
    }

    # Export
    Write-Step 'Export reports'
    Export-ReportCsv  -Tables $classicTables -Impacts $impacts -SolutionMatches $solutionMatches -OutDir $OutputPath
    Write-Ok "CSV files written to $OutputPath"

    Export-ReportJson -Tables $classicTables -Impacts $impacts -SolutionMatches $solutionMatches -Context $contextInfo -OutDir $OutputPath
    Write-Ok "JSON report: $(Join-Path $OutputPath 'report.json')"

    Export-ReportHtml -Tables $classicTables -Impacts $impacts -SolutionMatches $solutionMatches -Context $contextInfo -OutDir $OutputPath

    Write-Host ''
    Write-Host '┌────────────────────────────────────────────────────────────────────────┐' -ForegroundColor Green
    Write-Host '│                            Review complete                             │' -ForegroundColor Green
    Write-Host '└────────────────────────────────────────────────────────────────────────┘' -ForegroundColor Green
    Write-Host ''

    # Return to pipeline
    [PSCustomObject]@{
        Context         = $contextInfo
        ClassicTables   = $classicTables
        Impacts         = $impacts
        SolutionMatches = $solutionMatches
        OutputPath      = $OutputPath
    }
}
catch {
    Write-Err $_.Exception.Message
    Write-Host $_.ScriptStackTrace -ForegroundColor DarkGray
    exit 1
}
