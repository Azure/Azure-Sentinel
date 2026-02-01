# =============================================
# Defender Adoption Helper Script
#
# This PowerShell script assists with the adoption of Microsoft Defender and Sentinel by:
# - Checking retention settings for key Defender tables in Log Analytics
# - Analyzing analytics rules and Fusion engine status
# - Reviewing automation rules for best practices
#
# The script authenticates using an Entra App Registration and queries the Azure Management API.
#
# Author: [Mario Cuomo]
# Date: [15th September, 2025]
# =============================================

# Script Parameters
param(
    [Parameter(Mandatory = $false)]
    [string]$FileName = $null,
    [Parameter(Mandatory = $true)]
    [string]$EnvironmentsFile = $null,
    [Parameter(Mandatory = $false)]
    [string]$Format = $null
)

# Function to set Writer style
function Set-WriterStyle {
    param(
        [Parameter(Mandatory = $true)]
        $Writer,
        [int]$Color = 0,
        [bool]$Bold = $false,
        [bool]$Italic = $false
    )
    $Writer.Font.Color = $Color
    $Writer.Font.Bold = $Bold
    $Writer.Font.Italic = $Italic
}

# Function to write an header2
function Write-Heading2 {
    param(
        [Parameter(Mandatory = $true)]
        $Writer,
        [Parameter(Mandatory = $true)]
        [string]$HeadingText
    )
    $Writer.Style = 'Heading 2'
    $Writer.Font.Italic = $true
    $Writer.TypeText("$HeadingText ")
    $Writer.Font.Italic = $false
    $Writer.TypeText("environment")
    $Writer.TypeParagraph()
    $Writer.Style = 'Normal'
}

# Function to write an header3
function Write-Heading3 {
    param(
        [Parameter(Mandatory = $true)]
        $Writer,
        [Parameter(Mandatory = $true)]
        [string]$HeadingText
    )
    $Writer.Style = 'Heading 3'
    $Writer.TypeText($HeadingText)
    $Writer.TypeParagraph()
    $Writer.Style = 'Normal'
}

# Function to write statistics
function Write-Statistics {
    param(
        [Parameter(Mandatory = $true)]
        $Writer,
        [Parameter(Mandatory = $true)]
        $passedControlsTemp,
        [Parameter(Mandatory = $true)]
        $totalControlsTemp,
        [Parameter(Mandatory = $true)]
        $scorePercent,
        [Parameter(Mandatory = $true)]
        [string]$scoreText
    )
    Set-WriterStyle -Writer $Writer -Color 0 -Bold $true
    $Writer.TypeText("$scoreText $passedControlsTemp/$totalControlsTemp ($scorePercent%)")
    Set-WriterStyle -Writer $Writer -Bold $false -Color 0
    $Writer.TypeParagraph()
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


# Function to save the report and clean up resources
function Save-ReportAndCleanup {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FileName,
        [Parameter(Mandatory = $true)]
        $Document,
        [Parameter(Mandatory = $true)]
        $WordApplication,
        [Parameter(Mandatory = $false)]
        [string]$Format = $null
    )

    $scriptPath = $MyInvocation.MyCommand.Path
    if (-not $scriptPath) {
        $scriptDir = Get-Location
    }
    else {
        $scriptDir = Split-Path $scriptPath
    }

    # Determine format and extension
    $chosenFormat = if ($Format) { $Format.ToLower() } else { 'pdf' }
    switch ($chosenFormat) {
        'docx' {
            $finalName = if ($FileName.ToLower().EndsWith('.docx')) { $FileName } else { "$FileName.docx" }
            $wdFormat = 16 # wdFormatDocumentDefault
        }
        default {
            $finalName = if ($FileName.ToLower().EndsWith('.pdf')) { $FileName } else { "$FileName.pdf" }
            $wdFormat = 17 # wdFormatPDF
        }
    }
    $savePath = Join-Path $scriptDir $finalName

    try {
        $Document.SaveAs2([string]$savePath, [ref]$wdFormat)
        Write-Host "Report generated on" (Get-Date -Format "yyyy-MM-dd")
    }
    finally {
        $WordApplication.Quit()
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($Document) | Out-Null
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($WordApplication) | Out-Null
        exit
    }
}

function Get-AnalysisDefenderData {
    param (
        [Parameter(Mandatory = $true)]
        $defenderTables,
        [Parameter(Mandatory = $false)]
        $Writer
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
                Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                $Writer.TypeText("[WARNING] ")
                Set-WriterStyle -Writer $Writer -Color 0 -Bold $false
                $Writer.TypeText("The table ")
                Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
                $Writer.TypeText($table)
                Set-WriterStyle -Writer $Writer -Italic $false -Bold $false
                $Writer.Font.Bold = $false
                $Writer.TypeText(" has a retention of $retentionPeriod days - no need to ingest this data in Sentinel")
                $Writer.TypeParagraph()
            }
        }
        else {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The table $table has a retention of $retentionPeriod days - need to be stored in Sentinel for more retention" 
            $passedControlsTemp = $passedControlsTemp + 1
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Color 0 -Bold $false
                $Writer.TypeText(" The table ")
                Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
                $Writer.TypeText($table)
                Set-WriterStyle -Writer $Writer -Italic $false -Bold $false
                $Writer.TypeText(" has a retention of $retentionPeriod days - need to be stored in Sentinel for more retention")
                $Writer.TypeParagraph()
            }
        }
    }
    return $totalControlsTemp, $passedControlsTemp
}

