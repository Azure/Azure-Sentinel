<#
.SYNOPSIS
    Deploys custom detection rules to Microsoft 365 Defender via the
    Microsoft Graph Security API (beta).

.DESCRIPTION
    Reads detection rule definitions from a JSON array file and creates each
    rule by POSTing to:
        POST https://graph.microsoft.com/beta/security/rules/detectionRules

    The script supports two authentication methods:
      1. User-Assigned Managed Identity (UAMI) — default for Azure Automation.
      2. Service Principal (SPN) — for running outside Azure or in pipelines.

    The identity used must have the CustomDetection.ReadWrite.All application
    permission (admin-consented) on Microsoft Graph.

    Authentication selection (checked in order):
      - If TenantId + ClientId + ClientSecret are provided (as parameters or
        Automation Variables 'DetectionRulesTenantId', 'DetectionRulesClientId',
        'DetectionRulesClientSecret'), SPN auth is used.
      - Otherwise, Managed Identity auth is used (requires ManagedIdentityClientId
        or the Automation Variable 'DetectionRulesManagedIdentityClientId').

    Existing rules whose displayName already matches are skipped to keep the
    operation idempotent.

    Designed to run as an Azure Automation runbook before data-ingestion so
    that rules are already active when telemetry arrives.

.PARAMETER ManagedIdentityClientId
    Client ID of the User-Assigned Managed Identity. If omitted, the script
    reads it from the Automation Variable 'DetectionRulesManagedIdentityClientId'.
    Ignored when SPN parameters are provided.

.PARAMETER TenantId
    Microsoft Entra tenant ID for service principal authentication.

.PARAMETER ClientId
    Application (client) ID of the service principal.

.PARAMETER ClientSecret
    Client secret of the service principal.

.PARAMETER RulesUrl
    Direct URL to the detection rules JSON file. Defaults to the master branch.
#>
param(
    [string]$ManagedIdentityClientId,
    [string]$TenantId,
    [string]$ClientId,
    [string]$ClientSecret,
    [string]$RulesUrl = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Training/Microsoft-Sentinel-Training-Lab/Artifacts/DetectionRules/rules.json"
)

$ErrorActionPreference = "Stop"

# ── Helper: read Automation Variable (returns $null outside Automation) ──────
function Get-OptionalAutomationVariableValue {
    param([string]$Name)
    try { $v = Get-AutomationVariable -Name $Name; return $v.Trim().Trim('"') }
    catch { return $null }
}

# ── Resolve SPN credentials from Automation Variables if not passed ──────────
if (-not $TenantId)     { $TenantId     = Get-OptionalAutomationVariableValue -Name 'DetectionRulesTenantId' }
if (-not $ClientId)     { $ClientId     = Get-OptionalAutomationVariableValue -Name 'DetectionRulesClientId' }
if (-not $ClientSecret) { $ClientSecret = Get-OptionalAutomationVariableValue -Name 'DetectionRulesClientSecret' }

# ── Authenticate ─────────────────────────────────────────────────────────────
Import-Module Az.Accounts -ErrorAction Stop

$useSpn = $TenantId -and $ClientId -and $ClientSecret

if ($useSpn) {
    # ── Service Principal authentication ─────────────────────────────────────
    Write-Output "Authenticating with Service Principal (ClientId: $ClientId)"
    $secureSecret = ConvertTo-SecureString $ClientSecret -AsPlainText -Force
    $credential   = New-Object System.Management.Automation.PSCredential($ClientId, $secureSecret)
    Connect-AzAccount -ServicePrincipal -TenantId $TenantId -Credential $credential | Out-Null
}
else {
    # ── Managed Identity authentication ──────────────────────────────────────
    if (-not $ManagedIdentityClientId) {
        try {
            $raw = Get-AutomationVariable -Name 'DetectionRulesManagedIdentityClientId'
            $ManagedIdentityClientId = $raw.Trim().Trim('"')
        }
        catch {
            throw "No authentication method available. Provide TenantId + ClientId + ClientSecret for SPN auth, or ManagedIdentityClientId (or set Automation Variable 'DetectionRulesManagedIdentityClientId') for Managed Identity auth."
        }
    }
    Write-Output "Authenticating with Managed Identity (ClientId: $ManagedIdentityClientId)"
    Connect-AzAccount -Identity -AccountId $ManagedIdentityClientId | Out-Null
}

