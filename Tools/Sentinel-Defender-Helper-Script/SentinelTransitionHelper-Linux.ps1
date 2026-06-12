<#
.SYNOPSIS
    Analyzes Microsoft Sentinel environments for Defender XDR integration readiness.

.DESCRIPTION
    The Defender Adoption Helper Script (Linux Version) analyzes Microsoft Sentinel workspaces
    to assess their readiness for integration with Microsoft Defender XDR. It automatically
    discovers Sentinel workspaces in your subscription and generates comprehensive reports.

    Key Features:
    - Auto-discovers all Sentinel workspaces in a subscription
    - Interactive subscription selection with device code authentication
    - Analyzes Defender table retention settings
    - Reviews analytics rules and Fusion engine configuration
    - Validates automation rules for best practices
    - Generates HTML reports with visual charts and statistics

    Requirements:
    - PowerShell Core (pwsh) 7.0 or higher
    - Azure CLI (az) installed and configured
    - Reader or Contributor access to target Sentinel workspaces

.PARAMETER FileName
    Optional. Name of the HTML report file to generate (without extension).
    If not specified, results are only displayed in the console.

    Example: -FileName "sentinel-analysis"
    Output: sentinel-analysis.html

.PARAMETER SubscriptionId
    Optional. Azure subscription ID to analyze.
    If not specified, the script will show an interactive list of available subscriptions.

    Example: -SubscriptionId "12345678-1234-1234-1234-123456789abc"

.EXAMPLE
    pwsh ./SentinelTransitionHelper-Linux.ps1 -FileName report

    Interactive mode: Select subscription from list, auto-discover all Sentinel workspaces,
    and generate report.html with full analysis.

.EXAMPLE
    pwsh ./SentinelTransitionHelper-Linux.ps1

    Console-only mode: Interactive subscription selection, results displayed in terminal only.

.EXAMPLE
    pwsh ./SentinelTransitionHelper-Linux.ps1 -SubscriptionId "12345678-1234-1234-1234-123456789abc" -FileName analysis

    Direct mode: Analyze specific subscription and generate analysis.html report.

.NOTES
    Author: Edvinas Kubilius
    Inspired by: Mario Cuomo's original Defender Adoption Helper concept
    Date: November 17, 2025
    Version: 2.0 (Linux/Azure CLI Version)


.LINK
    https://learn.microsoft.com/en-us/azure/sentinel/
#>

# Script Parameters
param(
    [Parameter(Mandatory = $false)]
    [string]$FileName = $null,
    [Parameter(Mandatory = $false)]
    [string]$SubscriptionId = $null
)

# HTML Report Builder Class
class HtmlReportBuilder {
    [System.Collections.ArrayList]$Content
    [string]$Title

    HtmlReportBuilder([string]$title) {
        $this.Content = [System.Collections.ArrayList]::new()
        $this.Title = $title
        $this.InitializeHtml()
    }

