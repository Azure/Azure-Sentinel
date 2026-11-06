<#
.SYNOPSIS
    Shared ARM-TTK configuration and result filtering for Sentinel solution packages.

.DESCRIPTION
    Dot-sourced by both the GitHub CI ARM-TTK container (.github/actions/entrypoint.ps1)
    and the local runner (.script/local-validation/run-arm-ttk.ps1) so that both apply
    exactly the same exemptions.

    Exemptions are deliberately narrow:
      - 'IDs Should Be Derived From ResourceIDs': only errors for the exact content
        identifier properties listed in $SentinelArmTtkExemptIdProperties, plus
        *Id keys directly under an analytic rule's customDetails (column names, not
        resource IDs). Any other ID error still fails the test.
      - 'Template Should Not Contain Blanks': ARM-TTK already allows blanks inside a
        classic workbook's properties.serializedData payload. The same allowance is
        extended, through ARM-TTK's own ResourcePropertiesThatCanBeEmpty parameter, to
        the Notebook payload of Defender workbooks (Microsoft.Security/workbooks@<api>
        properties.content). Blanks anywhere else still fail.
#>

$script:SentinelArmTtkIdTestName = 'IDs Should Be Derived From ResourceIDs'

# Content identifiers emitted by Sentinel solution packaging that ARM-TTK mistakes for resource IDs.
$script:SentinelArmTtkExemptIdProperties = @(
    'id',
    'contentProductId',
    'packageId',
    'fromTemplateId',
    'chartId',
    'columnId'
)

function Get-SentinelArmTtkTestParameter {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$TemplateText
    )

    # Passing this parameter replaces ARM-TTK's defaults, so the defaults are repeated here.
    # A Hashtable is required: ARM-TTK looks up resource types case-insensitively by key.
    $blankPaths = @{
        'Microsoft.Web/sites/config'   = 'properties'
        'Microsoft.Insights/workbooks' = 'properties.serializedData'
    }

    # ARM-TTK resolves allowances by the exact resource type string, so register each versioned type.
    $defenderWorkbookTypes = [regex]::Matches(
        $TemplateText,
        '"type"\s*:\s*"(Microsoft\.Security/workbooks@[^"]+)"',
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    foreach ($match in $defenderWorkbookTypes) {
        $blankPaths[$match.Groups[1].Value] = 'properties.content'
    }

    return @{ ResourcePropertiesThatCanBeEmpty = $blankPaths }
}

function Test-SentinelArmTtkExemptIdError {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [AllowNull()]
        $ErrorItem
    )

    if ($null -eq $ErrorItem) {
        return $false
    }

    $target = if ($ErrorItem -is [System.Management.Automation.ErrorRecord]) { $ErrorItem.TargetObject } else { $null }
    $propertyName = $null
    $jsonPath = $null
    if ($null -ne $target) {
        if ($target.PSObject.Properties['PropertyName']) { $propertyName = [string]$target.PropertyName }
        if ($target.PSObject.Properties['JSONPath']) { $jsonPath = [string]$target.JSONPath }
    }

    if (-not $propertyName) {
        $message = if ($ErrorItem -is [System.Management.Automation.ErrorRecord]) { $ErrorItem.Exception.Message } else { "$ErrorItem" }
        if ($message -match '^\s*Property:\s*"([^"]+)"') {
            $propertyName = $Matches[1]
        }
    }

    if (-not $propertyName) {
        return $false
    }

    if ($script:SentinelArmTtkExemptIdProperties -contains $propertyName) {
        return $true
    }

    # customDetails values are KQL column names; only exempt when the structured path proves the location.
    if ($jsonPath -and $propertyName -match 'Id$' -and $jsonPath -match '(^|\.)customDetails\.[^.\[\]]+$') {
        return $true
    }

    return $false
}

function Resolve-SentinelArmTtkMainTemplateResults {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [AllowNull()]
        [object[]]$Results
    )

    $kept = [System.Collections.Generic.List[object]]::new()
    $pass = 0
    $fail = 0
    $exemptedErrors = 0
    $exemptedResults = 0

    foreach ($result in @($Results)) {
        if ($null -eq $result -or -not $result.PSObject.Properties['Name']) {
            continue
        }

        $errors = @($result.Errors | Where-Object { $null -ne $_ })
        if ($result.Name -eq $script:SentinelArmTtkIdTestName -and $errors.Count -gt 0) {
            $remaining = @($errors | Where-Object { -not (Test-SentinelArmTtkExemptIdError -ErrorItem $_) })
            $exemptedErrors += $errors.Count - $remaining.Count

            if ($remaining.Count -eq 0) {
                $exemptedResults++
                $pass++
                continue
            }

            if ($remaining.Count -lt $errors.Count) {
                $result = $result.PSObject.Copy()
                $result.Errors = $remaining
            }
        }

        # ARM-TTK's cumulative Summary counts unfiltered failures; callers report the totals returned here.
        if ($result.PSObject.Properties['Summary'] -and $null -ne $result.Summary) {
            $result = $result.PSObject.Copy()
            $result.Summary = $null
        }

        if ($result.Passed) {
            $pass++
        }
        else {
            $fail++
        }
        $kept.Add($result)
    }

    return [pscustomobject]@{
        Results         = $kept.ToArray()
        Pass            = $pass
        Fail            = $fail
        ExemptedErrors  = $exemptedErrors
        ExemptedResults = $exemptedResults
    }
}