# Acquire a token for Microsoft Graph
$graphToken = (Get-AzAccessToken -ResourceUrl "https://graph.microsoft.com").Token
$headers = @{
    "Authorization" = "Bearer $graphToken"
    "Content-Type"  = "application/json"
}

# Retry settings for tables that may not exist yet (e.g., OktaV2_CL)
$retryMaxAttempts  = 6
$retryDelaySeconds = 300

# ── Download rules file ──────────────────────────────────────────────────────
$workdir = Join-Path -Path $env:TEMP -ChildPath "sentinel-training-demo"
if (-not (Test-Path -Path $workdir)) {
    New-Item -ItemType Directory -Path $workdir | Out-Null
}

$rulesFile = Join-Path -Path $workdir -ChildPath "rules.json"
Write-Output "Downloading rules file from $RulesUrl ..."
Invoke-WebRequest -Uri $RulesUrl -OutFile $rulesFile -UseBasicParsing

$rules = Get-Content -Path $rulesFile -Raw | ConvertFrom-Json
Write-Output "Loaded $($rules.Count) detection rule(s)"

# ── Fetch existing rules for idempotency ─────────────────────────────────────
$graphBaseUrl   = "https://graph.microsoft.com/beta/security/rules/detectionRules"

Write-Output "Fetching existing custom detection rules..."
$existingRules  = @()
$nextLink       = $graphBaseUrl

while ($nextLink) {
    $response  = Invoke-RestMethod -Uri $nextLink -Headers $headers -Method Get
    $existingRules += $response.value
    $nextLink  = $response.'@odata.nextLink'
}

$existingNames = $existingRules | ForEach-Object { $_.displayName }
Write-Output "Found $($existingRules.Count) existing rule(s)"

# ── Create rules ─────────────────────────────────────────────────────────────
$created = 0
$skipped = 0

foreach ($rule in $rules) {
    if ($rule.displayName -in $existingNames) {
        Write-Output "SKIP  : '$($rule.displayName)' already exists"
        $skipped++
        continue
    }

    $body = $rule | ConvertTo-Json -Depth 10 -Compress
    $queryText = $rule.queryCondition.queryText
    $requiresOktaTable = $queryText -match '\bOktaV2_CL\b'
    Write-Output "CREATE: '$($rule.displayName)' ..."

    $attempt = 1
    while ($true) {
        try {
            $result = Invoke-RestMethod -Uri $graphBaseUrl `
                -Headers $headers `
                -Method Post `
                -Body $body

            Write-Output "  -> Created with id $($result.id)"
            $created++
            break
        }
        catch {
            $statusCode = $_.Exception.Response.StatusCode.value__
            $detail     = $_.ErrorDetails.Message
            $isSyntaxError = $detail -match 'syntax errors'

            if ($requiresOktaTable -and $isSyntaxError -and $attempt -lt $retryMaxAttempts) {
                Write-Warning "  -> FAILED ($statusCode): $detail"
                Write-Output "  -> Waiting $retryDelaySeconds seconds for OktaV2_CL to appear (attempt $attempt/$retryMaxAttempts)..."
                Start-Sleep -Seconds $retryDelaySeconds
                $attempt++
                continue
            }

            Write-Warning "  -> FAILED ($statusCode): $detail"
            break
        }
    }
}

Write-Output "`nDone. Created: $created | Skipped: $skipped | Total in file: $($rules.Count)"