    [void] InitializeHtml() {
        $this.Content.Add(@"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$($this.Title)</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        h1 {
            color: #0078d4;
            border-bottom: 3px solid #0078d4;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        h2 {
            color: #106ebe;
            margin-top: 30px;
            border-bottom: 2px solid #106ebe;
            padding-bottom: 8px;
        }
        h3 {
            color: #004578;
            margin-top: 20px;
        }
        .ok {
            color: #107c10;
            font-weight: bold;
        }
        .warning {
            color: #ff8c00;
            font-weight: bold;
        }
        .info {
            background-color: #e8f4fd;
            padding: 15px;
            border-left: 4px solid #0078d4;
            margin: 15px 0;
        }
        .stat-box {
            background-color: #f0f0f0;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
            font-weight: bold;
        }
        ul {
            line-height: 1.8;
        }
        .env-box {
            background-color: #fafafa;
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .rule-section {
            border-left: 3px solid #ccc;
            padding-left: 15px;
            margin: 20px 0;
        }
        .page-break {
            page-break-before: always;
            margin-top: 40px;
        }
        .toc {
            background-color: #f8f8f8;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 20px;
        }
        .toc a {
            color: #0078d4;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        .chart-container {
            width: 500px;
            height: 300px;
            margin: 20px auto;
        }
        @media print {
            .page-break {
                page-break-before: always;
            }
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
<div class="container">
"@) | Out-Null
    }

    [void] AddHeading1([string]$text) {
        $this.Content.Add("<h1>$text</h1>") | Out-Null
    }

    # Method overloads for AddHeading2
    [void] AddHeading2([string]$text) {
        $this.Content.Add("<h2>$text</h2>") | Out-Null
    }

    [void] AddHeading2([string]$text, [string]$id) {
        $this.Content.Add("<h2 id='$id'>$text</h2>") | Out-Null
    }

    # Method overloads for AddHeading3
    [void] AddHeading3([string]$text) {
        $this.Content.Add("<h3>$text</h3>") | Out-Null
    }

    [void] AddHeading3([string]$text, [string]$id) {
        $this.Content.Add("<h3 id='$id'>$text</h3>") | Out-Null
    }

    [void] AddParagraph([string]$text) {
        $this.Content.Add("<p>$text</p>") | Out-Null
    }

    [void] AddOkMessage([string]$text) {
        $this.Content.Add("<p><span class='ok'>[OK]</span> $text</p>") | Out-Null
    }

    [void] AddWarningMessage([string]$text) {
        $this.Content.Add("<p><span class='warning'>[WARNING]</span> $text</p>") | Out-Null
    }

    [void] AddStatBox([string]$text) {
        $this.Content.Add("<div class='stat-box'>$text</div>") | Out-Null
    }

    [void] AddInfoBox([string]$text) {
        $this.Content.Add("<div class='info'>$text</div>") | Out-Null
    }

    [void] StartList() {
        $this.Content.Add("<ul>") | Out-Null
    }

    [void] AddListItem([string]$text) {
        $this.Content.Add("<li>$text</li>") | Out-Null
    }

    [void] EndList() {
        $this.Content.Add("</ul>") | Out-Null
    }

    [void] AddPageBreak() {
        $this.Content.Add("<div class='page-break'></div>") | Out-Null
    }

    [void] AddChart([string]$chartId, [int]$passed, [int]$failed) {
        $chartHtml = @"
<div class="chart-container">
    <canvas id="$chartId"></canvas>
</div>
<script>
    const ctx$chartId = document.getElementById('$chartId').getContext('2d');
    new Chart(ctx$chartId, {
        type: 'pie',
        data: {
            labels: ['Passed Controls', 'Not Passed Controls'],
            datasets: [{
                data: [$passed, $failed],
                backgroundColor: ['#57BF67', '#FF0000'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                title: {
                    display: true,
                    text: 'Final Score Distribution'
                }
            }
        }
    });
</script>
"@
        $this.Content.Add($chartHtml) | Out-Null
    }

    [void] Finalize() {
        $this.Content.Add(@"
</div>
</body>
</html>
"@) | Out-Null
    }

    [void] SaveToFile([string]$filePath) {
        $this.Finalize()
        $this.Content -join "`n" | Out-File -FilePath $filePath -Encoding UTF8
    }
}

# Function to print a section header in the shell
function Show-HeaderInShell {
    param(
        [Parameter(Mandatory = $true)]
        $Message
    )
    Write-Host ""
    Write-Host "***********************"
    Write-Host "$Message"
    Write-Host "***********************"
}

function Get-AnalysisDefenderData {
    param (
        [Parameter(Mandatory = $true)]
        $defenderTables,
        [Parameter(Mandatory = $false)]
        $HtmlBuilder
    )

    $totalControlsTemp = 0
    $passedControlsTemp = 0
    $apiVersion = "2025-02-01"
    foreach ($table in $defenderTables) {
        $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/tables/${table}?api-version=$apiVersion"
        $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header
        $retentionPeriod = $response.properties.totalRetentionInDays
        $totalControlsTemp = $totalControlsTemp + 1

        if ($response.properties.totalRetentionInDays -lt 31) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " The table $table has a retention of $retentionPeriod days - no need to ingest this data in Sentinel"
            if ($reportRequested) {
                $HtmlBuilder.AddWarningMessage("The table <code>$table</code> has a retention of $retentionPeriod days - no need to ingest this data in Sentinel")
            }
        }
        else {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The table $table has a retention of $retentionPeriod days - need to be stored in Sentinel for more retention"
            $passedControlsTemp = $passedControlsTemp + 1
            if ($reportRequested) {
                $HtmlBuilder.AddOkMessage("The table <code>$table</code> has a retention of $retentionPeriod days - need to be stored in Sentinel for more retention")
            }
        }
    }
    return $totalControlsTemp, $passedControlsTemp
}

function Get-AnalyticsAnalysis {
    param (
        [Parameter(Mandatory = $false)]
        $HtmlBuilder
    )

    $totalControlsTemp = 0
    $passedControlsTemp = 0

    ## FUSION ENGINE
    $apiVersion = "2025-06-01"
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/alertRules/BuiltInFusion?api-version=$apiVersion"

    try {
        $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header -ErrorAction Stop
        $totalControlsTemp++

        if ($response.properties.enabled) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Fusion rules will be automatically disabled after Microsoft Sentinel is onboarded in Defender"
            if ($reportRequested) {
                $HtmlBuilder.AddWarningMessage("Fusion rules will be automatically disabled after Microsoft Sentinel is onboarded in Defender")
            }
        }
        else {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The Fusion engine is not enabled"
            $passedControlsTemp++
            if ($reportRequested) {
                $HtmlBuilder.AddOkMessage("The Fusion engine is not enabled")
            }
        }
    }
    catch {
        # Fusion rule doesn't exist (404 NotFound) - this is OK
        $totalControlsTemp++
        $passedControlsTemp++
        Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The Fusion engine is not enabled"
        if ($reportRequested) {
            $HtmlBuilder.AddOkMessage("The Fusion engine is not enabled")
        }
    }

    ## ALERT VISIBILITY
    $apiVersion = "2025-06-01"
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/alertRules?api-version=$apiVersion"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header
    foreach ($rule in $response.value) {
        if ($rule.properties.displayName -eq "Advanced Multistage Attack Detection") {
            continue
        }
        $totalControlsTemp++

        $ruleName = $($rule.properties.displayName)

        if (!$rule.properties.incidentConfiguration.createIncident) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " The rule $ruleName doesn't generate incidents. The alerts aren't visible in the Defender portal. They appear in SecurityAlerts table in Advanced Hunting"
            if ($reportRequested) {
                $HtmlBuilder.AddWarningMessage("The rule <em>$ruleName</em> doesn't generate incidents. The alerts aren't visible in the Defender portal. They appear in SecurityAlerts table in Advanced Hunting")
            }
        }
        else {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The rule $ruleName is configured correctly"
            $passedControlsTemp++
            if ($reportRequested) {
                $HtmlBuilder.AddOkMessage("The rule <em>$ruleName</em> is configured correctly")
            }
        }
    }

    return $totalControlsTemp, $passedControlsTemp
}

function Get-AutomationAnalysis {
    param (
        [Parameter(Mandatory = $false)]
        $HtmlBuilder
    )

    $totalControlsTemp = 0
    $passedControlsTemp = 0

    $apiVersion = "2025-09-01"
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/automationRules?api-version=$apiVersion"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header

    # Iterate through automation rules
    foreach ($rule in $response.value) {
        $totalControlsTemp++
        $ruleName = $rule.properties
        $triggeringLogic = $rule.properties.triggeringLogic
        $isEnabled = $triggeringLogic.isEnabled
        $triggersOn = $triggeringLogic.triggersOn
        $conditions = $triggeringLogic.conditions

        $incidentTitle = $false
        $incidentProvider = $false

        if ($isEnabled -and $triggersOn -eq "Incidents" -and $conditions) {
            foreach ($condition in $conditions) {
                if (
                    $condition.conditionType -eq "Property" -and
                    $condition.conditionProperties.propertyName -eq "IncidentTitle"
                ) { $incidentTitle = $true }
                if (
                    $condition.conditionType -eq "Property" -and
                    $condition.conditionProperties.propertyName -eq "IncidentProviderName"
                ) { $incidentProvider = $true }

                if ($incidentTitle -and $incidentProvider) {
                    break
                }
            }
        }

        $ruleName = $($rule.properties.displayName)
        if ($incidentTitle) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Change the trigger condition in the automation rule $ruleName from `"Incident Title`" to `"Analytics Rule Name`""
            if ($reportRequested) {
                $HtmlBuilder.AddWarningMessage("Change the trigger condition in the automation rule <em>$ruleName</em> from <code>Incident Title</code> to <code>Analytics Rule Name</code>")
            }
        }
        if ($incidentProvider) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Change the trigger condition in the automation rule $ruleName from `"Incident Provider`" to `"Alert Product Name`""
            if ($reportRequested) {
                $HtmlBuilder.AddWarningMessage("Change the trigger condition in the automation rule <em>$ruleName</em> from <code>Incident Provider</code> to <code>Alert Product Name</code>")
            }
        }
        if (!$incidentProvider -and !$incidentTitle) {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The automation rule $ruleName is configured correctly"
            $passedControlsTemp++
            if ($reportRequested) {
                $HtmlBuilder.AddOkMessage("The automation rule <em>$ruleName</em> is configured correctly")
            }
        }
    }

    return $totalControlsTemp, $passedControlsTemp
}

function Get-AnalyticsCustomDetectionAnalysis {
    param (
        [Parameter(Mandatory = $false)]
        $HtmlBuilder
    )

    $apiVersion = "2025-07-01-preview"
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/alertRules?api-version=$apiVersion"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header
    foreach ($rule in $response.value) {
        if ($rule.properties.displayName -eq "Advanced Multistage Attack Detection") {
            continue
        }

        ### ENTITY MAPPING ANALYSIS
        Write-Host "RULE: $($rule.properties.displayName)"
        if ($reportRequested) {
            $HtmlBuilder.AddParagraph("<strong>Rule <em>$($rule.properties.displayName)</em></strong>")
            $HtmlBuilder.StartList()
        }
        Write-Host ""
        Write-Host "- Entity Mapping Analysis"
        if ($reportRequested) {
            $HtmlBuilder.AddListItem("<strong>Entity Mapping Analysis</strong>")
        }
        if ($rule.properties.entityMappings) {
            foreach ($mapping in $rule.properties.entityMappings) {
                if ($mapping.fieldMappings.Length -gt 1) {
                    Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " You can associate only one of the $($mapping.fieldMappings.Length) mapped fields for the $($mapping.entityType) entity"
                    if ($reportRequested) {
                        $HtmlBuilder.AddListItem("<span class='warning'>[WARNING]</span> You can associate only one of the <em>$($mapping.fieldMappings.Length)</em> mapped fields for the <em>$($mapping.entityType) entity</em>")
                    }
                }
                else {
                    Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host "You can migrate the mapping for the $($mapping.entityType) entity"
                    if ($reportRequested) {
                        $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> You can migrate the mapping for the <em>$($mapping.entityType) entity</em>")
                    }
                }
            }
        }
        else {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " No entity mapping defined"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> No entity mapping defined")
            }
        }

        ### ALERT DETAILS OVERRIDE ANALYSIS
        Write-Host "- Alert Details Override Analysis"
        if ($reportRequested) {
            $HtmlBuilder.AddListItem("<strong>Alert Details Override Analysis</strong>")
        }
        if ($rule.properties.alertDetailsOverride) {
            $rule.properties.alertDetailsOverride | Get-Member -MemberType NoteProperty | ForEach-Object {
                if ($_.Name -eq "alertDisplayNameFormat") {
                    Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " Alert display name override defined. Custom Detection Rules supports it"
                    if ($reportRequested) {
                        $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> Alert display name override defined. Custom Detection Rules supports it")
                    }
                }
            }
            if ($_.Name -eq "alertDescriptionFormat") {
                Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " Alert description override defined. Custom Detection Rules supports it"
                if ($reportRequested) {
                    $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> Alert description override defined. Custom Detection Rules supports it")
                }
            }
            if ($_.Name -ne "alertDescriptionFormat" -and $_.Name -ne "alertDisplayNameFormat") {
                Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Found an unsupported details override property - Custom Detection Rules doesn't support it"
                if ($reportRequested) {
                    $HtmlBuilder.AddListItem("<span class='warning'>[WARNING]</span> Found an unsupported details override property - Custom Detection Rules doesn't support it")
                }
            }
        }
        else {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " No alert details override defined"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> No alert details override defined")
            }
        }

