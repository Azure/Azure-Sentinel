# =============================================
# Defender Adoption Helper Script
#
# Checks retention, analytics rules, Fusion, and automation rules
# for Sentinel environments. Outputs results to CSV for the HTML dashboard.
#
# Authentication modes:
#   User  - Interactive browser login (delegated permissions, no app registration needed)
#   App   - Client credentials (requires App Registration with Sentinel Reader role)
#
# Usage:
#   .\DefenderAdoptionHelper.ps1 -EnvironmentsFile .\sentinelEnvironments.json -AuthMode User
#   .\DefenderAdoptionHelper.ps1 -EnvironmentsFile .\sentinelEnvironments.json -AuthMode App
#   .\DefenderAdoptionHelper.ps1 -EnvironmentsFile .\sentinelEnvironments.json   (prompts)
#
# Then open dashboard.html and load the CSV.
#
# Author: [Mario Cuomo]
# Date: [27th March, 2026]
# =============================================

param(
    [Parameter(Mandatory = $true)]
    [string]$EnvironmentsFile,
    [Parameter(Mandatory = $false)]
    [string]$OutputFile = "results.csv",
    [Parameter(Mandatory = $false)]
    [ValidateSet("User", "App")]
    [string]$AuthMode
)

# ---- CSV result collector ----
$script:results = [System.Collections.Generic.List[PSCustomObject]]::new()

function Add-Result {
    param(
        [string]$Type,        # env | check | score
        [string]$Environment,
        [string]$ResourceGroup = '',
        [string]$SubscriptionId = '',
        [string]$Section = '',
        [string]$Status = '',  # OK | WARNING
        [int]$Passed = 0,
        [int]$Total = 0,
        [double]$Percent = 0,
        [string]$Message = '',
        [string]$SubItem = ''  # rule name or entity name for grouping
    )
    $script:results.Add([PSCustomObject]@{
        Type           = $Type
        Environment    = $Environment
        ResourceGroup  = $ResourceGroup
        SubscriptionId = $SubscriptionId
        Section        = $Section
        Status         = $Status
        Passed         = $Passed
        Total          = $Total
        Percent        = $Percent
        Message        = $Message
        SubItem        = $SubItem
    })
}

function Show-HeaderInShell {
    param([Parameter(Mandatory=$true)]$Message)
    Write-Host ""; Write-Host "***********************"; Write-Host "$Message"; Write-Host "***********************"
}

# ---- Analysis Functions ----

# Data lake supported regions (Azure internal location names)
$script:dataLakeSupportedRegions = @(
    "canadacentral",
    "centralus", "eastus", "eastus2", "southcentralus", "westus2",
    "southeastasia",
    "centralindia",
    "israelcentral",
    "japaneast",
    "northeurope", "westeurope",
    "francecentral",
    "italynorth",
    "switzerlandnorth",
    "uksouth",
    "australiaeast"
)

function Get-DataLakeRegionCheck {
    $totalControlsTemp = 0; $passedControlsTemp = 0
    $apiVersion = "2021-12-01-preview"
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/${workspaceName}?api-version=$apiVersion"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header
    $location = $response.location
    $totalControlsTemp++
    if ($script:dataLakeSupportedRegions -contains $location) {
        Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " Workspace region '$location' supports Data Lake"
        $passedControlsTemp++
        Add-Result -Type 'check' -Environment $workspaceName -Section 'Data Lake Region' -Status 'OK' -Message "Workspace region '$location' supports Data Lake"
    } else {
        Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Workspace region '$location' does not support Data Lake"
        Add-Result -Type 'check' -Environment $workspaceName -Section 'Data Lake Region' -Status 'WARNING' -Message "Workspace region '$location' does not support Data Lake. Consider migrating to a supported region"
    }
    return $totalControlsTemp, $passedControlsTemp
}

