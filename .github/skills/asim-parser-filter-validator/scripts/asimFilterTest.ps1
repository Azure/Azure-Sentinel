<#
.SYNOPSIS
    ASIM Parser Filtering Test — pure PowerShell / az CLI edition.

.DESCRIPTION
    Validates that an ASIM parser's filtering parameters work correctly
    by running queries against a Log Analytics workspace.
    Uses az CLI for authentication — no Python or Azure SDK packages required.

    Requirements:
      - PowerShell 7+
      - Azure CLI               (az login must have been run beforehand)

.PARAMETER ParserFile
    Path to the ASIM parser .kql file to test.

.PARAMETER SchemaName
    The ASIM schema name (e.g. Dns, Authentication, NetworkSession).

.PARAMETER WorkspaceId
    Log Analytics workspace GUID to run queries against.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ParserFile,

    [Parameter(Mandatory)]
    [string]$SchemaName,

    [Parameter(Mandatory)]
    [string]$WorkspaceId
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

$script:DUMMY_VALUE        = "'!not_REAL_vAlUe'"
$script:MAX_FILTERING_PARAMS = 2
$script:TIME_SPAN_DAYS     = 2
$script:INT_DUMMY_VALUE    = -967799
$script:LA_API_BASE        = "https://api.loganalytics.io/v1/workspaces"

$script:WsId = $WorkspaceId

$script:EndTime   = [DateTimeOffset]::UtcNow
$script:StartTime = $script:EndTime.AddDays(-$script:TIME_SPAN_DAYS)
$script:TimeSpanIso = "$($script:StartTime.ToString('o'))/$($script:EndTime.ToString('o'))"

# ANSI colours (PowerShell 7 supports them)
$script:GREEN  = "`e[92m"
$script:YELLOW = "`e[93m"
$script:RED    = "`e[91m"
$script:RESET  = "`e[0m"

# Known single-failure exceptions per schema
$script:FailureMessages = @{
    'AuditEvent'     = "This single failure is because only one value exist in 'EventResult' field in 'AuditEvent' schema. Audit Event is a special case where 'EventResult' validations could be partial as only 'Success' events exists. Ignoring this error."
    'Authentication' = "This single failure is because only two values exist in 'EventType' field in 'Authentication' schema. 'Authentication' is a special case where 'EventType' validations could be partial as only 'Logon' or 'Logoff' events may exists. Ignoring this error."
    'Dns'            = "This single failure is because only one value exist in 'EventType' field in 'Dns' schema. 'Dns' is a special case where 'EventType' validations could be 'Query' only. Ignoring this error."
}

# ─────────────────────────────────────────────────────────────────────────────
# Schema → parameter-to-column mapping
# ─────────────────────────────────────────────────────────────────────────────