function Get-AnalyticsAnalysis {
    param (
        [Parameter(Mandatory = $false)]
        $Writer
    )

    $totalControlsTemp = 0
    $passedControlsTemp = 0
    
    ## FUSION ENGINE
    $apiVersion = "2025-06-01"
    $uri = "https://management.azure.com/subscriptions/$subscriptionId/resourceGroups/$resourceGroupName/providers/Microsoft.OperationalInsights/workspaces/$workspaceName/providers/Microsoft.SecurityInsights/alertRules/BuiltInFusion?api-version=$apiVersion"
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $header
    $totalControlsTemp++

    if ($response -eq $null) {
        Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The Fusion engine is not enabled"
        $passedControlsTemp++
        if ($reportRequested) {
            Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
            $Writer.TypeText("[OK] ")
            Set-WriterStyle -Writer $Writer -Bold $false -Color 0
            $Writer.TypeText("The Fusion engine is not enabled")
            $Writer.TypeParagraph()
        }
    }
    if ($response.properties.enabled) {
        Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Fusion rules will be automatically disabled after Microsoft Sentinel is onboarded in Defender"
        if ($reportRequested) {
            Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
            $Writer.TypeText("[WARNING] ")
            Set-WriterStyle -Writer $Writer -Bold $false -Color 0
            $Writer.TypeText("Fusion rules will be automatically disabled after Microsoft Sentinel is onboarded in Defender")
            $Writer.TypeParagraph()
        }
    }
    else {
        Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The Fusion engine is not enabled"
        if ($reportRequested) {
            $passedControlsTemp++
            Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
            $Writer.TypeText("[OK] ")
            Set-WriterStyle -Writer $Writer -Bold $false -Color 0
            $Writer.TypeText("The Fusion engine is not enabled")
            $Writer.TypeParagraph()
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
                Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                $Writer.TypeText("[WARNING] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("The rule ")
                Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
                $Writer.TypeText($ruleName)
                Set-WriterStyle -Writer $Writer -Italic $false -Bold $false
                $Writer.TypeText(" doesn't generate incidents. The alerts aren't visible in the Defender portal. They appear in SecurityAlerts table in Advanced Hunting")
                $Writer.TypeParagraph()
            }
        }
        else {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The rule $ruleName is configured correctly"
            $passedControlsTemp++
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("The rule ")
                Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
                $Writer.TypeText($ruleName)
                Set-WriterStyle -Writer $Writer -Italic $false -Bold $false
                $Writer.TypeText(" is configured correctly")
                $Writer.TypeParagraph()
            }
        }
    }

    return $totalControlsTemp, $passedControlsTemp
}

function Get-AutomationAnalysis {
    param (
        [Parameter(Mandatory = $false)]
        $Writer
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
                Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                $Writer.TypeText("[WARNING] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("Change the trigger condition in the automation rule ")
                Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
                $Writer.TypeText($ruleName)
                Set-WriterStyle -Writer $Writer -Bold $false -Italic $false
                $Writer.TypeText(" from ")
                Set-WriterStyle -Writer $Writer -Bold $false -Italic $true
                $Writer.TypeText("Incident Title")
                Set-WriterStyle -Writer $Writer -Bold $false -Italic $false
                $Writer.TypeText(" to ")
                Set-WriterStyle -Writer $Writer -Bold $false -Italic $true
                $Writer.TypeText("Analytics Rule Name")
                Set-WriterStyle -Writer $Writer -Italic $false
                $Writer.TypeParagraph()
            }
        }
        if ($incidentProvider) {
            Write-Host "[WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Change the trigger condition in the automation rule $ruleName from `"Incident Provider`" to `"Alert Product Name`""
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                $Writer.TypeText("[WARNING] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("Change the trigger condition in the automation rule ")
                Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
                $Writer.TypeText($ruleName)
                Set-WriterStyle -Writer $Writer -Italic $false -Bold $false
                $Writer.TypeText(" from ")
                Set-WriterStyle -Writer $Writer -Italic $true
                $Writer.TypeText("Incident Provider")
                Set-WriterStyle -Writer $Writer -Italic $false
                $Writer.TypeText(" to ")
                Set-WriterStyle -Writer $Writer -Italic $true
                $Writer.TypeText("Alert Product Name")
                Set-WriterStyle -Writer $Writer -Italic $false
                $Writer.TypeParagraph()
            }
        }
        if (!$incidentProvider -and !$incidentTitle) {
            Write-Host "[OK]" -ForegroundColor Green -NoNewline; Write-Host " The automation rule $ruleName is configured correctly"
            $passedControlsTemp++
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("The automation rule ")
                Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
                $Writer.TypeText($ruleName)
                Set-WriterStyle -Writer $Writer -Italic $false
                $Writer.Font.Bold = $false
                $Writer.TypeText(" is configured correctly")
                $Writer.TypeParagraph()
            }
        }
    }

    return $totalControlsTemp, $passedControlsTemp
}

