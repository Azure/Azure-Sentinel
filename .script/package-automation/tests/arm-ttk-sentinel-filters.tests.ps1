#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Regression tests for .script/package-automation/arm-ttk-sentinel-filters.ps1.

.DESCRIPTION
    Unit cases use synthetic ARM-TTK error records. Integration cases run the real
    ARM-TTK 'IDs Should Be Derived From ResourceIDs' and 'Template Should Not Contain
    Blanks' tests on small generated templates; they need the arm-ttk module from
    -ArmTtkModulePath, an installed module, or the repository's .arm-ttk clone, and are
    reported as SKIPPED otherwise. Exits non-zero when any case fails.

.EXAMPLE
    pwsh -NoProfile -File .script/package-automation/tests/arm-ttk-sentinel-filters.tests.ps1 -ArmTtkModulePath ./.arm-ttk/arm-ttk/arm-ttk.psd1
#>
param(
    [string]$ArmTtkModulePath
)

# ARM-TTK reports findings through Write-Error; 'Stop' would abort instead of collecting them.
$ErrorActionPreference = 'Continue'
. (Join-Path $PSScriptRoot '..' 'arm-ttk-sentinel-filters.ps1')

$script:failures = [System.Collections.Generic.List[string]]::new()
$script:passed = 0

function Assert-True([bool]$Condition, [string]$Name) {
    if ($Condition) {
        $script:passed++
        Write-Host "  PASS  $Name" -ForegroundColor Green
    }
    else {
        $script:failures.Add($Name)
        Write-Host "  FAIL  $Name" -ForegroundColor Red
    }
}