function Get-AnalysisDefenderData {
    param([Parameter(Mandatory=$true)]$defenderTables)
    $totalControlsTemp = 0; $passedControlsTemp = 0
    $apiVersion = "2025-02-01"
    foreach ($table in $defenderTables) {
        $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/tables/${table}?api-version=$apiVersion"
        try {
            $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header -ErrorAction Stop
        } catch {
            $errBody = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($errBody.error.code -eq "SolutionNotActive") {
                Write-Host "[INFORMATIONAL]" -ForegroundColor Cyan -NoNewline; Write-Host " The table $table is not active (Sentinel solution not enabled) - skipping"
                Add-Result -Type 'check' -Environment $workspaceName -Section 'Defender Data' -Status 'INFORMATIONAL' -Message "The table $table is not active - Sentinel solution not enabled on this workspace"
            } else {
                Write-Host "[INFORMATIONAL]" -ForegroundColor Cyan -NoNewline; Write-Host " The table $table could not be queried: $($_.Exception.Message)"
                Add-Result -Type 'check' -Environment $workspaceName -Section 'Defender Data' -Status 'INFORMATIONAL' -Message "The table $table could not be queried: $($_.Exception.Message)"
            }
            continue
        }
        $retentionPeriod = $response.properties.totalRetentionInDays
        $totalControlsTemp++
        if ($response.properties.totalRetentionInDays -lt 31) {
            Write-Host "[INFORMATIONAL]" -ForegroundColor Cyan -NoNewline; Write-Host " The table $table has a retention of $retentionPeriod days - no need to ingest this data in Sentinel"
            $passedControlsTemp++
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Defender Data' -Status 'INFORMATIONAL' -Message "The table $table has a retention of $retentionPeriod days - no need to ingest this data in Sentinel"
        } else {
            $passedControlsTemp++
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The table $table has a retention of $retentionPeriod days - need to be stored in Sentinel for more retention"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Defender Data' -Status 'OK' -Message "The table $table has a retention of $retentionPeriod days - need to be stored in Sentinel for more retention"
        }
    }
    return $totalControlsTemp, $passedControlsTemp
}

function Get-AnalyticsAnalysis {
    $totalControlsTemp = 0; $passedControlsTemp = 0
    $apiVersion = "2025-07-01-preview"

    ## FUSION ENGINE
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/alertRules/BuiltInFusion?api-version=$apiVersion"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header
    $totalControlsTemp++
    if ($null -eq $response) {
        Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The Fusion engine is not enabled"
        $passedControlsTemp++
        Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'OK' -Message "The Fusion engine is not enabled"
    }
    if ($response.properties.enabled) {
        Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Fusion rules will be automatically disabled after Microsoft Sentinel is onboarded in Defender"
        Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'WARNING' -Message "Fusion rules will be automatically disabled after Microsoft Sentinel is onboarded in Defender"
    } else {
        Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The Fusion engine is not enabled"
        $passedControlsTemp++
        Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'OK' -Message "The Fusion engine is not enabled"
    }

    ## ALL RULES
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/alertRules?api-version=$apiVersion"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header
    foreach ($rule in $response.value) {
        if ($rule.properties.displayName -eq "Advanced Multistage Attack Detection") { continue }
        $ruleName = $rule.properties.displayName

        $totalControlsTemp++
        $ruleHasIssue = $false

        ## DISABLED RULE (informational only, counts as passed)
        if ($rule.properties.enabled -eq $false) {
            Write-Host "[INFORMATIONAL]" -ForegroundColor Cyan -NoNewline; Write-Host " The rule $ruleName is disabled"
            $passedControlsTemp++
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'INFORMATIONAL' -SubItem $ruleName -Message "Rule is disabled. It will remain disabled after onboarding"
            continue
        }

        ## ALERT VISIBILITY
        if (!$rule.properties.incidentConfiguration.createIncident) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " The rule $ruleName doesn't generate incidents"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'WARNING' -SubItem $ruleName -Message "Doesn't generate incidents. Alerts aren't visible in the Defender portal - they appear in SecurityAlerts table in Advanced Hunting"
            $ruleHasIssue = $true
        } else {
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'OK' -SubItem $ruleName -Message "Alert visibility configured correctly"
        }

        ## INCIDENT REOPENING
        if ($rule.properties.incidentConfiguration.groupingConfiguration.reopenClosedIncident) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " The rule $ruleName has incident reopening enabled"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'WARNING' -SubItem $ruleName -Message "Incident reopening enabled. Not supported in Defender portal - new incidents are created instead"
            $ruleHasIssue = $true
        } else {
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'OK' -SubItem $ruleName -Message "No incident reopening"
        }

        ## ALERT GROUPING
        if ($rule.properties.incidentConfiguration.groupingConfiguration.enabled) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " The rule $ruleName has alert grouping enabled"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'WARNING' -SubItem $ruleName -Message "Alert grouping enabled. After onboarding, Defender XDR engine fully controls grouping and merging"
            $ruleHasIssue = $true
        } else {
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'OK' -SubItem $ruleName -Message "No custom alert grouping"
        }

        ## MICROSOFT INCIDENT CREATION RULES
        if ($rule.kind -eq "MicrosoftSecurityIncidentCreation") {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " The rule $ruleName is a Microsoft incident creation rule"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Analytics' -Status 'WARNING' -SubItem $ruleName -Message "Microsoft incident creation rule - will be deactivated after onboarding"
            $ruleHasIssue = $true
        }

        if (-not $ruleHasIssue) { $passedControlsTemp++ }
    }
    return $totalControlsTemp, $passedControlsTemp
}