        ### INCIDENT RE-OPENING ANALYSIS
        Write-Host "- Incident Re-Opening Analysis"
        if ($reportRequested) {
            $HtmlBuilder.AddListItem("<strong>Incident Re-Opening Analysis</strong>")
        }
        if ($rule.properties.incidentConfiguration.groupingConfiguration.reopenClosedIncident) {
            Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Incident reopening defined. Custom Detection Rules doesn't support it"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='warning'>[WARNING]</span> Incident reopening defined. Custom Detection Rules doesn't support it")
            }
        }
        else {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " No incident reopening defined"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> No incident reopening defined")
            }
        }

        ### SUPPRESSION ANALYSIS
        Write-Host "- Suppression Analysis"
        if ($reportRequested) {
            $HtmlBuilder.AddListItem("<strong>Suppression Analysis</strong>")
        }
        if ($rule.properties.suppressionEnabled) {
            Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Suppression rule defined. Custom Detection Rules doesn't support it"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='warning'>[WARNING]</span> Suppression rule defined. Custom Detection Rules doesn't support it")
            }
        }
        else {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " No suppression rule defined"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> No suppression rule defined")
            }
        }

        ### THRESHOLD ANALYSIS
        Write-Host "- Threshold Analysis"
        if ($reportRequested) {
            $HtmlBuilder.AddListItem("<strong>Threshold Analysis</strong>")
        }
        Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Trigger threshold defined. Custom Detection Rules doesn't support it"
        if ($reportRequested) {
            $HtmlBuilder.AddListItem("<span class='warning'>[WARNING]</span> Trigger threshold defined. Custom Detection Rules doesn't support it")
        }

        ### LOOKBACK ANALYSIS
        Write-Host "- Lookback Analysis"
        if ($reportRequested) {
            $HtmlBuilder.AddListItem("<strong>Lookback Analysis</strong>")
        }
        $ok = 0
        if ($rule.properties.queryPeriod -eq "PT4H" -and $rule.properties.queryFrequency -eq "PT1H") {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " The scheduled rule is executed every hour and looks back 4 hours - Custom Detection Rules supports it"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> The scheduled rule is executed every hour and looks back 4 hours - Custom Detection Rules supports it")
            }
            $ok = 1
        }
        if ($rule.properties.queryPeriod -eq "PT12H" -or $rule.properties.queryFrequency -eq "PT3H") {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " The scheduled rule is executed every 3 hours and looks back 12 hours - Custom Detection Rules supports it"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> The scheduled rule is executed every 3 hours and looks back 12 hours - Custom Detection Rules supports it")
            }
            $ok = 1
        }
        if ($rule.properties.queryPeriod -eq "P2D" -or $rule.properties.queryFrequency -eq "PT12H") {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " The scheduled rule is executed every 12 hours and looks back 2 days - Custom Detection Rules supports it"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='ok'>[OK]</span> The scheduled rule is executed every 12 hours and looks back 2 days - Custom Detection Rules supports it")
            }
            $ok = 1
        }
        if ($ok -eq 0) {
            Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " The scheduled rule is executed with a frequency or lookback not supported by Custom Detection Rules by default. `n `t    If the rules uses only Sentinel data you can select a custom frequency in the Custom Detection Rule."
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='warning'>[WARNING]</span> The scheduled rule is executed with a frequency or lookback not supported by Custom Detection Rules by default. If the rules uses only Sentinel data you can select a custom frequency in the Custom Detection Rule.")
            }
        }
        ### NRT ANALYSIS
        if ($rule.kind -eq "NRT") {
            Write-Host "- NRT rules Analysis"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<strong>NRT Rules Analysis</strong>")
            }
            Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " If the rule uses only Defender data and target one single table, you can consider to migrate it to a Custom Detection Rule in Defender"
            if ($reportRequested) {
                $HtmlBuilder.AddListItem("<span class='warning'>[WARNING]</span> If the rule uses only Defender data and target one single table, you can consider to migrate it to a Custom Detection Rule in Defender")
            }
        }

        if ($reportRequested) {
            $HtmlBuilder.EndList()
        }

        Write-Host " "
    }
}