function Get-AnalyticsCustomDetectionAnalysis {
    param (
        [Parameter(Mandatory = $false)]
        $Writer
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
            Set-WriterStyle -Writer $Writer -Bold $true
            $Writer.TypeText("Rule ")
            Set-WriterStyle -Writer $Writer -Bold $false
            Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
            $Writer.TypeText($rule.properties.displayName)
            Set-WriterStyle -Writer $Writer -Italic $false -Bold $false
            $Writer.TypeParagraph()
        }
        Write-Host ""
        Write-Host "- Entity Mapping Analysis"
        if ($reportRequested) {
            $Writer.Range.ListFormat.ApplyBulletDefault()
            Set-WriterStyle -Writer $Writer -Bold $true
            $Writer.TypeText("Entity Mapping Analysis")
            Set-WriterStyle -Writer $Writer -Bold $false
            $Writer.TypeText([char]11) # manual line break (Shift+Enter)
        }
        if ($rule.properties.entityMappings) {
            foreach ($mapping in $rule.properties.entityMappings) {
                if ($mapping.fieldMappings.Length -gt 1) {
                    Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " You can associate only one of the $($mapping.fieldMappings.Length) mapped fields for the $($mapping.entityType) entity"
                    if ($reportRequested) {
                        Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                        $Writer.TypeText("[WARNING] ")
                        Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                        $Writer.TypeText("You can associate only one of the ")
                        Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
                        $Writer.TypeText($mapping.fieldMappings.Length)
                        Set-WriterStyle -Writer $Writer -Bold $false -Italic $false
                        $Writer.TypeText(" mapped fields for the ")
                        Set-WriterStyle -Writer $Writer -Bold $false -Italic $true
                        $Writer.TypeText("$($mapping.entityType) entity")
                        Set-WriterStyle -Writer $Writer -Bold $false -Italic $false
                        $Writer.TypeText([char]11)
                    }
                }
                else {
                    Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host "You can migrate the mapping for the $($mapping.entityType) entity"
                    if ($reportRequested) {
                        Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                        $Writer.TypeText("[OK] ")
                        Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                        $Writer.TypeText("You can migrate the mapping for the ")
                        Set-WriterStyle -Writer $Writer -Italic $true -Bold $true
                        $Writer.TypeText("$($mapping.entityType) entity")
                        Set-WriterStyle -Writer $Writer -Bold $false -Italic $false
                        $Writer.TypeText([char]11)
                    }
                }
            }
        }
        else {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " No entity mapping defined"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("No entity mapping defined")
                Set-WriterStyle -Writer $Writer -Bold $false -Italic $false
                $Writer.TypeText([char]11)
            }
        }        
        if ($reportRequested) {
            $Writer.TypeParagraph()
        }
        
        
        

        ### ALERT DETAILS OVERRIDE ANALYSIS
        Write-Host "- Alert Details Override Analysis"
        if ($reportRequested) {
            Set-WriterStyle -Writer $Writer -Bold $true
            $Writer.TypeText("Alert Details Override Analysis")
            Set-WriterStyle -Writer $Writer -Bold $false
            $Writer.TypeText([char]11)
        }
        if ($rule.properties.alertDetailsOverride) {
            $rule.properties.alertDetailsOverride | Get-Member -MemberType NoteProperty | ForEach-Object {
                if ($_.Name -eq "alertDisplayNameFormat") {
                    Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " Alert display name override defined. Custom Detection Rules supports it"
                    if ($reportRequested) {
                        Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                        $Writer.TypeText("[OK] ")
                        Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                        $Writer.TypeText("Alert display name override defined. Custom Detection Rules supports it")
                        $Writer.TypeText([char]11)
                    }
                }
            }
            if ($_.Name -eq "alertDescriptionFormat") {
                Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " Alert description override defined. Custom Detection Rules supports it"
                if ($reportRequested) {
                    Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                    $Writer.TypeText("[OK] ")
                    Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                    $Writer.TypeText("Alert description override defined. Custom Detection Rules supports it")
                    $Writer.TypeText([char]11)
                }
            }
            if ($_.Name -ne "alertDescriptionFormat" -and $_.Name -ne "alertDisplayNameFormat") {
                Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Found an unsupported details override property - Custom Detection Rules doesn't support it"
                if ($reportRequested) {
                    Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                    $Writer.TypeText("[WARNING] ")
                    Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                    $Writer.TypeText("Found an unsupported details override property - Custom Detection Rules doesn't support it")
                    $Writer.TypeText([char]11)
                }
            }
        }
        else {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " No alert details override defined"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("No alert details override defined")
                $Writer.TypeText([char]11)
            }
        }
        if ($reportRequested) {
            $Writer.TypeParagraph()
        }

        ### INCIDENT RE-OPENING ANALYSIS
        Write-Host "- Incident Re-Opening Analysis"
        if ($reportRequested) {
            Set-WriterStyle -Writer $Writer -Bold $true
            $Writer.TypeText("Incident Re-Opening Analysis")
            Set-WriterStyle -Writer $Writer -Bold $false
            $Writer.TypeText([char]11)
        }
        if ($rule.properties.incidentConfiguration.groupingConfiguration.reopenClosedIncident) {
            Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Incident reopening defined. Custom Detection Rules doesn't support it"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                $Writer.TypeText("[WARNING] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("Incident reopening defined. Custom Detection Rules doesn't support it")
                $Writer.TypeText([char]11)
            }
        }
        else {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " No incident reopening defined"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("No incident reopening defined")
                $Writer.TypeText([char]11)
            }
        }
        if ($reportRequested) {
            $Writer.TypeParagraph()
        }

        ### SUPPRESSION ANALYSIS
        Write-Host "- Suppression Analysis"
        if ($reportRequested) {
            Set-WriterStyle -Writer $Writer -Bold $true
            $Writer.TypeText("Suppression Analysis")
            Set-WriterStyle -Writer $Writer -Bold $false
            $Writer.TypeText([char]11)
        }
        if ($rule.properties.suppressionEnabled) {
            Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Suppression rule defined. Custom Detection Rules doesn't support it"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                $Writer.TypeText("[WARNING] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("Suppression rule defined. Custom Detection Rules doesn't support it")
                $Writer.TypeText([char]11)
            }
        }
        else {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " No suppression rule defined"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("No suppression rule defined")
                $Writer.TypeText([char]11)
            }
        }
        if ($reportRequested) {
            $Writer.TypeParagraph()
        }

        ### THRESHOLD ANALYSIS
        Write-Host "- Threshold Analysis"
        if ($reportRequested) {
            Set-WriterStyle -Writer $Writer -Bold $true
            $Writer.TypeText("Threshold Analysis")
            Set-WriterStyle -Writer $Writer -Bold $false
            $Writer.TypeText([char]11)
        }
        Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " Trigger threshold defined. Custom Detection Rules doesn't support it"
        if ($reportRequested) {
            Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
            $Writer.TypeText("[WARNING] ")
            Set-WriterStyle -Writer $Writer -Bold $false -Color 0
            $Writer.TypeText("Trigger threshold defined. Custom Detection Rules doesn't support it")
            $Writer.TypeText([char]11)
        }
        if ($reportRequested) {
            $Writer.TypeParagraph()
        }

        ### LOOKBACK ANALYSIS
        Write-Host "- Lookback Analysis"
        if ($reportRequested) {
            Set-WriterStyle -Writer $Writer -Bold $true
            $Writer.TypeText("Lookback Analysis")
            Set-WriterStyle -Writer $Writer -Bold $false
            $Writer.TypeText([char]11)
        }
        $ok = 0
        if ($rule.properties.queryPeriod -eq "PT4H" -and $rule.properties.queryFrequency -eq "PT1H") {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " The scheduled rule is executed every hour and looks back 4 hours - Custom Detection Rules supports it"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("The scheduled rule is executed every hour and looks back 4 hours - Custom Detection Rules supports it")
                $Writer.TypeText([char]11)
            }
            $ok = 1
        }
        if ($rule.properties.queryPeriod -eq "PT12H" -or $rule.properties.queryFrequency -eq "PT3H") {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " The scheduled rule is executed every 3 hours and looks back 12 hours - Custom Detection Rules supports it"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("The scheduled rule is executed every 3 hours and looks back 12 hours - Custom Detection Rules supports it")
                $Writer.TypeText([char]11)
            }
            $ok = 1
        }
        if ($rule.properties.queryPeriod -eq "P2D" -or $rule.properties.queryFrequency -eq "PT12H") {
            Write-Host "  [OK]" -ForegroundColor Green -NoNewline; Write-Host " The scheduled rule is executed every 12 hours and looks back 2 days - Custom Detection Rules supports it"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 5287936 -Bold $true
                $Writer.TypeText("[OK] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("The scheduled rule is executed every 12 hours and looks back 2 days - Custom Detection Rules supports it")
                $Writer.TypeText([char]11)
            }
            $ok = 1
        }
        if ($ok -eq 0) {
            Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " The scheduled rule is executed with a frequency or lookback not supported by Custom Detection Rules by default. `n `t    If the rules uses only Sentinel data you can select a custom frequency in the Custom Detection Rule."
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                $Writer.TypeText("[WARNING] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("The scheduled rule is executed with a frequency or lookback not supported by Custom Detection Rules by default. If the rules uses only Sentinel data you can select a custom frequency in the Custom Detection Rule.")
                $Writer.TypeText([char]11)
            }
        }
        ### NRT ANALYSIS
        if ($rule.kind -eq "NRT") {
            Write-Host "- NRT rules Analysis"
            if ($reportRequested) {
                $Writer.TypeParagraph()
                Set-WriterStyle -Writer $Writer -Bold $true
                $Writer.TypeText("NRT Rules Analysis")
                Set-WriterStyle -Writer $Writer -Bold $false
                $Writer.TypeText([char]11)
            }
            Write-Host "  [WARNING]" -ForegroundColor DarkYellow -NoNewline; Write-Host " If the rule uses only Defender data and target one single table, you can consider to migrate it to a Custom Detection Rule in Defender"
            if ($reportRequested) {
                Set-WriterStyle -Writer $Writer -Color 255 -Bold $true
                $Writer.TypeText("[WARNING] ")
                Set-WriterStyle -Writer $Writer -Bold $false -Color 0
                $Writer.TypeText("If the rule uses only Defender data and target one single table, you can consider to migrate it to a Custom Detection Rule in Defender")
                $Writer.TypeText([char]11)
            }
        }

        if ($reportRequested) {
            $Writer.TypeParagraph()
        }
        if ($reportRequested) {
            $Writer.Range.ListFormat.RemoveNumbers()    
        }

        Write-Host " "      
    }
    
}