function Get-TableTiersAnalysis {
    $totalControlsTemp = 0; $passedControlsTemp = 0
    $apiVersion = "2022-10-01"
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/tables?api-version=$apiVersion"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header
    foreach ($table in $response.value) {
        $tableName = $table.name
        $plan = $table.properties.plan
        $totalControlsTemp++
        if ($plan -eq "Basic") {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " $tableName [$plan] - must be converted to Analytics or Auxiliary tier (Data Lake) when transitioning to Defender"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Table Tiers' -Status 'WARNING' -SubItem $tableName -Message "Uses Basic tier. Must be converted to Analytics or Auxiliary tier (Data Lake) when transitioning to Defender"
        } elseif ($plan -eq "Auxiliary") {
            Write-Host "[INFORMATIONAL]" -ForegroundColor Cyan -NoNewline; Write-Host " $tableName [$plan] - will become a data lake table when transitioning to Defender"
            $passedControlsTemp++
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Table Tiers' -Status 'INFORMATIONAL' -SubItem $tableName -Message "Uses Auxiliary tier. Will become a data lake table when transitioning to Defender"
        } else {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " $tableName [$plan]"
            $passedControlsTemp++
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Table Tiers' -Status 'OK' -SubItem $tableName -Message "Uses $plan tier"
        }
    }
    return $totalControlsTemp, $passedControlsTemp
}