function Add-IntroToReport {
    param (
        [Parameter(Mandatory = $true)]
        [HtmlReportBuilder]$HtmlBuilder,
        [Parameter(Mandatory = $true)]
        [array]$environments
    )

    $HtmlBuilder.AddHeading1("Defender Adoption Helper Overview")
    $HtmlBuilder.AddParagraph("This report describes the current situation to adopt Sentinel in Defender in terms of Table Retention, Analytics Rules and Automations Rules. The report analyses Sentinel environments, <strong>considering them all good candidates to be Primary Workspaces. The choice depends on your needs.</strong>")

    $HtmlBuilder.AddParagraph("<strong>Sentinel environments in scope:</strong>")
    $HtmlBuilder.StartList()
    foreach ($env in $environments) {
        $HtmlBuilder.AddListItem("Workspace name: <strong>$($env.workspaceName)</strong><br>Resource group name: <strong>$($env.resourceGroupName)</strong><br>Subscription id: <strong>$($env.subscriptionId)</strong>")
    }
    $HtmlBuilder.EndList()

    $HtmlBuilder.AddInfoBox("<strong>Defender XDR data</strong><br>You can query and <strong>correlate your Defender XDR logs</strong> (30 days of default retention) <strong>with third-party logs from Microsoft Sentinel without ingesting the Microsoft Defender XDR logs into Microsoft Sentinel.</strong> If you have detection use cases that involve both Defender XDR and Microsoft Sentinel data, where you don't need to retain Defender XDR data for more than 30 days, Microsoft recommends creating custom detection rules that query data from both Microsoft Sentinel and Defender XDR tables.")

    $HtmlBuilder.AddInfoBox("<strong>Analytics Rules</strong><br><strong>Fusion rules will be automatically disabled after Microsoft Sentinel is onboarded to Defender.</strong> However, you will not lose the alert correlation functionality. The alert correlation functionality previously managed by Fusion will now be handled by the Defender XDR engine, which consolidates all signals in one place. While the engines are different, they serve the same purpose.<br><br>If you have Microsoft Sentinel analytics rules configured to trigger alerts only, with incident creation turned off, these <strong>alerts aren't visible in the Defender portal.</strong> You can use the <code>SecurityAlerts</code> table to have visibility about them.")

    $HtmlBuilder.AddInfoBox("<strong>Automation Rules</strong><br>The Defender portal uses a unique engine to correlate incidents and alerts. When onboarding your workspace to the Defender portal, <strong>existing incident names might be changed if the correlation is applied.</strong> For this reason, change the trigger condition from <code>Incident Title</code> to <code>Analytics Rule Name</code>. Also the <code>Incident provider condition</code> property is removed, as all incidents have Microsoft XDR as the incident provider (the value in the <code>ProviderName</code> field).")

    $HtmlBuilder.AddInfoBox("<strong>Analytics Rules or Custom Detection Rules</strong><br>This section does not contribute to the final score. Its purpose is to analyse the current Analytics Rules and their configuration to understand whether they can be migrated to Custom Detection Rules based on the features in Public Preview/General Availability as of today (September 12, 2025).<br><br>NOTE: <strong>Analytic Rules will continue to work at this time, and that you don't need to migrate them to proceed with integration of Sentinel in Defender.</strong>")

    $date = Get-Date -Format "yyyy-MM-dd"
    $HtmlBuilder.AddParagraph("<strong>Report Generated on date:</strong> $date")
    $HtmlBuilder.AddPageBreak()
}