function Add-IntroToReport {
    param (
        [Parameter(Mandatory = $true)]
        [object]$Writer,
        [Parameter(Mandatory = $true)]
        [array]$environments
    )

    $Writer.Style = 'Heading 1'
    $Writer.TypeText("Defender Adoption Helper Overview")
    $Writer.TypeParagraph()
    $Writer.Style = 'Normal'
    $Writer.TypeText("This report describes the current situation to adopt Sentinel in Defender in terms of Table Retention, Analytics Rules and Automations Rules. The report analyses Sentinel environments, ")
    Set-WriterStyle -Writer $Writer -Bold $true
    $Writer.TypeText("considering them all good candidates to be Primary Workspaces. The choice depends on your needs.")
    Set-WriterStyle -Writer $Writer -Bold $false
    $Writer.TypeParagraph()
    $Writer.TypeText("Sentinel environments in scope: ")
    $Writer.TypeParagraph()
    $Writer.Range.ListFormat.ApplyBulletDefault()
    foreach ($env in $environments) {
        $Writer.TypeText("Workspace name: $($env.workspaceName)")
        $Writer.TypeText([char]11) # manual line break (Shift+Enter)
        $Writer.TypeText("Resource group name: $($env.resourceGroupName)")
        $Writer.TypeText([char]11) # manual line break (Shift+Enter)
        $Writer.TypeText("Subscription id: $($env.subscriptionId)")
        $Writer.TypeParagraph() # new bullet for next environment
    }
    $Writer.Range.ListFormat.RemoveNumbers()

    $Writer.Font.Bold = $false

    # Defender XDR data section
    $Writer.Font.Bold = $true
    $Writer.TypeText("Defender XDR data")
    $Writer.Font.Bold = $false
    $Writer.TypeText([char]11) # manual line break (Shift+Enter)
    $Writer.TypeText("You can query and ")
    $Writer.Font.Bold = $true
    $Writer.TypeText("correlate your Defender XDR logs ")
    $Writer.Font.Bold = $false
    $Writer.TypeText("(30 days of default retention)")
    $Writer.Font.Bold = $true
    $Writer.TypeText(" with third-party logs from Microsoft Sentinel without ingesting the Microsoft Defender XDR logs into Microsoft Sentinel.")
    $Writer.Font.Bold = $false
    $Writer.TypeText(" If you have detection use cases that involve both Defender XDR and Microsoft Sentinel data, where you don't need to retain Defender XDR data for more than 30 days, Microsoft recommends creating custom detection rules that query data from both Microsoft Sentinel and Defender XDR tables.")
    $Writer.TypeParagraph()

    # Analytics Rules section
    $Writer.Font.Bold = $true
    $Writer.TypeText("Analytics Rules")
    $Writer.TypeText([char]11) # manual line break (Shift+Enter)
    $Writer.TypeText("Fusion rules will be automatically disabled after Microsoft Sentinel is onboarded to Defender")
    $Writer.Font.Bold = $false
    $Writer.TypeText("However, you will not lose the alert correlation functionality. The alert correlation functionality previously managed by Fusion will now be handled by the Defender XDR engine, which consolidates all signals in one place. While the engines are different, they serve the same purpose.")
    $Writer.TypeParagraph()
    $Writer.TypeText("If you have Microsoft Sentinel analytics rules configured to trigger alerts only, with incident creation turned off, these ")
    $Writer.Font.Bold = $true
    $Writer.TypeText("alerts aren't visible in the Defender portal.")
    $Writer.Font.Bold = $false
    $Writer.TypeText(" You can use the ")
    $Writer.Font.Italic = $true
    $Writer.TypeText("SecurityAlerts")
    $Writer.Font.Italic = $false
    $Writer.TypeText(" table to have visibilty about them.")
    $Writer.TypeParagraph()

    # Automation Rules section
    $Writer.Font.Bold = $true
    $Writer.TypeText("Automation Rules")
    $Writer.Font.Bold = $false
    $Writer.TypeText([char]11) # manual line break (Shift+Enter)
    $Writer.TypeText("The Defender portal uses a unique engine to correlate incidents and alerts. When onboarding your workspace to the Defender portal, ")
    $Writer.Font.Bold = $true
    $Writer.TypeText("existing incident names might be changed if the correlation is applied.")
    $Writer.Font.Bold = $false
    $Writer.TypeText(" For this reason, change the trigger condition from ")
    $Writer.Font.Italic = $true
    $Writer.TypeText("Incident Title")
    $Writer.Font.Italic = $false
    $Writer.TypeText(" to ")
    $Writer.Font.Italic = $true
    $Writer.TypeText("Analytics Rule Name")
    $Writer.Font.Italic = $false
    $Writer.TypeText(". Also the ")
    $Writer.Font.Italic = $true
    $Writer.TypeText("Incident provider condition")
    $Writer.Font.Italic = $false
    $Writer.TypeText(" property is removed, as all incidents have Microsoft XDR as the incident provider (the value in the ")
    $Writer.Font.Italic = $true
    $Writer.TypeText("ProviderName")
    $Writer.Font.Italic = $false
    $Writer.TypeText(" field).")
    $Writer.TypeParagraph()
    
    # Analytics Rules or Custom Detection Rules section
    $Writer.Font.Bold = $true
    $Writer.TypeText("Analytics Rules or Custom Detection Rules")
    $Writer.Font.Bold = $false
    $Writer.TypeText([char]11) # manual line break (Shift+Enter)
    $Writer.TypeText("This section does not contribute to the final score. Its purpose is to analyse the current Analytics Rules and their configuration to understand whether they can be migrated to Custom Detection Rules based on the features in Public Preview/General Availability as of today (September 12, 2025).")
    $Writer.TypeText([char]11) # manual line break (Shift+Enter)
    $Writer.TypeText("NOTE: ")
    $Writer.Font.Bold = $true
    $Writer.TypeText("Analytic Rules will continue to work at this time, and that you don't need to migrate them to proceed with integration of Sentinel in Defender.")
    $Writer.Font.Bold = $false

    $Writer.TypeParagraph()
    $Writer.TypeText("Report Generated on date: ")
    $Writer.Font.Bold = $true
    $date = Get-Date -Format "yyyy-MM-dd"
    $Writer.TypeText($date)
    $Writer.Font.Bold = $false
    $Writer.TypeParagraph()

    $Writer.InsertBreak(7)
}


