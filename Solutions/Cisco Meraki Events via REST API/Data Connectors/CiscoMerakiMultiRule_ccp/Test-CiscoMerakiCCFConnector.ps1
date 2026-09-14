<#
.SYNOPSIS
    Diagnostic / connectivity-test script that replays the exact same Cisco Meraki REST API
    calls the CCF (Codeless Connector Framework) RestApiPoller connections make, using the
    request shapes, time-window parameters, paging, and rate limits defined in
    CiscoMeraki_PollerConfig.json.

.DESCRIPTION
    This script is a *local troubleshooting aid* for the "Cisco Meraki Events via REST API"
    CCF solution. It mirrors, per data type, the same endpoint / method / query-window /
    time-parameter behavior configured in the poller so that connector-side data issues
    (empty results, 404s, throttling, auth failures) can be reproduced and isolated without
    needing to redeploy or wait on a live poller cycle.

    Data types covered (matches CiscoMeraki_PollerConfig.json):
      - CiscoMerakiOrganizations          GET  /organizations                                  (queryWindowInMin=1440, no time params)
      - CiscoMerakiOrganizationNetworks    GET  /organizations/{orgId}/networks                 (queryWindowInMin=1440, no time params)
      - CiscoMerakiNetworkClients          GET  /organizations/{orgId}/networks -> per network:
                                            GET  /networks/{networkId}/clients                  (queryWindowInMin=60,  t0 only)
      - CiscoMerakiAirMarshalEvents        GET  /organizations/{orgId}/networks (wireless only) -> per network:
                                            GET  /networks/{networkId}/wireless/airMarshal       (queryWindowInMin=15,  t0 only)
      - ASimWebSessionLogs (API Requests)  GET  /organizations/{orgId}/apiRequests               (queryWindowInMin=5,   t0+t1)
      - ASimAuditEventLogs (Config Chgs)   GET  /organizations/{orgId}/configurationChanges      (queryWindowInMin=129600, t0+t1; 90 days)
      - ASimNetworkSessionLogs (Security)  GET  /organizations/{orgId}/appliance/security/events (queryWindowInMin=5,   t0+t1)

    This script never writes the API key to disk, a log file, or the console. It supports
    three ways to supply the API key, in order of preference (most to least secure):

      1. -ApiKeySecure <SecureString>        (recommended; e.g. Read-Host -AsSecureString, or
                                               pulled from Azure Key Vault as a SecureString)
      2. $env:MERAKI_API_KEY environment variable (process/session scoped, never persisted)
      3. -ApiKeyPlainText <string>            (see FEASIBILITY / SECURITY WARNING below)

.PARAMETER FEASIBILITY / SECURITY WARNING — pasting the secret directly in this script
    It IS technically feasible to hardcode the API key as a literal string inside this file
    (e.g. replace a parameter default with the raw key) and it will work exactly the same,
    because the script only ever needs a plain string in memory to build the
    "X-Cisco-Meraki-API-Key" request header. There is no technical restriction that requires
    a SecureString or Key Vault.

    However, this is STRONGLY DISCOURAGED and must never be done in any file that is
    committed to source control (this repo, or any git repo), because:
      - Any commit, even later deleted, permanently remains in git history and is
        recoverable by anyone with repo access (or a repo leak).
      - Secret-scanning tools (e.g. TruffleHog, GitHub secret scanning) used by this repo's
        CI (see .github/instructions/packaging.instructions.md, Step 4) will flag/fail the
        build if a live key is committed.
      - Plaintext secrets in a script are trivially exposed via `Get-Content`, shell history,
        crash dumps, shared screenshots, or accidental `git add .`.
      - This violates this session's and this repo's security policy (no credentials in
        source code).

    If you still want to run this script with the key pasted inline for a one-off, purely
    LOCAL, NEVER-COMMITTED test, the supported (but discouraged) mechanism is the
    -ApiKeyPlainText parameter below — pass it on the command line or paste it only into
    your own local, gitignored copy of this file. Do not paste it into the tracked copy in
    this solution folder, and do not commit it.

.PARAMETER ApiBaseUrl
    Cisco Meraki API base URL, e.g. https://api.meraki.com/api/v1