$reportRequested = $PSBoundParameters.ContainsKey('FileName')

# If no filename provided, generate default with date suffix
if ([string]::IsNullOrWhiteSpace($FileName)) {
    $dateStamp = Get-Date -Format "yyyy-MM-dd"
    $FileName = "sentinel-report_$dateStamp"
    $reportRequested = $true
    Write-Host "No filename specified. Will generate: $FileName.html" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "DEFENDER ADOPTION HELPER (Linux-Compatible)" -ForegroundColor Green
Write-Host "This script assists with Defender and Sentinel adoption by checking table retention, analytics rules, and automation rules of your environments."  -ForegroundColor Green
Write-Host ""

# Check for Azure CLI (better for Linux + device auth)
Write-Host "Checking for Azure CLI..." -ForegroundColor Cyan
$azCliInstalled = Get-Command az -ErrorAction SilentlyContinue
if (-not $azCliInstalled) {
    Write-Host "ERROR: Azure CLI (az) is not installed!" -ForegroundColor Red
    Write-Host "Azure CLI works better on Linux with device authentication." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Install it with:" -ForegroundColor Yellow
    Write-Host "  curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
Write-Host "Azure CLI found." -ForegroundColor Green

# Logout and login fresh
Write-Host "Logging out of any existing Azure CLI sessions..." -ForegroundColor Cyan
az logout 2>$null
Write-Host "Cleared existing sessions." -ForegroundColor Green

# Login with device code
Write-Host ""
Write-Host "Authenticating with Azure..." -ForegroundColor Yellow
Write-Host ""

# Run az login and let it show the device code prompt (don't redirect output)
az login --use-device-code

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Failed to authenticate!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Successfully authenticated!" -ForegroundColor Green

# Function to get access token using Azure CLI
function Get-AzCliAccessToken {
    $tokenJson = az account get-access-token --resource https://management.azure.com/ --query "{accessToken:accessToken}" -o json 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to get access token: $tokenJson"
    }
    $tokenObj = $tokenJson | ConvertFrom-Json
    return $tokenObj.accessToken
}

# Get or select subscription
Write-Host ""
if (-not $SubscriptionId) {
    Write-Host "No subscription specified. Listing available subscriptions..." -ForegroundColor Cyan
    Write-Host ""

    $subsJson = az account list --query "[].{name:name, id:id, isDefault:isDefault}" -o json
    $subscriptions = $subsJson | ConvertFrom-Json

    if ($subscriptions.Count -eq 0) {
        Write-Host "ERROR: No subscriptions found!" -ForegroundColor Red
        exit 1
    }

    Write-Host "Available subscriptions:" -ForegroundColor Yellow
    for ($i = 0; $i -lt $subscriptions.Count; $i++) {
        $sub = $subscriptions[$i]
        $defaultMarker = if ($sub.isDefault) { " (current)" } else { "" }
        Write-Host "  [$i] $($sub.name)$defaultMarker" -ForegroundColor White
        Write-Host "      ID: $($sub.id)" -ForegroundColor Gray
    }

    Write-Host ""
    $selection = Read-Host "Select subscription number (or press Enter for current)"
    Write-Host ""

    if ([string]::IsNullOrWhiteSpace($selection)) {
        $currentSub = $subscriptions | Where-Object { $_.isDefault -eq $true }
        $SubscriptionId = $currentSub.id
        Write-Host "Using current subscription: $($currentSub.name)" -ForegroundColor Green
    }
    else {
        $selectedIndex = [int]$selection
        if ($selectedIndex -lt 0 -or $selectedIndex -ge $subscriptions.Count) {
            Write-Host "ERROR: Invalid selection!" -ForegroundColor Red
            exit 1
        }
        $SubscriptionId = $subscriptions[$selectedIndex].id
        Write-Host "Selected subscription: $($subscriptions[$selectedIndex].name)" -ForegroundColor Green
    }
}
else {
    Write-Host "Using specified subscription: $SubscriptionId" -ForegroundColor Green
}

# Set subscription context
Write-Host "Setting subscription context..." -ForegroundColor Cyan
az account set --subscription $SubscriptionId 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to set subscription context!" -ForegroundColor Red
    exit 1
}
Write-Host "Subscription context set successfully." -ForegroundColor Green