$reportRequested = $PSBoundParameters.ContainsKey('FileName')

Write-Host "DEFENDER ADOPTION HELPER" -ForegroundColor Green
Write-Host "This script assists with Defender and Sentinel adoption by checking table retention, analytics rules, and automation rules of your environments."  -ForegroundColor Green
Write-Host ""

# Define your Entra App Registration and Sentinel details
$tenantId = "<your-tenant-id>"
$clientId = "<your-client-id>"
$clientSecret = "<your-client-secret>"

# Read environments from JSON file
if ($EnvironmentsFile) {
    $environments = Get-Content $EnvironmentsFile | ConvertFrom-Json
    write-Host "$($environments.Count) environments found in the $EnvironmentsFile file" -ForegroundColor Green
    write-Host "Environments loaded from file:" -ForegroundColor Green
    $environments | ForEach-Object {
        write-Host "   - $($_.workspaceName) in subscription $($_.subscriptionId) and resource group $($_.resourceGroupName)"  -ForegroundColor Green
    }
}
else {
    $environments = @(
        @{
            subscriptionId    = $subscriptionId
            resourceGroupName = $resourceGroupName
            workspaceName     = $workspaceName
        }
    )
}

$resource = "https://management.azure.com/"
$authUrl = "https://login.microsoftonline.com/$tenantId/oauth2/token"