.PARAMETER OrganizationId
    Cisco Meraki Organization ID to test against.

.PARAMETER ApiKeySecure
    (Recommended) The Meraki API key as a SecureString.

.PARAMETER ApiKeyPlainText
    (Discouraged — see SECURITY WARNING above) The Meraki API key as a plain string.
    Falls back to $env:MERAKI_API_KEY if neither this nor -ApiKeySecure is supplied.

.PARAMETER DataTypes
    One or more data types to test. Defaults to all.

.EXAMPLE
    # Recommended: prompt securely, never visible on screen or in history
    $secureKey = Read-Host -Prompt "Meraki API Key" -AsSecureString
    .\Test-CiscoMerakiCCFConnector.ps1 -OrganizationId "1752626" -ApiKeySecure $secureKey

.EXAMPLE
    # Recommended: source from Key Vault at runtime, never persisted to disk
    $secure = (Get-AzKeyVaultSecret -VaultName "ccf-ca-3p-accounts-kv" -Name "0--Cisco-Meraki-Temporary-Creds").SecretValue
    .\Test-CiscoMerakiCCFConnector.ps1 -OrganizationId "1752626" -ApiKeySecure $secure

.EXAMPLE
    # Environment variable (process-scoped, not persisted, not visible in this script)
    $env:MERAKI_API_KEY = "<paste-only-in-your-own-shell-never-in-this-file>"
    .\Test-CiscoMerakiCCFConnector.ps1 -OrganizationId "1752626"

.EXAMPLE
    # Discouraged: fill in the $OrganizationId and $ApiKeyPlainText defaults directly at the
    # top of this file (param block) for a throwaway LOCAL test, then run with no arguments:
    #   [string]$OrganizationId = "1752626"
    #   [string]$ApiKeyPlainText = "abcd1234yourrealkey"
    # .\Test-CiscoMerakiCCFConnector.ps1
    # NEVER commit a version of this file with a real OrganizationId/key filled in above.

.EXAMPLE
    # Discouraged: same as above but passed on the command line instead of edited into the file.
    .\Test-CiscoMerakiCCFConnector.ps1 -OrganizationId "1752626" -ApiKeyPlainText "PASTE-KEY-HERE-LOCAL-ONLY"
#>