# Discover Sentinel workspaces in the subscription
Write-Host ""
Write-Host "Discovering Microsoft Sentinel workspaces in subscription..." -ForegroundColor Cyan
Write-Host ""

$accessToken = Get-AzCliAccessToken
$header = @{
    Authorization = "Bearer $accessToken"
    ContentType   = "application/json"
}

# Get all Log Analytics workspaces
$workspacesUri = "https://management.azure.com/subscriptions/$SubscriptionId/providers/Microsoft.OperationalInsights/workspaces?api-version=2021-12-01-preview"
$workspacesResponse = Invoke-RestMethod -Uri $workspacesUri -Method Get -Headers $header

$environments = @()

foreach ($workspace in $workspacesResponse.value) {
    # Check if Sentinel is enabled on this workspace by checking for SecurityInsights solution
    $workspaceId = $workspace.id
    $solutionsUri = "https://management.azure.com${workspaceId}/providers/Microsoft.SecurityInsights/onboardingStates/default?api-version=2023-02-01"

    try {
        $sentinelCheck = Invoke-RestMethod -Uri $solutionsUri -Method Get -Headers $header -ErrorAction Stop

        # Extract details from workspace resource ID
        # Format: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspaces/{name}
        if ($workspaceId -match '/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/Microsoft.OperationalInsights/workspaces/([^/]+)') {
            $env = [PSCustomObject]@{
                subscriptionId = $Matches[1]
                resourceGroupName = $Matches[2]
                workspaceName = $Matches[3]
            }
            $environments += $env
            Write-Host "  [FOUND] $($env.workspaceName) in resource group $($env.resourceGroupName)" -ForegroundColor Green
        }
    }
    catch {
        # Sentinel not enabled on this workspace, skip it
        continue
    }
}