if ($reportRequested) {
    ## create a Word Application instance and add a document
    $WordApplication = New-Object -ComObject Word.Application
    $WordApplication.Visible = $false
    $Document = $WordApplication.Documents.Add()
    $Writer = $WordApplication.Selection

    # Insert Table of Contents at the beginning
    $null = $Writer.HomeKey(6) # Move to start of document (wdStory)
    $Writer.Style = 'Normal'
    $Writer.Font.Bold = $true
    $Writer.TypeText('TABLE OF CONTENTS')
    $Writer.Font.Bold = $false
    $Writer.TypeParagraph()
    $null = $Document.Fields.Add($Writer.Range, -1, 'TOC \o "1-3" \h \z \u', $false)
    $Writer.TypeParagraph()

    # Insert a page break after the TOC
    $Writer.InsertBreak(2) # 2 = wdPageBreak

    Add-IntroToReport -Writer $Writer -environments $environments
}

Write-Host ""
Write-Host ""

foreach ($env in $environments) {
    $subscriptionId = $env.subscriptionId
    $resourceGroupName = $env.resourceGroupName
    $workspaceName = $env.workspaceName
    write-Host "Starting the analysis for $workspaceName (RG: $resourceGroupName) in subscription $subscriptionId" -ForegroundColor Cyan
    if ($reportRequested) {
        Write-Heading2 -Writer $Writer -HeadingText "$workspaceName"
        $Writer.Style = 'Normal'
        $Writer.TypeText("This section provides details about the following Sentinel environment:")
        $Writer.TypeParagraph()
        # Write bullet point list with workspace info
        $Writer.Range.ListFormat.ApplyBulletDefault()
        $Writer.TypeText("Workspace name: ")
        Set-WriterStyle -Writer $Writer -Bold $true
        $Writer.TypeText($workspaceName)
        Set-WriterStyle -Writer $Writer -Bold $false
        $Writer.TypeParagraph()
        $Writer.TypeText("Resource Group name: ")
        Set-WriterStyle -Writer $Writer -Bold $true
        $Writer.TypeText($resourceGroupName)
        Set-WriterStyle -Writer $Writer -Bold $false
        $Writer.TypeParagraph()
        $Writer.TypeText("Subscription ID: ")
        Set-WriterStyle -Writer $Writer -Bold $true
        $Writer.TypeText($subscriptionId)
        Set-WriterStyle -Writer $Writer -Bold $false
        $Writer.TypeParagraph()
        $Writer.Range.ListFormat.RemoveNumbers()
        $Writer.InsertBreak(7)
    }

    $totalControls = 0
    $totalPassedControls = 0
    $totalControlsTemp = 0
    $passedControlsTemp = 0

    # Prepare the body for the token request
    $body = @{
        grant_type    = "client_credentials"
        client_id     = $clientId
        client_secret = $clientSecret
        resource      = $resource
    }

    # Request the token
    $tokenResponse = Invoke-RestMethod -Method Post -Uri $authUrl -Body $body
    $accessToken = $tokenResponse.access_token

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
        Write-Heading3 -Writer $Writer -HeadingText "Defender data analysis"
    }

    Show-HeaderInShell -Message "DEFENDER DATA ANALYSIS"
    $apiVersion = "2025-02-01"
    $totalControlsTemp, $passedControlsTemp = Get-AnalysisDefenderData -defenderTables $defenderTables -Writer $Writer
    $totalControls = $totalControls + $totalControlsTemp
    $totalPassedControls = $totalPassedControls + $passedControlsTemp

    # Show score for this section
    $scorePercent = [math]::Round(($passedControlsTemp / $totalControlsTemp) * 100, 2)
    Write-Host "Defender Data Analysis Score: $passedControlsTemp/$totalControlsTemp ($scorePercent%)" -ForegroundColor Cyan
    if ($reportRequested) {
        Write-Statistics -Writer $Writer -passedControlsTemp $passedControlsTemp -totalControlsTemp $totalControlsTemp -scorePercent $scorePercent -scoreText "Defender Data Analysis Score:"
    }
    Write-Host ""



    $passedControlsTemp = 0
    $totalControlsTemp = 0
    if ($reportRequested) {
        Write-Heading3 -Writer $Writer -HeadingText "Analytics Analysis"
    }

    Show-HeaderInShell -Message "ANALYTICS ANALYSIS"
    $totalControlsTemp, $passedControlsTemp = Get-AnalyticsAnalysis -Writer $Writer
    $totalControls = $totalControls + $totalControlsTemp
    $totalPassedControls = $totalPassedControls + $passedControlsTemp

    # Show score for this section
    $scorePercent = [math]::Round(($passedControlsTemp / $totalControlsTemp) * 100, 2)
    Write-Host "Analytics Analysis Score: $passedControlsTemp/$totalControlsTemp ($scorePercent%)" -ForegroundColor Cyan
    if ($reportRequested) {
        Write-Statistics -Writer $Writer -passedControlsTemp $passedControlsTemp -totalControlsTemp $totalControlsTemp -scorePercent $scorePercent -scoreText "Analytics Analysis Score:"
    }
    Write-Host ""



    Show-HeaderInShell -Message "AUTOMATION RULES ANALYSIS"
    $passedControlsTemp = 0
    $totalControlsTemp = 0
    if ($reportRequested) {
        $Writer.InsertBreak(7) 
        Write-Heading3 -Writer $Writer -HeadingText "Automation Rules Analysis"
    }

    $totalControlsTemp, $passedControlsTemp = Get-AutomationAnalysis -Writer $Writer
    $totalControls = $totalControls + $totalControlsTemp
    $totalPassedControls = $totalPassedControls + $passedControlsTemp
    # Show score for this section
    $scorePercent = [math]::Round(($passedControlsTemp / $totalControlsTemp) * 100, 2)
    Write-Host "Automation Rule Analysis Score: $passedControlsTemp/$totalControlsTemp ($scorePercent%)" -ForegroundColor Cyan
    if ($reportRequested) {
        Write-Statistics -Writer $Writer -passedControlsTemp $passedControlsTemp -totalControlsTemp $totalControlsTemp -scorePercent $scorePercent -scoreText "Automation Rule Analysis Score:"
    }
    Write-Host ""

    Show-HeaderInShell -Message "FINAL SCORE"
    Write-Host "Total number of Controls : $totalControls"
    Write-Host "Total number of Passed Controls : $totalPassedControls"
    Write-Host "Total number of Not Passed Controls : $($totalControls - $totalPassedControls)"
    $scorePercent = [math]::Round(($totalPassedControls / $totalControls) * 100, 2)
    Write-Host "Final Score: $totalPassedControls/$totalControls ($scorePercent%)" -ForegroundColor Cyan
    if ($reportRequested) {
        $Writer.InsertBreak(7) 
        Write-Heading3 -Writer $Writer -HeadingText "Final Score"

        Set-WriterStyle -Writer $Writer -Bold $true
        $Writer.TypeText("Total number of Controls : ")
        Set-WriterStyle -Writer $Writer -Bold $false
        $Writer.TypeText("$totalControls")
        $Writer.TypeParagraph()
        Set-WriterStyle -Writer $Writer -Bold $true
        $Writer.TypeText("Total number of Passed Controls : ")
        Set-WriterStyle -Writer $Writer -Bold $false
        $Writer.TypeText("$totalPassedControls")
        $Writer.TypeParagraph()
        Set-WriterStyle -Writer $Writer -Bold $true
        $Writer.TypeText("Total number of Not Passed Controls : ")
        Set-WriterStyle -Writer $Writer -Bold $false
        $Writer.TypeText("$($totalControls - $totalPassedControls)")
        $Writer.TypeParagraph()
        Set-WriterStyle -Writer $Writer -Bold $true
        $Writer.TypeText("Final Score: ")
        Set-WriterStyle -Writer $Writer -Bold $false
        $Writer.TypeText("$totalPassedControls/$totalControls ($scorePercent%)")
        $Writer.TypeParagraph()

        $excel = New-Object -ComObject Excel.Application
        $excel.Visible = $false
        $workbook = $excel.Workbooks.Add()
        $sheet = $workbook.Sheets.Item(1)

        $sheet.Cells.Item(1, 1).Value2 = "Controls"
        $sheet.Cells.Item(1, 2).Value2 = "Values"
        $sheet.Cells.Item(2, 1).Value2 = "Passed Controls"
        $sheet.Cells.Item(2, 2).Value2 = $totalPassedControls
        $sheet.Cells.Item(3, 1).Value2 = "Not Passed Controls"
        $sheet.Cells.Item(3, 2).Value2 = $totalControls - $totalPassedControls

        $chart = $sheet.Shapes.AddChart2(251, 5, $sheet.Cells.Item(5, 1).Left, $sheet.Cells.Item(5, 1).Top, 400, 300).Chart
        $chart.SetSourceData($sheet.Range("A1:B3"))
        $chart.ChartTitle.Text = "Final Score Distribution"
        $chart.ApplyDataLabels()
        foreach ($point in $chart.SeriesCollection(1).Points()) {
            $point.DataLabel.Font.Color = 0x000000
            $point.DataLabel.Font.Size = 14

        }
        $chart.ChartArea.Format.Line.Visible = 0 
        $chart.SeriesCollection(1).Points(1).Format.Fill.ForeColor.RGB = 0x57BF67  # Dark Green
        $chart.SeriesCollection(1).Points(2).Format.Fill.ForeColor.RGB = 0x000000FF  # Red

        $chart.ChartArea.Copy()

        # Paste chart into Word
        $Writer.TypeParagraph()
        Start-Sleep -Milliseconds 500

        $Writer.Paste()

    }

    Write-Host ""
    Write-Host "------------------------"
    Write-Host "APPENDIX - EXCLUDED FROM THE SCORE"
    Write-Host "ANALYTICS RULES or SCHEDULED RULES"
    Write-Host ""
    if ($reportRequested) {
        $Writer.InsertBreak(7) 
        Write-Heading3 -Writer $Writer -HeadingText "Appendix - Analytics Rules or Scheduled Rules Analysis"
    }
    Get-AnalyticsCustomDetectionAnalysis -Writer $Writer

    
    Write-Host ""
    Write-Host ""
    Write-Host ""

    if ($reportRequested) {
        $Writer.InsertBreak(7)
    }
}
    

##SAVE FILE
if ($reportRequested) {
    Write-Host "***********************"
    Write-Host "SAVING THE REPORT"
    Write-Host "***********************"
    $Document.TablesOfContents.Item(1).Update()
    Save-ReportAndCleanup -FileName $FileName -Document $Document -WordApplication $WordApplication -Format $Format
}