$script:AllSchemasParameters = @{
    "AgentEvent" = @{
        "starttime"             = "EventStartTime"
        "endtime"               = "EventEndTime"
        "agentid_has_any"       = "SrcAgentId"
        "agentname_has_any"     = "SrcAgentName"
        "username_has_any"      = "ActorUsername"
    }
    "AlertEvent" = @{
        "ipaddr_has_any_prefix"     = "DvcIpAddr"
        "disabled"                  = ""
        "endtime"                   = "EventEndTime"
        "hostname_has_any"          = "DvcHostname"
        "username_has_any"          = "Username"
        "attacktactics_has_any"     = "AttackTactics"
        "attacktechniques_has_any"  = "AttackTechniques"
        "threatcategory_has_any"    = "ThreatCategory"
        "alertverdict_has_any"      = "AlertVerdict"
        "starttime"                 = "EventStartTime"
        "eventseverity_has_any"     = "EventSeverity"
    }
    "AssetEntity" = @{
        "starttime"              = "EntityIngestionTime"
        "endtime"                = "EntityIngestionTime"
        "entityid_has_any"       = "EntityId"
        "entityname_has_any"     = "EntityName"
        "assettype_in"           = "AssetType"
        "path_has_any"           = "FilePath"
        "assetowner_has_any"     = "AssetOwnerId"
        "entitysource_has_any"   = "EntitySource"
    }
    "AuditEvent" = @{
        "actorusername_has_any"     = "ActorUsername"
        "disabled"                  = ""
        "endtime"                   = "EventEndTime"
        "eventresult"               = "EventResult"
        "eventtype_in"              = "EventType"
        "newvalue_has_any"          = "NewValue"
        "object_has_any"            = "Object"
        "operation_has_any"         = "Operation"
        "srcipaddr_has_any_prefix"  = "SrcIpAddr"
        "starttime"                 = "EventStartTime"
    }
    "Authentication" = @{
        "disabled"                  = ""
        "eventresult"               = "EventResult"
        "eventresultdetails_in"     = "EventResultDetails"
        "eventtype_in"              = "EventType"
        "endtime"                   = "EventEndTime"
        "srchostname_has_any"       = "SrcHostname"
        "srcipaddr_has_any_prefix"  = "SrcIpAddr"
        "starttime"                 = "EventStartTime"
        "targetappname_has_any"     = "TargetAppName"
        "username_has_any"          = "User"
    }
    "DhcpEvent" = @{
        "disabled"                  = ""
        "eventresult"               = "EventResult"
        "endtime"                   = "EventEndTime"
        "starttime"                 = "EventStartTime"
        "srcipaddr_has_any_prefix"  = "SrcIpAddr"
        "srchostname_has_any"       = "SrcHostname"
        "srcusername_has_any"       = "SrcUsername"
    }
    "Dns" = @{
        "disabled"                  = ""
        "domain_has_any"            = "Domain"
        "eventtype"                 = "EventType"
        "endtime"                   = "EventEndTime"
        "response_has_any_prefix"   = "DnsResponseName"
        "response_has_ipv4"         = "DnsResponseName"
        "responsecodename"          = "DnsResponseCodeName"
        "srcipaddr"                 = "SrcIpAddr"
        "starttime"                 = "EventStartTime"
    }
    "FileEvent" = @{
        "actorusername_has_any"     = "ActorUsername"
        "disabled"                  = ""
        "eventtype_in"              = "EventType"
        "endtime"                   = "EventEndTime"
        "srcfilepath_has_any"       = "SrcFilePath"
        "srcipaddr_has_any_prefix"  = "SrcIpAddr"
        "starttime"                 = "EventStartTime"
        "targetfilepath_has_any"    = "TargetFilePath"
        "hashes_has_any"            = "Hash"
        "dvchostname_has_any"       = "DvcHostname"
    }
    "NetworkSession" = @{
        "disabled"                  = ""
        "dstipaddr_has_any_prefix"  = "DstIpAddr"
        "dstportnumber"             = "DstPortNumber"
        "dvcaction"                 = "DvcAction"
        "endtime"                   = "EventEndTime"
        "eventresult"               = "EventResult"
        "hostname_has_any"          = "Hostname"
        "ipaddr_has_any_prefix"     = "IpAddr"
        "srcipaddr_has_any_prefix"  = "SrcIpAddr"
        "starttime"                 = "EventStartTime"
    }
    "ProcessEvent" = @{
        "actingprocess_has_any"         = "ActingProcessName"
        "actorusername_has"             = "ActorUsername"
        "commandline_has_all"           = "CommandLine"
        "commandline_has_any"           = "CommandLine"
        "commandline_has_any_ip_prefix" = "CommandLine"
        "disabled"                      = ""
        "dvchostname_has_any"           = "DvcHostname"
        "dvcipaddr_has_any_prefix"      = "DvcIpAddr"
        "endtime"                       = "EventEndTime"
        "eventtype"                     = "EventType"
        "hashes_has_any"                = "Hash"
        "parentprocess_has_any"         = "ParentProcessName"
        "starttime"                     = "EventStartTime"
        "targetprocess_has_any"         = "TargetProcessName"
        "targetusername_has"            = "TargetUsername"
    }
    "RegistryEvent" = @{
        "actorusername_has_any"  = "ActorUsername"
        "disabled"               = ""
        "dvchostname_has_any"    = "DvcHostname"
        "endtime"                = "EventEndTime"
        "eventtype_in"           = "EventType"
        "registrykey_has_any"    = "RegistryKey"
        "registryvalue_has_any"  = "RegistryValue"
        "registrydata_has_any"   = "RegistryValueData"
        "starttime"              = "EventStartTime"
    }
    "UserManagement" = @{
        "actorusername_has_any"     = "ActorUsername"
        "disabled"                  = ""
        "endtime"                   = "EventEndTime"
        "eventtype_in"              = "EventType"
        "srcipaddr_has_any_prefix"  = "SrcIpAddr"
        "starttime"                 = "EventStartTime"
        "targetusername_has_any"    = "TargetUsername"
    }
    "WebSession" = @{
        "disabled"                      = ""
        "endtime"                       = "EventEndTime"
        "eventresult"                   = "EventResult"
        "eventresultdetails_in"         = "EventResultDetails"
        "httpuseragent_has_any"         = "HttpUserAgent"
        "ipaddr_has_any_prefix"         = "IpAddr"
        "srcipaddr_has_any_prefix"      = "SrcIpAddr"
        "starttime"                     = "EventStartTime"
        "url_has_any"                   = "Url"
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Test-result tracking
# ─────────────────────────────────────────────────────────────────────────────

class TestContext {
    [string]$ParserPath
    [System.Collections.Generic.List[string]]$Failures
    [int]$PassCount
    [int]$SubTestCount

    TestContext([string]$path) {
        $this.ParserPath = $path
        $this.Failures   = [System.Collections.Generic.List[string]]::new()
        $this.PassCount   = 0
        $this.SubTestCount = 0
    }

    [void] Pass() {
        $this.PassCount++
        $this.SubTestCount++
    }

    [void] Fail([string]$message) {
        $this.Failures.Add($message)
        $this.SubTestCount++
        Write-Host "${script:RED}  FAIL: $message${script:RESET}"
    }

    [bool] WasSuccessful() {
        return $this.Failures.Count -eq 0
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Azure CLI / Log Analytics helpers
# ─────────────────────────────────────────────────────────────────────────────

function Get-LaAccessToken {
    $tokenResult = az account get-access-token --resource https://api.loganalytics.io --query accessToken -o tsv 2>&1
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($tokenResult)) {
        throw "Failed to get access token via az CLI. Run 'az login' first. $tokenResult"
    }
    return $tokenResult.Trim()
}

# Cache the token for the run
$script:AccessToken = $null

function Ensure-Token {
    if (-not $script:AccessToken) {
        $script:AccessToken = Get-LaAccessToken
    }
    return $script:AccessToken
}

function Invoke-LaQuery {
    <#
    .SYNOPSIS
        Send a KQL query to Log Analytics and return parsed tables.
    .OUTPUTS
        Hashtable with key 'tables', each table has 'columns' (string[]) and 'rows' (array of arrays).
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory)][AllowEmptyString()][string]$Query)

    $token = Ensure-Token
    $url   = "$($script:LA_API_BASE)/$($script:WsId)/query"
    $body  = @{ query = $Query; timespan = $script:TimeSpanIso } | ConvertTo-Json -Depth 5 -Compress

    # Write payload to temp file to avoid shell-escaping issues with large KQL
    $tmpFile = [System.IO.Path]::GetTempFileName()
    try {
        [System.IO.File]::WriteAllText($tmpFile, $body, [System.Text.Encoding]::UTF8)
        $resp = Invoke-WebRequest -Method Post -Uri $url `
            -Headers @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" } `
            -Body ([System.IO.File]::ReadAllBytes($tmpFile)) `
            -SkipHttpErrorCheck
    } finally {
        Remove-Item $tmpFile -Force -ErrorAction SilentlyContinue
    }

    if ($resp.StatusCode -ne 200) {
        $errBody = ($resp.Content | ConvertFrom-Json -ErrorAction SilentlyContinue)
        $errMsg  = if ($errBody.error) { $errBody.error.message } else { $resp.Content }
        throw "Query failed (HTTP $($resp.StatusCode)): $errMsg`nQuery: $Query"
    }

    $parsed = $resp.Content | ConvertFrom-Json
    $result = @{ tables = @() }
    foreach ($t in $parsed.tables) {
        $colNames = @($t.columns | ForEach-Object { $_.name })
        $rows = @()
        foreach ($r in $t.rows) {
            $rows += , @($r)  # keep as array-of-arrays
        }
        $result.tables += @{ columns = $colNames; rows = $rows }
    }
    return $result
}