function Get-AutomationAnalysis {
    $totalControlsTemp = 0; $passedControlsTemp = 0
    $apiVersion = "2025-09-01"
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/automationRules?api-version=$apiVersion"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header
    foreach ($rule in $response.value) {
        $totalControlsTemp++
        $triggeringLogic = $rule.properties.triggeringLogic
        $isEnabled = $triggeringLogic.isEnabled
        $triggersOn = $triggeringLogic.triggersOn
        $triggersWhen = $triggeringLogic.triggersWhen
        $conditions = $triggeringLogic.conditions
        $incidentTitle = $false; $incidentProvider = $false; $fusionMentioned = $false
        $usesDescription = $false; $usesUpdatedBy365 = $false

        if ($isEnabled -and $conditions) {
            foreach ($condition in $conditions) {
                if ($condition.conditionType -eq "Property" -and $condition.conditionProperties.propertyName -eq "IncidentTitle") { $incidentTitle = $true }
                if ($condition.conditionType -eq "Property" -and $condition.conditionProperties.propertyName -eq "IncidentProviderName") { $incidentProvider = $true }
                if ($condition.conditionType -eq "Property" -and $condition.conditionProperties.propertyName -eq "IncidentRelatedAnalyticRuleIds" -and ($condition.conditionProperties.propertyValues | Where-Object { $_ -like "*BuiltInFusion" })) { $fusionMentioned = $true }
                if ($condition.conditionType -eq "Property" -and $condition.conditionProperties.propertyName -eq "IncidentDescription") { $usesDescription = $true }
                if ($condition.conditionType -eq "Property" -and $condition.conditionProperties.propertyName -eq "IncidentUpdatedBySource" -and ($condition.conditionProperties.propertyValues | Where-Object { $_ -like "*365*" -or $_ -like "*Defender*" })) { $usesUpdatedBy365 = $true }
                if ($incidentTitle -and $incidentProvider -and $fusionMentioned) { break }
            }
        }
        $ruleName = $rule.properties.displayName
        $hasIssue = $false
        if ($incidentTitle) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Automation rule ${ruleName}: change Incident Title to Analytics Rule Name"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Automation' -Status 'WARNING' -SubItem $ruleName -Message "Change trigger from Incident Title to Analytics Rule Name"
            $hasIssue = $true
        }
        if ($incidentProvider) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Automation rule ${ruleName}: change Incident Provider to Alert Product Name"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Automation' -Status 'WARNING' -SubItem $ruleName -Message "Change trigger from Incident Provider to Alert Product Name"
            $hasIssue = $true
        }
        if ($fusionMentioned) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Automation rule ${ruleName}: triggered by Fusion"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Automation' -Status 'WARNING' -SubItem $ruleName -Message "Triggered by Fusion incidents. Fusion will be disabled after onboarding"
            $hasIssue = $true
        }
        if ($usesDescription) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Automation rule ${ruleName}: uses Description field as condition"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Automation' -Status 'WARNING' -SubItem $ruleName -Message "Uses Description field as condition. Field removed from SecurityIncident after onboarding"
            $hasIssue = $true
        }
        if ($usesUpdatedBy365) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Automation rule ${ruleName}: uses Updated By = Microsoft 365 Defender"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Automation' -Status 'WARNING' -SubItem $ruleName -Message "Uses Updated By = Microsoft 365 Defender. Value becomes Other after onboarding"
            $hasIssue = $true
        }
        ## ALERT TRIGGER CHECK
        if ($isEnabled -and $triggersOn -eq "Alerts") {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Automation rule ${ruleName}: uses alert trigger - will only act on Sentinel alerts after onboarding"
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Automation' -Status 'WARNING' -SubItem $ruleName -Message "Uses alert trigger. After onboarding, alert triggers act only on Sentinel alerts"
            $hasIssue = $true
        }
        if (!$hasIssue) {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The automation rule $ruleName is configured correctly"
            $passedControlsTemp++
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Automation' -Status 'OK' -SubItem $ruleName -Message "Configured correctly"
        }
    }
    return $totalControlsTemp, $passedControlsTemp
}

# =============================================
# MAIN
# =============================================

Write-Host ""
Write-Host "  =======================================" -ForegroundColor Cyan
Write-Host "       DEFENDER ADOPTION HELPER          " -ForegroundColor Cyan
Write-Host "  =======================================" -ForegroundColor Cyan
Write-Host ""

# ---- Auth mode selection ----
if (-not $AuthMode) {
    Write-Host "Select authentication mode:" -ForegroundColor Yellow
    Write-Host "  [1] User  - Interactive login (browser)" -ForegroundColor White
    Write-Host "  [2] App   - Client credentials (service principal)" -ForegroundColor White
    $choice = Read-Host "Enter 1 or 2"
    switch ($choice) {
        "1" { $AuthMode = "User" }
        "2" { $AuthMode = "App" }
        default { Write-Host "Invalid selection. Defaulting to User." -ForegroundColor Yellow; $AuthMode = "User" }
    }
}
Write-Host "Auth mode: $AuthMode" -ForegroundColor Green

$environments = Get-Content $EnvironmentsFile | ConvertFrom-Json
Write-Host "$($environments.Count) environment(s) found" -ForegroundColor Green

$resource = "https://management.azure.com/"