if ($environments.Count -eq 0) {
    Write-Host ""
    Write-Host "No Microsoft Sentinel workspaces found in this subscription!" -ForegroundColor Yellow
    Write-Host "Make sure Sentinel is enabled on at least one Log Analytics workspace." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Found $($environments.Count) Sentinel workspace(s) to analyze." -ForegroundColor Green

# Initialize HTML report if requested
$htmlBuilder = $null
if ($reportRequested) {
    $htmlBuilder = [HtmlReportBuilder]::new("Defender Adoption Helper Report")
    Add-IntroToReport -HtmlBuilder $htmlBuilder -environments $environments
}

Write-Host ""
Write-Host ""

foreach ($env in $environments) {
    $subscriptionId = $env.subscriptionId
    $resourceGroupName = $env.resourceGroupName
    $workspaceName = $env.workspaceName

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    write-Host "Analyzing: $workspaceName" -ForegroundColor Cyan
    Write-Host "Resource Group: $resourceGroupName" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    # Get fresh access token
    try {
        $accessToken = Get-AzCliAccessToken
    }
    catch {
        Write-Host "ERROR: Failed to get access token!" -ForegroundColor Red
        Write-Host "Details: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Skipping this workspace..." -ForegroundColor Yellow
        Write-Host ""
        continue
    }

    if ($reportRequested) {
        $htmlBuilder.AddHeading2("$workspaceName environment")
        $htmlBuilder.AddParagraph("This section provides details about the following Sentinel environment:")
        $htmlBuilder.StartList()
        $htmlBuilder.AddListItem("Workspace name: <strong>$workspaceName</strong>")
        $htmlBuilder.AddListItem("Resource Group name: <strong>$resourceGroupName</strong>")
        $htmlBuilder.AddListItem("Subscription ID: <strong>$subscriptionId</strong>")
        $htmlBuilder.EndList()
        $htmlBuilder.AddPageBreak()
    }

    $totalControls = 0
    $totalPassedControls = 0
    $totalControlsTemp = 0
    $passedControlsTemp = 0

    # Set up authorization header with user's access token
    $header = @{
        Authorization = "Bearer $accessToken"
        ContentType   = "application/json"
    }

    $defenderTables = @(
        "DeviceInfo",
        "DeviceNetworkInfo",
        "DeviceProcessEvents",
        "DeviceNetworkEvents",
        "DeviceFileEvents",
        "DeviceRegistryEvents",
        "DeviceLogonEvents",
        "DeviceImageLoadEvents",
        "DeviceEvents",
        "DeviceFileCertificateInfo",
        "EmailEvents",
        "EmailUrlInfo",
        "EmailAttachmentInfo",
        "EmailPostDeliveryEvents",
        "UrlClickEvents",
        "CloudAppEvents",
        "IdentityLogonEvents",
        "IdentityQueryEvents",
        "IdentityDirectoryEvents",
        "AlertInfo",
        "AlertEvidence"
    )

    if ($reportRequested) {
        $htmlBuilder.AddHeading3("Defender data analysis")
    }

    Show-HeaderInShell -Message "DEFENDER DATA ANALYSIS"
    $apiVersion = "2025-02-01"
    $totalControlsTemp, $passedControlsTemp = Get-AnalysisDefenderData -defenderTables $defenderTables -HtmlBuilder $htmlBuilder
    $totalControls = $totalControls + $totalControlsTemp
    $totalPassedControls = $totalPassedControls + $passedControlsTemp

    # Show score for this section
    if ($totalControlsTemp -gt 0) {
        $scorePercent = [math]::Round(($passedControlsTemp / $totalControlsTemp) * 100, 2)
        Write-Host "Defender Data Analysis Score: $passedControlsTemp/$totalControlsTemp ($scorePercent%)" -ForegroundColor Cyan
        if ($reportRequested) {
            $htmlBuilder.AddStatBox("Defender Data Analysis Score: $passedControlsTemp/$totalControlsTemp ($scorePercent%)")
        }
    }
    else {
        Write-Host "Defender Data Analysis Score: No tables found" -ForegroundColor Cyan
        if ($reportRequested) {
            $htmlBuilder.AddStatBox("Defender Data Analysis Score: No tables found")
        }
    }
    Write-Host ""

    $passedControlsTemp = 0
    $totalControlsTemp = 0
    if ($reportRequested) {
        $htmlBuilder.AddHeading3("Analytics Analysis")
    }

    Show-HeaderInShell -Message "ANALYTICS ANALYSIS"
    $totalControlsTemp, $passedControlsTemp = Get-AnalyticsAnalysis -HtmlBuilder $htmlBuilder
    $totalControls = $totalControls + $totalControlsTemp
    $totalPassedControls = $totalPassedControls + $passedControlsTemp

    # Show score for this section
    if ($totalControlsTemp -gt 0) {
        $scorePercent = [math]::Round(($passedControlsTemp / $totalControlsTemp) * 100, 2)
        Write-Host "Analytics Analysis Score: $passedControlsTemp/$totalControlsTemp ($scorePercent%)" -ForegroundColor Cyan
        if ($reportRequested) {
            $htmlBuilder.AddStatBox("Analytics Analysis Score: $passedControlsTemp/$totalControlsTemp ($scorePercent%)")
        }
    }
    else {
        Write-Host "Analytics Analysis Score: No analytics rules found" -ForegroundColor Cyan
        if ($reportRequested) {
            $htmlBuilder.AddStatBox("Analytics Analysis Score: No analytics rules found")
        }
    }
    Write-Host ""

    Show-HeaderInShell -Message "AUTOMATION RULES ANALYSIS"
    $passedControlsTemp = 0
    $totalControlsTemp = 0
    if ($reportRequested) {
        $htmlBuilder.AddPageBreak()
        $htmlBuilder.AddHeading3("Automation Rules Analysis")
    }

    $totalControlsTemp, $passedControlsTemp = Get-AutomationAnalysis -HtmlBuilder $htmlBuilder
    $totalControls = $totalControls + $totalControlsTemp
    $totalPassedControls = $totalPassedControls + $passedControlsTemp
    # Show score for this section
    if ($totalControlsTemp -gt 0) {
        $scorePercent = [math]::Round(($passedControlsTemp / $totalControlsTemp) * 100, 2)
        Write-Host "Automation Rule Analysis Score: $passedControlsTemp/$totalControlsTemp ($scorePercent%)" -ForegroundColor Cyan
        if ($reportRequested) {
            $htmlBuilder.AddStatBox("Automation Rule Analysis Score: $passedControlsTemp/$totalControlsTemp ($scorePercent%)")
        }
    }
    else {
        Write-Host "Automation Rule Analysis Score: No automation rules found" -ForegroundColor Cyan
        if ($reportRequested) {
            $htmlBuilder.AddStatBox("Automation Rule Analysis Score: No automation rules found")
        }
    }
    Write-Host ""

    Show-HeaderInShell -Message "FINAL SCORE"
    Write-Host "Total number of Controls : $totalControls"
    Write-Host "Total number of Passed Controls : $totalPassedControls"
    Write-Host "Total number of Not Passed Controls : $($totalControls - $totalPassedControls)"

    if ($totalControls -gt 0) {
        $scorePercent = [math]::Round(($totalPassedControls / $totalControls) * 100, 2)
        Write-Host "Final Score: $totalPassedControls/$totalControls ($scorePercent%)" -ForegroundColor Cyan
        if ($reportRequested) {
            $htmlBuilder.AddPageBreak()
            $htmlBuilder.AddHeading3("Final Score")
            $htmlBuilder.AddParagraph("<strong>Total number of Controls:</strong> $totalControls")
            $htmlBuilder.AddParagraph("<strong>Total number of Passed Controls:</strong> $totalPassedControls")
            $htmlBuilder.AddParagraph("<strong>Total number of Not Passed Controls:</strong> $($totalControls - $totalPassedControls)")
            $htmlBuilder.AddStatBox("Final Score: $totalPassedControls/$totalControls ($scorePercent%)")

            # Add chart
            $failed = $totalControls - $totalPassedControls
            $htmlBuilder.AddChart("finalScoreChart", $totalPassedControls, $failed)
        }
    }
    else {
        Write-Host "Final Score: No controls found to analyze" -ForegroundColor Yellow
        if ($reportRequested) {
            $htmlBuilder.AddPageBreak()
            $htmlBuilder.AddHeading3("Final Score")
            $htmlBuilder.AddParagraph("<strong>No controls found to analyze.</strong>")
        }
    }

    Write-Host ""
    Write-Host "------------------------"
    Write-Host "APPENDIX - EXCLUDED FROM THE SCORE"
    Write-Host "ANALYTICS RULES or SCHEDULED RULES"
    Write-Host ""
    if ($reportRequested) {
        $htmlBuilder.AddPageBreak()
        $htmlBuilder.AddHeading3("Appendix - Analytics Rules or Scheduled Rules Analysis")
    }
    Get-AnalyticsCustomDetectionAnalysis -HtmlBuilder $htmlBuilder

    Write-Host ""
    Write-Host ""
    Write-Host ""

    if ($reportRequested) {
        $htmlBuilder.AddPageBreak()
    }
}

# Save HTML report
if ($reportRequested) {
    Write-Host "***********************"
    Write-Host "SAVING THE REPORT"
    Write-Host "***********************"

    # Ensure .html extension
    $finalFileName = if ($FileName.ToLower().EndsWith('.html')) { $FileName } else { "$FileName.html" }

    $scriptPath = $PSCommandPath
    if (-not $scriptPath) {
        $scriptDir = Get-Location
    }
    else {
        $scriptDir = Split-Path $scriptPath
    }

    $savePath = Join-Path $scriptDir $finalFileName
    $htmlBuilder.SaveToFile($savePath)

    Write-Host "Report generated: $savePath" -ForegroundColor Green
    Write-Host "Generated on: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
}