function Send-QueryForTest {
    <#
    .SYNOPSIS
        Wrapper for Invoke-LaQuery used inside tests.
        On failure, records the failure in the test context and returns $null.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Query,
        [Parameter(Mandatory)][TestContext]$Ctx
    )
    try {
        return Invoke-LaQuery -Query $Query
    } catch {
        $Ctx.Fail("Query failed: $_")
        return $null
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Row helper — get value by column index or name
# ─────────────────────────────────────────────────────────────────────────────

function Get-RowValue {
    param(
        [array]$Row,
        [string[]]$Columns,
        $Key   # int index or string column name
    )
    if ($Key -is [int]) {
        return $Row[$Key]
    }
    $idx = [Array]::IndexOf($Columns, $Key)
    if ($idx -lt 0) { return $null }
    return $Row[$idx]
}

# ─────────────────────────────────────────────────────────────────────────────
# KQL file parser
# ─────────────────────────────────────────────────────────────────────────────

function Get-ParamType {
    <#
    .SYNOPSIS
        Infers the KQL type of an ASIM filtering parameter from its name.
    #>
    param([string]$Name)
    if ($Name -eq 'disabled')                          { return 'bool' }
    if ($Name -in @('starttime','endtime'))             { return 'datetime' }
    if ($Name -like '*_has_any' -or
        $Name -like '*_has_all' -or
        $Name -like '*_has_any_prefix' -or
        $Name -like '*_in')                            { return 'dynamic' }
    if ($Name -eq 'dstportnumber')                     { return 'int' }
    return 'string'
}

# ─────────────────────────────────────────────────────────────────────────────
# KQL query-building helpers
# ─────────────────────────────────────────────────────────────────────────────

function New-QueryDefinition {
    <#
    .SYNOPSIS
        Takes the raw KQL from a parser file and renames the function to 'query'
        so the test harness can call query() / query(param=value).
        Removes the trailing self-invocation line (e.g. "parser(...)") since
        the test harness appends its own query() calls.
    #>
    param([string]$RawKql)
    # Capture the original function name
    $nameMatch = [regex]::Match($RawKql, '(?s)^\s*let\s+(\w+)\s*=')
    $funcName = if ($nameMatch.Success) { $nameMatch.Groups[1].Value } else { 'parser' }
    # Replace `let <name>=` with `let query=`
    $def = $RawKql -replace '(?s)^(\s*let\s+)\w+(\s*=)', '${1}query${2}'
    # Remove trailing self-invocation: lines like "parser(...)" or "funcName(...)" after the closing };
    $def = $def -replace "(?m)^\s*$funcName\s*\(.*\)\s*$", ''
    # Ensure it ends with a semicolon + newline for chaining
    $def = $def.TrimEnd()
    if (-not $def.EndsWith(';')) { $def += ';' }
    return "$def`n"
}

function New-ExecWithoutParams {
    param([string]$ColumnName)
    return "query() | summarize count() by $ColumnName`n"
}

function New-ExecWithOneParam {
    param([string]$ParamName, [string]$Value, [string]$ColumnName)
    return "query($ParamName=$Value) | summarize count() by $ColumnName`n"
}

function New-ValuesString {
    param([string[]]$Values)
    return ($Values | ForEach-Object { "@'$_'" }) -join ','
}

# ─────────────────────────────────────────────────────────────────────────────
# String-analysis helpers (prefix / postfix / delimiter logic)
# ─────────────────────────────────────────────────────────────────────────────

function Get-SubstringOrDefault {
    param([string]$Default, [string]$Substring, [array]$Rows, [string[]]$Columns, [System.Collections.Generic.List[string]]$CurrentList)
    if ($CurrentList.Contains($Substring)) { return $Default }
    if ($Rows.Count -eq 1) { return $Substring }
    foreach ($row in $Rows) {
        $val = $row[0]
        if ($val -notlike "*$Substring*") { return $Substring }
    }
    return $Default
}

function Get-PrefixValue {
    param([string]$Str, [array]$Rows, [string[]]$Columns, [System.Collections.Generic.List[string]]$CurrentList, [string]$Delimiter)
    $idx = $Str.LastIndexOf($Delimiter)
    if ($idx -lt 0) { return $Str }
    $sub = $Str.Substring(0, $idx)
    return Get-SubstringOrDefault -Default $Str -Substring $sub -Rows $Rows -Columns $Columns -CurrentList $CurrentList
}

function Get-PostfixValue {
    param([string]$Str, [array]$Rows, [string[]]$Columns, [System.Collections.Generic.List[string]]$CurrentList, [string]$Delimiter)
    $idx = $Str.IndexOf($Delimiter)
    if ($idx -lt 0) { return $Str }
    $sub = $Str.Substring($idx + 1)
    return Get-SubstringOrDefault -Default $Str -Substring $sub -Rows $Rows -Columns $Columns -CurrentList $CurrentList
}

function Get-FrequentNonWordChar {
    param([array]$Rows)
    $charCount = @{}
    $limit = [Math]::Min(5, $Rows.Count)
    for ($i = 0; $i -lt $limit; $i++) {
        $val = [string]$Rows[$i][0]
        $matches = [regex]::Matches($val, '\W')
        foreach ($m in $matches) {
            $c = $m.Value
            $charCount[$c] = ($charCount[$c] -as [int]) + 1
        }
    }
    if ($charCount.Count -eq 0) { return ' ' }
    return ($charCount.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1).Key
}

function Get-SplittedParts {
    param([string[]]$Values)
    foreach ($val in $Values) {
        for ($i = 0; $i -lt $val.Length; $i++) {
            if (-not [char]::IsLetterOrDigit($val[$i])) {
                return @($val.Substring(0, $i + 1), $val.Substring($i + 1))
            }
        }
    }
    return @($null, $null)
}

# ─────────────────────────────────────────────────────────────────────────────
# Test implementations
# ─────────────────────────────────────────────────────────────────────────────

function Test-DataInWorkspace {
    param([string]$QueryDef, [TestContext]$Ctx)
    $resp = Send-QueryForTest -Query "$QueryDef query() | take 5" -Ctx $Ctx
    if ($null -eq $resp) { return $false }
    if ($resp.tables[0].rows.Count -eq 0) {
        $Ctx.Fail("No data in the provided workspace")
        return $false
    }
    $Ctx.Pass()
    return $true
}

function Get-ParserColumns {
    param([string]$QueryDef, [TestContext]$Ctx)
    $resp = Send-QueryForTest -Query "$QueryDef query() | getschema`n" -Ctx $Ctx
    if ($null -eq $resp) { return @() }
    $cols = $resp.tables[0].columns
    $nameIdx = [Array]::IndexOf($cols, 'ColumnName')
    if ($nameIdx -lt 0) { $nameIdx = 0 }
    $set = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($row in $resp.tables[0].rows) {
        [void]$set.Add([string]$row[$nameIdx])
    }
    return $set
}

# ── disabled ──

function Test-Disabled {
    param([string]$QueryDef, [TestContext]$Ctx)

    $trueResp = Send-QueryForTest -Query "$QueryDef query(disabled=true) | summarize count()`n" -Ctx $Ctx
    if ($null -eq $trueResp) { return }
    $trueCount = $trueResp.tables[0].rows[0][0]
    if ($trueCount -ne 0) {
        $Ctx.Fail("Expected 0 results for disabled=true, got $trueCount")
    } else { $Ctx.Pass() }

    $falseResp = Send-QueryForTest -Query "$QueryDef query(disabled=false) | summarize count()`n" -Ctx $Ctx
    if ($null -eq $falseResp) { return }
    $falseCount = $falseResp.tables[0].rows[0][0]
    if ($falseCount -eq 0) {
        $Ctx.Fail("Expected results for disabled=false, got 0")
    } else { $Ctx.Pass() }
}

# ── datetime ──

function Test-Datetime {
    param([hashtable]$Param, [string]$QueryDef, [string]$ColumnName, [TestContext]$Ctx)
    $pName = $Param.Name

    $noFilterResp = Send-QueryForTest -Query "$QueryDef query() | project TimeGenerated`n" -Ctx $Ctx
    if ($null -eq $noFilterResp) { return }
    $noFilterCount = $noFilterResp.tables[0].rows.Count
    if ($noFilterCount -eq 0) { $Ctx.Fail("No data for parameter: $pName"); return }

    $midQ = "$QueryDef query() | summarize max_TimeGenerated = max(TimeGenerated), min_TimeGenerated = min(TimeGenerated) `n | extend timeSpan = datetime_diff('second', max_TimeGenerated, min_TimeGenerated) `n | project mid_point = datetime_add('second', timeSpan / 2, min_TimeGenerated)"
    $midResp = Send-QueryForTest -Query $midQ -Ctx $Ctx
    if ($null -eq $midResp) { return }
    $midVal = $midResp.tables[0].rows[0][0]
    $dtVal  = "datetime($midVal)"

    $filteredResp = Send-QueryForTest -Query "$QueryDef query($pName=$dtVal)`n" -Ctx $Ctx
    if ($null -eq $filteredResp) { return }
    $filteredCount = $filteredResp.tables[0].rows.Count
    if ($filteredCount -eq 0) { $Ctx.Fail("No data for parameter: $pName after filtering"); return }
    if ($filteredCount -ge $noFilterCount) {
        $Ctx.Fail("Parameter: $pName - Expected less results after filtering. Filtered by value: $dtVal")
    } else { $Ctx.Pass() }
}

# ── scalar ──

function Test-Scalar {
    param([hashtable]$Param, [string]$QueryDef, [string]$ColumnName, [TestContext]$Ctx)
    $pName = $Param.Name
    $pType = $Param.Type

    $noFilterQ    = "$QueryDef$(New-ExecWithoutParams -ColumnName $ColumnName)"
    $noFilterResp = Send-QueryForTest -Query $noFilterQ -Ctx $Ctx
    if ($null -eq $noFilterResp) { return }
    $rowCount = $noFilterResp.tables[0].rows.Count
    if ($rowCount -eq 0) { $Ctx.Fail("No data for parameter: $pName"); return }

    if ($rowCount -eq 1) {
        $Ctx.Fail("Only one value exists for parameter: $pName - validations for this parameter are partial")
    } else { $Ctx.Pass() }

    $selectedVal = [string]$noFilterResp.tables[0].rows[0][0]
    $filterVal   = if ($pType -eq 'string') { "'$selectedVal'" } else { $selectedVal }

    if ($selectedVal -eq '') {
        $filterQ = "$QueryDef query() | where isempty($ColumnName) | summarize count() by $ColumnName`n"
    } else {
        $filterQ = "$QueryDef$(New-ExecWithOneParam -ParamName $pName -Value $filterVal -ColumnName $ColumnName)"
    }

    # check filtering returns results
    $filteredResp = Send-QueryForTest -Query $filterQ -Ctx $Ctx
    if ($null -eq $filteredResp) { return }
    if ($filteredResp.tables[0].rows.Count -eq 0) {
        $Ctx.Fail("Parameter: $pName - Got no results after filtering. Filtered by value: $filterVal")
    } else { $Ctx.Pass() }

    if ($filteredResp.tables[0].rows.Count -ne 1) {
        $Ctx.Fail("Parameter: $pName - Expected results for only one value after filtering. Filtered by value: $filterVal")
    } else { $Ctx.Pass() }

    # fictive value → expect 0 rows
    $ficVal = if ($pType -eq 'int') { $script:INT_DUMMY_VALUE } else { $script:DUMMY_VALUE }
    $ficQ   = "$QueryDef$(New-ExecWithOneParam -ParamName $pName -Value $ficVal -ColumnName $ColumnName)"
    $ficResp = Send-QueryForTest -Query $ficQ -Ctx $Ctx
    if ($null -eq $ficResp) { return }
    if ($ficResp.tables[0].rows.Count -ne 0) {
        $Ctx.Fail("Parameter: $pName - Returned results for non-existing filter value: $ficVal")
    } else { $Ctx.Pass() }
}

# ── dynamic helpers ──

function Get-ValuesForDynamicTests {
    param([array]$Rows)
    if ($Rows.Count -eq 1) {
        $v = [string]$Rows[0][0]
        if ($v -eq '') { return @() } else { return @($v) }
    }
    $values = [System.Collections.Generic.List[string]]::new()
    foreach ($row in $Rows) {
        if ($values.Count -ge $script:MAX_FILTERING_PARAMS) { break }
        $val = [string]$row[0]
        if ($val -eq '') { continue }
        foreach ($cmpRow in $Rows) {
            $cmpVal = [string]$cmpRow[0]
            if ($cmpVal -notlike "*$val*" -or $cmpVal -ne $val) {
                # value is not a substring of ALL other values
                if ($val -notin $values) { $values.Add($val) }
                break
            }
        }
    }
    return $values.ToArray()
}

function Invoke-DynamicAssertions {
    param([string]$ParamName, [int]$FilteredCount, [string]$FilterParams, [int]$NoFilterCount, [TestContext]$Ctx)
    if ($FilteredCount -eq 0) {
        $Ctx.Fail("Parameter: $ParamName - Got no results after filtering. Filtered by value: $FilterParams")
    } else { $Ctx.Pass() }

    if ($NoFilterCount -eq 1) {
        if ($FilteredCount -ne 1) {
            $Ctx.Fail("Parameter: $ParamName - Expected one result after filtering. Filtered by value: $FilterParams")
        } else { $Ctx.Pass() }
    } else {
        if ($FilteredCount -ge $NoFilterCount) {
            $Ctx.Fail("Parameter: $ParamName - Expected less results after filtering. Filtered by value: $FilterParams")
        } else { $Ctx.Pass() }
    }
}

function Invoke-QueryWithDynamicParams {
    param([string]$ParamName, [string]$QueryDef, [string]$ColumnName, [string[]]$ValuesList, [TestContext]$Ctx)
    $filterStr = New-ValuesString -Values $ValuesList
    $q = "$QueryDef$(New-ExecWithOneParam -ParamName $ParamName -Value "dynamic([$filterStr])" -ColumnName $ColumnName)"
    $resp = Send-QueryForTest -Query $q -Ctx $Ctx
    return @{ Response = $resp; FilterString = $filterStr }
}

function Test-DynamicFictiveValue {
    param([string]$ParamName, [string]$QueryDef, [string]$ColumnName, [TestContext]$Ctx)
    $q    = "$QueryDef$(New-ExecWithOneParam -ParamName $ParamName -Value "dynamic([$($script:DUMMY_VALUE)])" -ColumnName $ColumnName)"
    $resp = Send-QueryForTest -Query $q -Ctx $Ctx
    if ($null -eq $resp) { return }
    if ($resp.tables[0].rows.Count -ne 0) {
        $Ctx.Fail("Parameter: $ParamName - Returned results for non-existing dynamic filter value: $($script:DUMMY_VALUE)")
    } else { $Ctx.Pass() }
}

function Test-DynamicHelper {
    param(
        [string]$ParamName, [string]$QueryDef, [int]$NoFilterCount,
        [string]$ColumnName, [string[]]$ValuesList, [string]$TestType, [TestContext]$Ctx
    )
    if ($ValuesList.Count -eq 0) {
        $Ctx.Fail("Parameter: $ParamName - Unable to find values to perform $TestType tests")
        return
    }

    # filter with one value
    $oneResult = Invoke-QueryWithDynamicParams -ParamName $ParamName -QueryDef $QueryDef -ColumnName $ColumnName -ValuesList @($ValuesList[0]) -Ctx $Ctx
    if ($null -eq $oneResult.Response) { return }
    $oneCount = $oneResult.Response.tables[0].rows.Count
    Invoke-DynamicAssertions -ParamName $ParamName -FilteredCount $oneCount -FilterParams $oneResult.FilterString -NoFilterCount $NoFilterCount -Ctx $Ctx

    # filter with two values if possible
    if ($ValuesList.Count -eq 1 -or $NoFilterCount -le $script:MAX_FILTERING_PARAMS) {
        $isAuthException = ($ValuesList.Count -ge 2) -and ($ParamName -eq 'eventtype_in') -and (@('Logon','Logoff') | Where-Object { $_ -in $ValuesList }).Count -eq 2
        if (-not $isAuthException) {
            $Ctx.Fail("Parameter: $ParamName - Not enough data to perform two values $TestType tests")
        }
    }
    $twoResult = Invoke-QueryWithDynamicParams -ParamName $ParamName -QueryDef $QueryDef -ColumnName $ColumnName -ValuesList $ValuesList -Ctx $Ctx
    if ($null -eq $twoResult.Response) { return }
    $twoCount = $twoResult.Response.tables[0].rows.Count
    Invoke-DynamicAssertions -ParamName $ParamName -FilteredCount $twoCount -FilterParams $twoResult.FilterString -NoFilterCount $NoFilterCount -Ctx $Ctx

    Test-DynamicFictiveValue -ParamName $ParamName -QueryDef $QueryDef -ColumnName $ColumnName -Ctx $Ctx
}

function Test-DynamicCommon {
    param([string]$ParamName, [string]$QueryDef, [array]$NoFilterRows, [string]$ColumnName, [TestContext]$Ctx)
    $vals = Get-ValuesForDynamicTests -Rows $NoFilterRows
    Test-DynamicHelper -ParamName $ParamName -QueryDef $QueryDef -NoFilterCount $NoFilterRows.Count -ColumnName $ColumnName -ValuesList $vals -TestType "default" -Ctx $Ctx
}

function Get-SubstringsList {
    param([array]$Rows, [int]$Num, [string]$Delimiter)
    $list = [System.Collections.Generic.List[string]]::new()
    foreach ($row in $Rows) {
        if ($list.Count -ge $Num) { break }
        $val  = [string]$row[0]
        $post = Get-PostfixValue -Str $val -Rows $Rows -Columns @() -CurrentList $list -Delimiter $Delimiter
        if ($post -and $post -notin $list) { $list.Add($post) }
        if ($list.Count -ge $Num) { break }
        if ($post -eq $val) {
            $pre = Get-PrefixValue -Str $val -Rows $Rows -Columns @() -CurrentList $list -Delimiter $Delimiter
            if ($pre -and $pre -notin $list) { $list.Add($pre) }
        }
    }
    return $list.ToArray()
}

function Get-PrefixList {
    param([array]$Rows, [int]$Num, [string]$Delimiter)
    $list = [System.Collections.Generic.List[string]]::new()
    foreach ($row in $Rows) {
        if ($list.Count -ge $Num) { break }
        $val = [string]$row[0]
        $pre = Get-PrefixValue -Str $val -Rows $Rows -Columns @() -CurrentList $list -Delimiter $Delimiter
        if ($pre -ne $val) { $list.Add("$pre.") }
    }
    return $list.ToArray()
}

function Test-HasAny {
    param([string]$ParamName, [string]$QueryDef, [array]$NoFilterRows, [string]$ColumnName, [TestContext]$Ctx)
    Test-DynamicCommon -ParamName $ParamName -QueryDef $QueryDef -NoFilterRows $NoFilterRows -ColumnName $ColumnName -Ctx $Ctx
    $delim = Get-FrequentNonWordChar -Rows $NoFilterRows
    $subs  = Get-SubstringsList -Rows $NoFilterRows -Num $script:MAX_FILTERING_PARAMS -Delimiter $delim
    Test-DynamicHelper -ParamName $ParamName -QueryDef $QueryDef -NoFilterCount $NoFilterRows.Count -ColumnName $ColumnName -ValuesList $subs -TestType "has_any" -Ctx $Ctx
}

function Test-HasAll {
    param([string]$ParamName, [string]$QueryDef, [array]$NoFilterRows, [string]$ColumnName, [TestContext]$Ctx)
    $vals = Get-ValuesForDynamicTests -Rows $NoFilterRows
    if ($vals.Count -eq 0) { $Ctx.Fail("Parameter: $ParamName - Unable to find values to perform has_all tests"); return }

    # one value
    $oneResult = Invoke-QueryWithDynamicParams -ParamName $ParamName -QueryDef $QueryDef -ColumnName $ColumnName -ValuesList @($vals[0]) -Ctx $Ctx
    if ($null -eq $oneResult.Response) { return }
    $oneCount = $oneResult.Response.tables[0].rows.Count
    Invoke-DynamicAssertions -ParamName $ParamName -FilteredCount $oneCount -FilterParams $oneResult.FilterString -NoFilterCount $NoFilterRows.Count -Ctx $Ctx

    # two parts
    $parts = Get-SplittedParts -Values $vals
    if ($null -eq $parts[0]) {
        $Ctx.Fail("Parameter: $ParamName - has_all tests performed for only one filtering value")
        return
    }
    $twoResult = Invoke-QueryWithDynamicParams -ParamName $ParamName -QueryDef $QueryDef -ColumnName $ColumnName -ValuesList $parts -Ctx $Ctx
    if ($null -eq $twoResult.Response) { return }
    $twoCount = $twoResult.Response.tables[0].rows.Count
    Invoke-DynamicAssertions -ParamName $ParamName -FilteredCount $twoCount -FilterParams $twoResult.FilterString -NoFilterCount $NoFilterRows.Count -Ctx $Ctx

    Test-DynamicFictiveValue -ParamName $ParamName -QueryDef $QueryDef -ColumnName $ColumnName -Ctx $Ctx
}

function Test-HasAnyPrefix {
    param([string]$ParamName, [string]$QueryDef, [array]$NoFilterRows, [string]$ColumnName, [TestContext]$Ctx)
    Test-DynamicCommon -ParamName $ParamName -QueryDef $QueryDef -NoFilterRows $NoFilterRows -ColumnName $ColumnName -Ctx $Ctx
    $prefixes = Get-PrefixList -Rows $NoFilterRows -Num $script:MAX_FILTERING_PARAMS -Delimiter '.'
    Test-DynamicHelper -ParamName $ParamName -QueryDef $QueryDef -NoFilterCount $NoFilterRows.Count -ColumnName $ColumnName -ValuesList $prefixes -TestType "has_any_prefix" -Ctx $Ctx
}

function Test-Dynamic {
    param([hashtable]$Param, [string]$QueryDef, [string]$ColumnName, [TestContext]$Ctx)
    $pName = $Param.Name

    $noFilterQ    = "$QueryDef$(New-ExecWithoutParams -ColumnName $ColumnName)"
    $noFilterResp = Send-QueryForTest -Query $noFilterQ -Ctx $Ctx
    if ($null -eq $noFilterResp) { return }
    $rows = $noFilterResp.tables[0].rows
    if ($rows.Count -eq 0) { $Ctx.Fail("No data for parameter: $pName"); return }
    if ($rows.Count -eq 1) {
        $Ctx.Fail("Only one value exists for parameter: $pName - validations for this parameter are partial")
    } else { $Ctx.Pass() }

    if ($pName -like '*has_any' -and $pName -notlike '*has_any_prefix') {
        Test-HasAny -ParamName $pName -QueryDef $QueryDef -NoFilterRows $rows -ColumnName $ColumnName -Ctx $Ctx
    } elseif ($pName -like '*has_any_prefix') {
        Test-HasAnyPrefix -ParamName $pName -QueryDef $QueryDef -NoFilterRows $rows -ColumnName $ColumnName -Ctx $Ctx
    } elseif ($pName -like '*has_all') {
        Test-HasAll -ParamName $pName -QueryDef $QueryDef -NoFilterRows $rows -ColumnName $ColumnName -Ctx $Ctx
    } else {
        Test-DynamicCommon -ParamName $pName -QueryDef $QueryDef -NoFilterRows $rows -ColumnName $ColumnName -Ctx $Ctx
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Parameter dispatcher
# ─────────────────────────────────────────────────────────────────────────────

function Send-ParamToTest {
    param([hashtable]$Param, [string]$QueryDef, [System.Collections.Generic.HashSet[string]]$Columns, [string]$ColumnName, [TestContext]$Ctx)
    $pName = $Param.Name
    $pType = $Param.Type

    if ($pName -eq 'pack')     { return }
    if ($pName -eq 'disabled') { Test-Disabled -QueryDef $QueryDef -Ctx $Ctx; return }
    if ($ColumnName -notin $Columns) { return }
    if ($pType -eq 'datetime') { Test-Datetime -Param $Param -QueryDef $QueryDef -ColumnName $ColumnName -Ctx $Ctx; return }
    if ($pType -eq 'dynamic')  { Test-Dynamic  -Param $Param -QueryDef $QueryDef -ColumnName $ColumnName -Ctx $Ctx; return }
    Test-Scalar -Param $Param -QueryDef $QueryDef -ColumnName $ColumnName -Ctx $Ctx
}

# ─────────────────────────────────────────────────────────────────────────────
# Run all tests for one parser
# ─────────────────────────────────────────────────────────────────────────────

function Test-Parser {
    param([string]$ParserPath, [string]$Schema)

    $ctx = [TestContext]::new($ParserPath)
    Write-Host "`n${script:GREEN}--- Running filter tests for parser: '$ParserPath'${script:RESET}"

    # Load & validate
    if (-not (Test-Path $ParserPath)) { $ctx.Fail("File not found: $ParserPath"); return $ctx }
    if ($ParserPath -notlike '*.kql')  { $ctx.Fail("Not a KQL file: $ParserPath"); return $ctx }

    $rawKql = Get-Content -Path $ParserPath -Raw
    if ([string]::IsNullOrWhiteSpace($rawKql)) { $ctx.Fail("Parser file is empty: $ParserPath"); return $ctx }

    $queryDef = New-QueryDefinition -RawKql $rawKql
    if (-not (Test-DataInWorkspace -QueryDef $queryDef -Ctx $ctx)) { return $ctx }

    $columns = Get-ParserColumns -QueryDef $queryDef -Ctx $ctx

    if (-not $script:AllSchemasParameters.ContainsKey($Schema)) {
        $ctx.Fail("Schema: $Schema - Not supported by the validations script")
        return $ctx
    }
    $paramMap = $script:AllSchemasParameters[$Schema]

    foreach ($pName in $paramMap.Keys) {
        $colName = $paramMap[$pName]
        $pType   = Get-ParamType -Name $pName
        $param   = @{ Name = $pName; Type = $pType }
        Send-ParamToTest -Param $param -QueryDef $queryDef -Columns $columns -ColumnName $colName -Ctx $ctx
    }

    return $ctx
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

function Main {
    # ── Prerequisites ──
    Write-Host "${script:YELLOW}Checking prerequisites...${script:RESET}"

    # Verify az CLI login
    try {
        $null = az account show 2>&1
        if ($LASTEXITCODE -ne 0) { throw "not logged in" }
    } catch {
        Write-Error "Azure CLI is not logged in. Please run 'az login' first."
        exit 1
    }

    # Verify connectivity
    Write-Host "${script:YELLOW}Verifying workspace connectivity...${script:RESET}"
    try {
        $null = Invoke-LaQuery -Query "print 1"
    } catch {
        Write-Error "::error::Cannot connect to workspace $($script:WsId): $_"
        exit 1
    }
    Write-Host "${script:GREEN}Connected to workspace $($script:WsId)${script:RESET}"

    # ── Resolve parser file ──
    $resolvedPath = if ([System.IO.Path]::IsPathRooted($ParserFile)) { $ParserFile } else { Join-Path (Get-Location) $ParserFile }
    if (-not (Test-Path $resolvedPath)) {
        Write-Error "Parser file not found: $resolvedPath"
        exit 1
    }
    Write-Host "${script:YELLOW}Running filter tests for parser:${script:RESET}"
    Write-Host "${script:GREEN}- $resolvedPath${script:RESET}"
    Write-Host "${script:YELLOW}Schema: $SchemaName${script:RESET}"

    # ── Run tests ──
    $ctx = Test-Parser -ParserPath $resolvedPath -Schema $SchemaName

    if (-not $ctx.WasSuccessful()) {
        # Check known single-failure exceptions
        if ($ctx.Failures.Count -eq 1) {
            $failMsg = $ctx.Failures[0]
            $ignore = $false
            switch ($SchemaName) {
                'AuditEvent'     { if ($failMsg -like '*eventresult*partial*')           { Write-Host "${script:YELLOW} $($script:FailureMessages['AuditEvent'])${script:RESET}"; $ignore = $true } }
                'Authentication' { if ($failMsg -like '*eventtype_in*less results*')     { Write-Host "${script:YELLOW} $($script:FailureMessages['Authentication'])${script:RESET}"; $ignore = $true } }
                'Dns'            { if ($failMsg -like '*eventtype*partial*')              { Write-Host "${script:YELLOW} $($script:FailureMessages['Dns'])${script:RESET}"; $ignore = $true } }
            }
            if ($ignore) { return }
        }

        Write-Host "${script:RED}::error::Tests failed for $resolvedPath ($($ctx.Failures.Count) failure(s))${script:RESET}"
        exit 1
    } else {
        Write-Host "${script:GREEN}All $($ctx.PassCount) tests passed for $resolvedPath${script:RESET}"
    }
}

# ── Entry point ──
Main