function New-IdError([string]$PropertyName, [string]$JsonPath) {
    $target = [pscustomobject]@{ PropertyName = $PropertyName; JSONPath = $JsonPath }
    $exception = [System.Exception]::new("Property: `"$PropertyName`" must use one of the following expressions for an resourceId property:")
    return [System.Management.Automation.ErrorRecord]::new($exception, 'ResourceId.Should.Contain.Proper.Expression', 'NotSpecified', $target)
}

function New-Result([string]$Name, [object[]]$Errors) {
    $list = @($Errors | Where-Object { $null -ne $_ })
    return [pscustomobject]@{ Name = $Name; Errors = $list; Passed = ($list.Count -eq 0); Summary = $null }
}

$idTest = 'IDs Should Be Derived From ResourceIDs'

Write-Host "Unit: ID error classification"
foreach ($name in 'id', 'contentProductId', 'packageId', 'fromTemplateId', 'chartId', 'columnId') {
    Assert-True (Test-SentinelArmTtkExemptIdError (New-IdError $name "resources[0].properties.$name")) "exempts content identifier '$name'"
}
Assert-True (-not (Test-SentinelArmTtkExemptIdError (New-IdError 'storageAccountId' 'resources[0].properties.storageAccountId'))) 'keeps genuine storageAccountId error'
Assert-True (-not (Test-SentinelArmTtkExemptIdError (New-IdError 'packageIdentifier' 'resources[0].properties.packageIdentifier'))) 'does not prefix-match exempt names'
Assert-True (Test-SentinelArmTtkExemptIdError (New-IdError 'UserId' 'resources[4].properties.mainTemplate.resources[0].properties.customDetails.UserId')) 'exempts customDetails *Id column name'
Assert-True (-not (Test-SentinelArmTtkExemptIdError (New-IdError 'UserId' 'resources[4].properties.UserId'))) 'keeps *Id outside customDetails'
Assert-True (-not (Test-SentinelArmTtkExemptIdError (New-IdError 'UserId' 'resources[4].properties.customDetails.nested.UserId'))) 'keeps *Id nested below a customDetails value'
$messageOnly = [System.Management.Automation.ErrorRecord]::new([System.Exception]::new('Property: "UserId" must use one of ...'), 'x', 'NotSpecified', $null)
Assert-True (-not (Test-SentinelArmTtkExemptIdError $messageOnly)) 'does not exempt customDetails-style names without a structured path'
$messageOnlyPackage = [System.Management.Automation.ErrorRecord]::new([System.Exception]::new('Property: "packageId" must use one of ...'), 'x', 'NotSpecified', $null)
Assert-True (Test-SentinelArmTtkExemptIdError $messageOnlyPackage) 'falls back to the message for exact exempt names'

Write-Host "Unit: result resolution and counting"
$results = @(
    (New-Result $idTest @((New-IdError 'id' 'a.id'), (New-IdError 'packageId' 'a.packageId'))),
    (New-Result $idTest @((New-IdError 'chartId' 'b.chartId'), (New-IdError 'storageAccountId' 'b.storageAccountId'), (New-IdError 'vnetId' 'b.vnetId'))),
    (New-Result 'Template Should Not Contain Blanks' @([System.Exception]::new('Empty property: ""'))),
    (New-Result 'apiVersions Should Be Recent' @())
)
$results[3].Summary = [pscustomobject]@{ Pass = 1; Fail = 3; Total = 4 }
$resolved = Resolve-SentinelArmTtkMainTemplateResults -Results $results
Assert-True ($resolved.Fail -eq 2) 'counts genuine ID failure and other failing test (Fail=2)'
Assert-True ($resolved.Pass -eq 2) 'counts fully exempted ID result and passing test (Pass=2)'
Assert-True ($resolved.ExemptedErrors -eq 3) 'reports each exempted ID error (3)'
Assert-True ($resolved.ExemptedResults -eq 1) 'drops only the fully exempted ID result'
$keptId = @($resolved.Results | Where-Object Name -eq $idTest)
Assert-True ($keptId.Count -eq 1 -and @($keptId[0].Errors).Count -eq 2) 'keeps both genuine ID errors on the mixed result'
Assert-True (@($results[1].Errors).Count -eq 3) 'does not mutate the original ARM-TTK result'
Assert-True (@($resolved.Results | Where-Object { $null -ne $_.Summary }).Count -eq 0) 'removes ARM-TTK cumulative Summary from emitted results'
Assert-True ((Resolve-SentinelArmTtkMainTemplateResults -Results @()).Fail -eq 0) 'handles empty result sets'

Write-Host "Unit: ARM-TTK blank-allowance parameter"
$parameter = Get-SentinelArmTtkTestParameter -TemplateText '{"type": "Microsoft.Security/workbooks@2026-06-01-preview"}, {"type":"Microsoft.Security/workbooks@2027-01-01"}'
$blankPaths = $parameter.ResourcePropertiesThatCanBeEmpty
Assert-True ($blankPaths['Microsoft.Insights/workbooks'] -eq 'properties.serializedData') 'keeps ARM-TTK classic workbook default'
Assert-True ($blankPaths['Microsoft.Web/sites/config'] -eq 'properties') 'keeps ARM-TTK sites/config default'
Assert-True ($blankPaths['Microsoft.Security/workbooks@2026-06-01-preview'] -eq 'properties.content') 'allows blanks only in Defender workbook content (version 1)'
Assert-True ($blankPaths['microsoft.security/workbooks@2027-01-01'] -eq 'properties.content') 'registers each versioned type case-insensitively'
Assert-True ($blankPaths.Count -eq 4) 'adds nothing beyond the Defender workbook payload'

# --------------------------------------------------------------------------
# Integration with the real ARM-TTK module
# --------------------------------------------------------------------------
if (-not $ArmTtkModulePath) {
    $installed = Get-Module -ListAvailable arm-ttk | Select-Object -First 1
    if ($installed) {
        $ArmTtkModulePath = $installed.Path
    }
    else {
        $candidate = Join-Path $PSScriptRoot '..' '..' '..' '.arm-ttk' 'arm-ttk' 'arm-ttk.psd1'
        if (Test-Path $candidate) { $ArmTtkModulePath = $candidate }
    }
}

if (-not $ArmTtkModulePath -or -not (Test-Path $ArmTtkModulePath)) {
    Write-Host "Integration: SKIPPED (arm-ttk module not found; pass -ArmTtkModulePath)" -ForegroundColor Yellow
}
else {
    Import-Module $ArmTtkModulePath -Force
    Write-Host "Integration: real ARM-TTK ($ArmTtkModulePath)"

    function New-FixtureTemplate([string]$PackageExtra = '', [string]$WorkbookPropertiesExtra = '') {
        return @"
{
  "`$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": { "workspace": { "type": "string" } },
  "resources": [
    {
      "type": "Microsoft.OperationalInsights/workspaces/providers/contentPackages",
      "apiVersion": "2023-04-01-preview",
      "name": "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/fixture')]",
      "properties": { "packageId": "azuresentinel.fixture"$PackageExtra }
    },
    {
      "type": "Microsoft.SecurityInsights/AlertRuleTemplates",
      "apiVersion": "2023-02-01-preview",
      "name": "fixture-rule",
      "kind": "Scheduled",
      "properties": { "customDetails": { "UserId": "AccountId" } }
    },
    {
      "type": "Microsoft.Resources/deployments",
      "apiVersion": "2022-09-01",
      "name": "DefenderWorkbook-fixture",
      "properties": {
        "mode": "Incremental",
        "template": {
          "`$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
          "languageVersion": "2.0",
          "contentVersion": "1.0.0.0",
          "imports": { "MicrosoftSecurity": { "provider": "MicrosoftSecurity", "version": "1.0.0" } },
          "resources": {
            "workbook": {
              "import": "MicrosoftSecurity",
              "type": "Microsoft.Security/workbooks@2026-06-01-preview",
              "properties": {
                "id": "c50c74d5-7936-5229-938e-d31653d0eb49",
                "name": "Fixture workbook"$WorkbookPropertiesExtra,
                "content": {
                  "version": "Notebook/1.0",
                  "fromTemplateId": "fixture-template",
                  "items": [ { "type": 10, "content": { "chartId": "workbook-chart-1", "splitBy": null, "min": null, "max": null } } ]
                }
              }
            }
          }
        }
      }
    }
  ]
}
"@
    }

    function Invoke-Fixture([string]$TemplateText) {
        $dir = Join-Path ([System.IO.Path]::GetTempPath()) ("armttk-filter-" + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $dir | Out-Null
        try {
            Set-Content -Path (Join-Path $dir 'mainTemplate.json') -Value $TemplateText -Encoding utf8
            $tests = @('IDs Should Be Derived From ResourceIDs', 'Template Should Not Contain Blanks')
            $raw = @(Test-AzTemplate -TemplatePath $dir -File mainTemplate.json -Test $tests -TestParameter (Get-SentinelArmTtkTestParameter -TemplateText $TemplateText))
            $baseline = @(Test-AzTemplate -TemplatePath $dir -File mainTemplate.json -Test $tests)
            return [pscustomobject]@{
                Resolved     = Resolve-SentinelArmTtkMainTemplateResults -Results $raw
                BaselineFail = @($baseline | Where-Object { -not $_.Passed }).Count
            }
        }
        finally {
            Remove-Item -LiteralPath $dir -Recurse -Force
        }
    }

    function Get-FailingTests($Run) {
        return @($Run.Resolved.Results | Where-Object { -not $_.Passed } | ForEach-Object Name | Sort-Object -Unique)
    }

    $clean = Invoke-Fixture (New-FixtureTemplate)
    Assert-True ($clean.BaselineFail -gt 0) 'baseline ARM-TTK fails the unfiltered Sentinel fixture'
    Assert-True ($clean.Resolved.Fail -eq 0) 'shared filters pass content IDs, customDetails and Defender workbook blanks'
    Assert-True ($clean.Resolved.ExemptedErrors -ge 5) 'exempted the expected content-identifier errors'

    $badId = Invoke-Fixture (New-FixtureTemplate -PackageExtra ', "storageAccountId": "literal-not-a-resource-id"')
    Assert-True ((Get-FailingTests $badId) -contains $idTest) 'genuine literal *Id still fails alongside exempted IDs'
    $keptIdErrors = @($badId.Resolved.Results | Where-Object Name -eq $idTest | ForEach-Object { @($_.Errors) })
    Assert-True ($keptIdErrors.Count -ge 1 -and @($keptIdErrors | Where-Object { Test-SentinelArmTtkExemptIdError $_ }).Count -eq 0) 'reports only the genuine ID errors'

    $blankOutside = Invoke-Fixture (New-FixtureTemplate -PackageExtra ', "description": ""')
    Assert-True ((Get-FailingTests $blankOutside) -contains 'Template Should Not Contain Blanks') 'blank outside workbook payload still fails'

    $blankInWorkbookProps = Invoke-Fixture (New-FixtureTemplate -WorkbookPropertiesExtra ', "description": ""')
    Assert-True ((Get-FailingTests $blankInWorkbookProps) -contains 'Template Should Not Contain Blanks') 'blank in Defender workbook properties outside content still fails'
}

Write-Host ""
Write-Host "Passed: $script:passed  Failed: $($script:failures.Count)"
if ($script:failures.Count -gt 0) {
    $script:failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}
exit 0