# ---- Acquire token based on auth mode ----
function Get-AccessToken {
    param([string]$TenantId)

    if ($script:AuthMode -eq "App") {
        # --- App (client credentials) ---
        if (-not $script:appTenantId) {
            $script:appTenantId = Read-Host "Enter Tenant ID"
            $script:appClientId = Read-Host "Enter Client (App) ID"
            $script:appClientSecret = Read-Host "Enter Client Secret" 
        }
        $authUrl = "https://login.microsoftonline.com/$($script:appTenantId)/oauth2/token"
        $body = @{
            grant_type    = "client_credentials"
            client_id     = $script:appClientId
            client_secret = $script:appClientSecret
            resource      = $resource
        }
        $tokenResponse = Invoke-RestMethod -Method Post -Uri $authUrl -Body $body
        return $tokenResponse.access_token
    }
    else {
        # --- User (device code flow) ---
        # Uses well-known Azure PowerShell first-party client ID (no app registration needed)
        $userClientId = "1950a258-227b-4e31-a9cf-717495945fc2"
        $tenant = if ($TenantId) { $TenantId } else { "common" }
        $deviceCodeUrl = "https://login.microsoftonline.com/$tenant/oauth2/v2.0/devicecode"
        $tokenUrl      = "https://login.microsoftonline.com/$tenant/oauth2/v2.0/token"
        $scope = "https://management.azure.com/.default offline_access"

        # Request device code
        $dcResponse = Invoke-RestMethod -Method Post -Uri $deviceCodeUrl -Body @{
            client_id = $userClientId
            scope     = $scope
        }
        Write-Host ""
        Write-Host "  $($dcResponse.message)" -ForegroundColor Yellow
        Write-Host ""

        # Poll for token
        $interval = $dcResponse.interval
        $expiresIn = $dcResponse.expires_in
        $elapsed = 0
        while ($elapsed -lt $expiresIn) {
            Start-Sleep -Seconds $interval
            $elapsed += $interval
            try {
                $tokenResponse = Invoke-RestMethod -Method Post -Uri $tokenUrl -Body @{
                    grant_type  = "urn:ietf:params:oauth:grant-type:device_code"
                    client_id   = $userClientId
                    device_code = $dcResponse.device_code
                }
                Write-Host "  Authenticated successfully!" -ForegroundColor Green
                return $tokenResponse.access_token
            } catch {
                $err = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
                if ($err.error -eq "authorization_pending") { continue }
                if ($err.error -eq "slow_down") { $interval += 5; continue }
                throw $_
            }
        }
        throw "Device code login timed out."
    }
}

# Get initial token (for User mode we authenticate once; for App mode credentials are prompted once)
$firstEnv = $environments[0]
$accessToken = Get-AccessToken -TenantId $null
$header = @{ Authorization = "Bearer $accessToken"; ContentType = "application/json" }

Write-Host "Generating CSV results..." -ForegroundColor Green