[CmdletBinding(DefaultParameterSetName = 'SecureKey')]
param(
    # Defaulted so it can be run with no arguments; override on the command line if needed,
    # e.g. -ApiBaseUrl "https://api.meraki.com/api/v1" (or a regional endpoint such as
    # https://api.meraki.cn/api/v1 / https://api.gov-meraki.com/api/v1).
    [string]$ApiBaseUrl = "https://api.meraki.com/api/v1",

    # Defaulted for convenience — replace with your own Organization ID, or override with
    # -OrganizationId "<yourOrgId>" on the command line.
    [string]$OrganizationId = "<YOUR_ORGANIZATION_ID>",

    [Parameter(ParameterSetName = 'SecureKey')]
    [System.Security.SecureString]$ApiKeySecure,

    # DISCOURAGED — see SECURITY WARNING in the help block above.
    # This default lets you paste the key directly in this file for a quick LOCAL test
    # (e.g. $ApiKeyPlainText = "abcd1234...") instead of passing it on the command line.
    # NEVER commit this file with a real key filled in here — see warning above.
    [Parameter(ParameterSetName = 'PlainTextKey')]
    [string]$ApiKeyPlainText = "<PASTE-YOUR-API-KEY-HERE-LOCAL-ONLY-NEVER-COMMIT>",

    [ValidateSet(
        'CiscoMerakiOrganizations',
        'CiscoMerakiOrganizationNetworks',
        'CiscoMerakiNetworkClients',
        'CiscoMerakiAirMarshalEvents',
        'ASimWebSessionLogs',
        'ASimAuditEventLogs',
        'ASimNetworkSessionLogs'
    )]
    [string[]]$DataTypes = @(
        'CiscoMerakiOrganizations',
        'CiscoMerakiOrganizationNetworks',
        'CiscoMerakiNetworkClients',
        'CiscoMerakiAirMarshalEvents',
        'ASimWebSessionLogs',
        'ASimAuditEventLogs',
        'ASimNetworkSessionLogs'
    ),

    [int]$RateLimitDelayMs = 110  # ~10 req/s ceiling per Meraki org rate limit, same as connector's rateLimitQPS=10
)

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Resolve the API key from the most secure source available. Never echoed,
# never written to a variable that gets logged, and cleared from memory
# (best-effort; .NET strings are not guaranteed erasable) before exit.
# ---------------------------------------------------------------------------
function Resolve-MerakiApiKey {
    param(
        [System.Security.SecureString]$Secure,
        [string]$PlainText
    )

    if ($Secure) {
        $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Secure)
        try {
            return [System.Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
        }
        finally {
            [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
        }
    }

    if ($PlainText -and $PlainText -ne '<PASTE-YOUR-API-KEY-HERE-LOCAL-ONLY-NEVER-COMMIT>') {
        Write-Warning "Using -ApiKeyPlainText: the key is present in memory as a plain string for this session. Do not commit any file containing a real key."
        return $PlainText
    }

    if ($env:MERAKI_API_KEY) {
        return $env:MERAKI_API_KEY
    }

    throw "No API key supplied. Either fill in the `$ApiKeyPlainText default in this file (local-only, never commit), pass -ApiKeySecure (recommended), pass -ApiKeyPlainText on the command line, or set `$env:MERAKI_API_KEY."
}

if ($OrganizationId -eq '<YOUR_ORGANIZATION_ID>') {
    throw "OrganizationId is still the placeholder value. Either fill in the `$OrganizationId default in this file or pass -OrganizationId on the command line."
}

$apiKey = Resolve-MerakiApiKey -Secure $ApiKeySecure -PlainText $ApiKeyPlainText
$headers = @{
    'X-Cisco-Meraki-API-Key' = $apiKey
    'Content-Type'           = 'application/json'
    'Accept'                 = 'application/json'
}

function Invoke-MerakiGet {
    param(
        [string]$Uri
    )
    Start-Sleep -Milliseconds $RateLimitDelayMs
    try {
        $response = Invoke-WebRequest -Uri $Uri -Headers $headers -Method Get -UseBasicParsing
        return [pscustomobject]@{
            Uri        = $Uri
            StatusCode = [int]$response.StatusCode
            Success    = $true
            Count      = $(try { (ConvertFrom-Json $response.Content).Count } catch { $null })
            Error      = $null
        }
    }
    catch {
        $statusCode = $null
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        return [pscustomobject]@{
            Uri        = $Uri
            StatusCode = $statusCode
            Success    = $false
            Count      = $null
            Error      = $_.Exception.Message
        }
    }
}

function Get-UnixTimeAgo {
    param([int]$Minutes)
    [int][double]::Parse((Get-Date -Date (Get-Date).ToUniversalTime().AddMinutes(-$Minutes) -UFormat %s))
}

function ConvertTo-AsimAuditEventPreview {
    param(
        [Parameter(ValueFromPipeline = $true)]
        [object]$Event
    )

    process {
        [pscustomobject]@{
            TimeGenerated      = $Event.ts
            ActorUsername      = $Event.adminEmail
            ActorUserId        = $Event.adminId
            ObjectId           = $Event.networkId
            OldValue           = $Event.oldValue
            NewValue           = $Event.newValue
            Object             = $Event.networkName
            Operation          = "$($Event.page)/$($Event.label)"
            EventType          = if ([string]::IsNullOrEmpty($Event.oldValue)) { 'Create' } elseif ([string]::IsNullOrEmpty($Event.newValue)) { 'Delete' } else { 'Set' }
            EventResult        = 'Success'
            EventProduct       = 'Meraki'
            EventVendor        = 'Cisco'
            EventSeverity      = 'Informational'
            ActorUsernameType  = 'UPN'
            ActorUserType      = 'Admin'
            ActorUserIdType    = 'Other'
            ObjectType         = 'Other'
            EventSchemaVersion = '0.1'
            EventCount         = 1
        }
    }
}

$results = New-Object System.Collections.Generic.List[object]

# --- CiscoMerakiOrganizations : queryWindowInMin=1440, no time params ---
if ($DataTypes -contains 'CiscoMerakiOrganizations') {
    Write-Host "`n[CiscoMerakiOrganizations] GET /organizations" -ForegroundColor Cyan
    $r = Invoke-MerakiGet -Uri "$ApiBaseUrl/organizations?perPage=1000"
    $results.Add(($r | Select-Object @{n='DataType';e={'CiscoMerakiOrganizations'}}, *))
}

# --- CiscoMerakiOrganizationNetworks : queryWindowInMin=1440, no time params ---
$networks = $null
if ($DataTypes -contains 'CiscoMerakiOrganizationNetworks' -or
    $DataTypes -contains 'CiscoMerakiNetworkClients' -or
    $DataTypes -contains 'CiscoMerakiAirMarshalEvents') {
    Write-Host "`n[CiscoMerakiOrganizationNetworks] GET /organizations/$OrganizationId/networks" -ForegroundColor Cyan
    $netUri = "$ApiBaseUrl/organizations/$OrganizationId/networks?perPage=1000"
    $r = Invoke-MerakiGet -Uri $netUri
    $results.Add(($r | Select-Object @{n='DataType';e={'CiscoMerakiOrganizationNetworks'}}, *))
    if ($r.Success) {
        try {
            $rawNetworks = Invoke-WebRequest -Uri $netUri -Headers $headers -Method Get -UseBasicParsing
            $networks = ConvertFrom-Json $rawNetworks.Content
        } catch { $networks = @() }
    }
}

# --- CiscoMerakiNetworkClients : queryWindowInMin=60, t0 only, nested per-network step ---
if ($DataTypes -contains 'CiscoMerakiNetworkClients') {
    $t0 = Get-UnixTimeAgo -Minutes 60
    if ($networks) {
        foreach ($net in $networks) {
            $uri = "$ApiBaseUrl/networks/$($net.id)/clients?perPage=5000&t0=$t0"
            Write-Host "[CiscoMerakiNetworkClients] GET /networks/$($net.id)/clients (t0=$t0)" -ForegroundColor Cyan
            $r = Invoke-MerakiGet -Uri $uri
            $results.Add(($r | Select-Object @{n='DataType';e={'CiscoMerakiNetworkClients'}}, @{n='NetworkId';e={$net.id}}, *))
        }
    } else {
        Write-Warning "Skipping CiscoMerakiNetworkClients: network list unavailable."
    }
}

# --- CiscoMerakiAirMarshalEvents : queryWindowInMin=15, t0 only, wireless networks only ---
if ($DataTypes -contains 'CiscoMerakiAirMarshalEvents') {
    $t0 = Get-UnixTimeAgo -Minutes 15
    if ($networks) {
        $wirelessNets = $networks | Where-Object { $_.productTypes -contains 'wireless' }
        foreach ($net in $wirelessNets) {
            $uri = "$ApiBaseUrl/networks/$($net.id)/wireless/airMarshal?t0=$t0"
            Write-Host "[CiscoMerakiAirMarshalEvents] GET /networks/$($net.id)/wireless/airMarshal (t0=$t0)" -ForegroundColor Cyan
            $r = Invoke-MerakiGet -Uri $uri
            $results.Add(($r | Select-Object @{n='DataType';e={'CiscoMerakiAirMarshalEvents'}}, @{n='NetworkId';e={$net.id}}, *))
        }
    } else {
        Write-Warning "Skipping CiscoMerakiAirMarshalEvents: network list unavailable."
    }
}

# --- ASimWebSessionLogs (API Requests) : queryWindowInMin=5, t0+t1 ---
if ($DataTypes -contains 'ASimWebSessionLogs') {
    $t0 = Get-UnixTimeAgo -Minutes 5
    $t1 = Get-UnixTimeAgo -Minutes 0
    Write-Host "`n[ASimWebSessionLogs] GET /organizations/$OrganizationId/apiRequests (t0=$t0, t1=$t1)" -ForegroundColor Cyan
    $r = Invoke-MerakiGet -Uri "$ApiBaseUrl/organizations/$OrganizationId/apiRequests?perPage=1000&t0=$t0&t1=$t1"
    $results.Add(($r | Select-Object @{n='DataType';e={'ASimWebSessionLogs'}}, *))
}

# --- ASimAuditEventLogs (Configuration Changes) : queryWindowInMin=129600, t0+t1; 90 days ---
if ($DataTypes -contains 'ASimAuditEventLogs') {
    $t0 = Get-UnixTimeAgo -Minutes 129600
    $t1 = Get-UnixTimeAgo -Minutes 0
    Write-Host "`n[ASimAuditEventLogs] GET /organizations/$OrganizationId/configurationChanges (t0=$t0, t1=$t1)" -ForegroundColor Cyan
    $auditUri = "$ApiBaseUrl/organizations/$OrganizationId/configurationChanges?perPage=1000&t0=$t0&t1=$t1"
    $r = Invoke-MerakiGet -Uri $auditUri
    $results.Add(($r | Select-Object @{n='DataType';e={'ASimAuditEventLogs'}}, *))

    if ($r.Success) {
        $auditResponse = Invoke-WebRequest -Uri $auditUri -Headers $headers -Method Get -UseBasicParsing
        $auditEvents = @($auditResponse.Content | ConvertFrom-Json)

        Write-Host "`n[ASimAuditEventLogs] Source API response count: $($auditEvents.Count)" -ForegroundColor Yellow
        if ($auditEvents.Count -gt 0) {
            $sourceColumns = $auditEvents[0].PSObject.Properties.Name
            Write-Host "`n[ASimAuditEventLogs] Source API response fields:" -ForegroundColor Yellow
            $sourceColumns | ForEach-Object { Write-Host " - $_" }

            Write-Host "`n[ASimAuditEventLogs] Raw source response sample (first 5 records):" -ForegroundColor Yellow
            $auditEvents | Select-Object -First 5 | Format-List

            $asimPreview = $auditEvents | Select-Object -First 5 | ConvertTo-AsimAuditEventPreview
            Write-Host "`n[ASimAuditEventLogs] ASIMAuditEventLogs columns produced by the DCR transform:" -ForegroundColor Yellow
            $asimPreview[0].PSObject.Properties.Name | ForEach-Object { Write-Host " - $_" }

            Write-Host "`n[ASimAuditEventLogs] ASIMAuditEventLogs-shaped preview (first 5 records):" -ForegroundColor Yellow
            $asimPreview | Format-List
        }
        else {
            Write-Host "`n[ASimAuditEventLogs] No configurationChanges records returned for the 90-day window. Expected ASIMAuditEventLogs columns when data exists:" -ForegroundColor Yellow
            @(
                'TimeGenerated',
                'ActorUsername',
                'ActorUserId',
                'ObjectId',
                'OldValue',
                'NewValue',
                'Object',
                'Operation',
                'EventType',
                'EventResult',
                'EventProduct',
                'EventVendor',
                'EventSeverity',
                'ActorUsernameType',
                'ActorUserType',
                'ActorUserIdType',
                'ObjectType',
                'EventSchemaVersion',
                'EventCount'
            ) | ForEach-Object { Write-Host " - $_" }
        }
    }
}

# --- ASimNetworkSessionLogs (Security/IDS Events) : queryWindowInMin=5, t0+t1 ---
if ($DataTypes -contains 'ASimNetworkSessionLogs') {
    $t0 = Get-UnixTimeAgo -Minutes 5
    $t1 = Get-UnixTimeAgo -Minutes 0
    Write-Host "`n[ASimNetworkSessionLogs] GET /organizations/$OrganizationId/appliance/security/events (t0=$t0, t1=$t1)" -ForegroundColor Cyan
    $r = Invoke-MerakiGet -Uri "$ApiBaseUrl/organizations/$OrganizationId/appliance/security/events?perPage=1000&t0=$t0&t1=$t1"
    $results.Add(($r | Select-Object @{n='DataType';e={'ASimNetworkSessionLogs'}}, *))
}

# Best-effort scrub of the key from memory/process state before returning.
$apiKey = $null
$headers['X-Cisco-Meraki-API-Key'] = $null
[System.GC]::Collect()

Write-Host "`n=== Summary ===" -ForegroundColor Yellow
$results | Select-Object DataType, NetworkId, StatusCode, Success, Count, Error | Format-Table -AutoSize