foreach ($env in $environments) {
    $subscriptionId = $env.subscriptionId
    $resourceGroupName = $env.resourceGroupName
    $workspaceName = $env.workspaceName
    Write-Host "`nAnalyzing $workspaceName..." -ForegroundColor Cyan

    Add-Result -Type 'env' -Environment $workspaceName -ResourceGroup $resourceGroupName -SubscriptionId $subscriptionId

    # ---- Permission check: verify Sentinel Reader access ----
    $testUri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/alertRules?api-version=2024-03-01" + '&$top=1'
    $accessOk = $true
    try {
        Invoke-RestMethod -Uri $testUri -Headers $header -ErrorAction Stop | Out-Null
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $errBody = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($statusCode -eq 403 -or $statusCode -eq 401) {
            Write-Host "   [ERROR] No Sentinel Reader access on $workspaceName. Skipping." -ForegroundColor Red
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Access' -Status 'WARNING' -Message "The app does not have Microsoft Sentinel Reader role on this workspace. Assign the role and retry."
            Add-Result -Type 'score' -Environment $workspaceName -Section 'Final' -Passed 0 -Total 1 -Percent 0
            $accessOk = $false
        } elseif ($errBody.error.code -eq "SolutionNotActive" -or ($statusCode -eq 400 -and $errBody.error.message -match "not onboarded to Microsoft Sentinel")) {
            Write-Host "   [ERROR] Microsoft Sentinel is not installed on $workspaceName. Skipping." -ForegroundColor Red
            Add-Result -Type 'check' -Environment $workspaceName -Section 'Access' -Status 'WARNING' -Message "Microsoft Sentinel is not installed on this workspace. Enable Sentinel and retry."
            Add-Result -Type 'score' -Environment $workspaceName -Section 'Final' -Passed 0 -Total 1 -Percent 0
            $accessOk = $false
        } else {
            Write-Host "   [WARN] API test failed ($statusCode): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    if (-not $accessOk) { continue }

    $defenderTables = @("DeviceInfo","DeviceNetworkInfo","DeviceProcessEvents","DeviceNetworkEvents","DeviceFileEvents","DeviceRegistryEvents","DeviceLogonEvents","DeviceImageLoadEvents","DeviceEvents","DeviceFileCertificateInfo","EmailEvents","EmailUrlInfo","EmailAttachmentInfo","EmailPostDeliveryEvents","UrlClickEvents","CloudAppEvents","IdentityLogonEvents","IdentityQueryEvents","IdentityDirectoryEvents","AlertInfo","AlertEvidence")

    $totalControls = 0; $totalPassedControls = 0

    Show-HeaderInShell "DEFENDER DATA"
    $t, $p = Get-AnalysisDefenderData -defenderTables $defenderTables
    $totalControls += $t; $totalPassedControls += $p
    Add-Result -Type 'score' -Environment $workspaceName -Section 'Defender Data' -Passed $p -Total $t -Percent $(if($t -gt 0){[math]::Round(($p/$t)*100,2)}else{100})

    Show-HeaderInShell "ANALYTICS"
    $t, $p = Get-AnalyticsAnalysis
    $totalControls += $t; $totalPassedControls += $p
    Add-Result -Type 'score' -Environment $workspaceName -Section 'Analytics' -Passed $p -Total $t -Percent $(if($t -gt 0){[math]::Round(($p/$t)*100,2)}else{100})

    Show-HeaderInShell "AUTOMATION"
    $t, $p = Get-AutomationAnalysis
    $totalControls += $t; $totalPassedControls += $p
    Add-Result -Type 'score' -Environment $workspaceName -Section 'Automation' -Passed $p -Total $t -Percent $(if($t -gt 0){[math]::Round(($p/$t)*100,2)}else{100})

    $finalPct = if($totalControls -gt 0){[math]::Round(($totalPassedControls/$totalControls)*100,2)}else{100}
    Add-Result -Type 'score' -Environment $workspaceName -Section 'Final' -Passed $totalPassedControls -Total $totalControls -Percent $finalPct
    Write-Host ('Final Score: {0}/{1} ({2}%)' -f $totalPassedControls, $totalControls, $finalPct) -ForegroundColor Cyan

    # ---- data lake Readiness (does not contribute to final score) ----
    Show-HeaderInShell "DATA LAKE READINESS - Region"
    $t, $p = Get-DataLakeRegionCheck
    Add-Result -Type 'score' -Environment $workspaceName -Section 'Data Lake Region' -Passed $p -Total $t -Percent $(if($t -gt 0){[math]::Round(($p/$t)*100,2)}else{100})

    Show-HeaderInShell "DATA LAKE READINESS - Table Tiers"
    $t, $p = Get-TableTiersAnalysis
    Add-Result -Type 'score' -Environment $workspaceName -Section 'Table Tiers' -Passed $p -Total $t -Percent $(if($t -gt 0){[math]::Round(($p/$t)*100,2)}else{100})
}

$scriptDir = if ($MyInvocation.MyCommand.Path) { Split-Path $MyInvocation.MyCommand.Path } else { Get-Location }
$savePath = Join-Path $scriptDir $OutputFile
$script:results | Export-Csv -Path $savePath -NoTypeInformation -Encoding UTF8
Write-Host ('CSV saved to {0}' -f $savePath) -ForegroundColor Green
Write-Host 'Open dashboard.html and load the CSV to view the report.' -ForegroundColor Green
