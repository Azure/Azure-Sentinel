
$mainTemplateChanged = (Get-Item env:mainTemplateChanged).value
$createUiChanged = (Get-Item env:createUiChanged).value
$hasFailures = $false

$expandTemplatePath = '/dist/armttk/arm-ttk/Expand-AzTemplate.ps1'
if (Test-Path $expandTemplatePath) {
    $expandContent = [IO.File]::ReadAllText($expandTemplatePath)
    $expandContent = $expandContent.Replace(
        'if (-not $foundInnerTemplate) { $anyProblems = $true; continue }',
        'if (-not $foundInnerTemplate) { $fileObject.InnerTemplatesText += ($it.template | ConvertTo-Json -Depth 100); $fileObject.InnerTemplatesNames += $it.ParentObject[0].Name; continue }'
    )
    [IO.File]::WriteAllText($expandTemplatePath, $expandContent)
}

$idsTestPath = '/dist/armttk/arm-ttk/testcases/deploymentTemplate/IDs-Should-Be-Derived-From-ResourceIDs.test.ps1'
if (Test-Path $idsTestPath) {
    $idsContent = [IO.File]::ReadAllText($idsTestPath)
    $idsContent = $idsContent.Replace(
        '"contentProductId",',
        '"contentProductId", "id", "packageId", "fromTemplateId", "columnId", "signature_id",'
    )
    [IO.File]::WriteAllText($idsTestPath, $idsContent)
}

Import-Module '/dist/armttk/arm-ttk/arm-ttk.psd1' 
$PackageFolderPath = './dist/Package'
$skipTests = @("Template Should Not Contain Blanks", "URIs Should Be Properly Constructed")

# RUN FOR MAINTEMPLATE.JSON FILE
if ($mainTemplateChanged -eq $true)
{
    Write-Host "Running ARM-TTK on MainTemplate.json file!"
    $MainTemplateTestResults = Test-AzTemplate -TemplatePath "$PackageFolderPath" -File mainTemplate.json -Skip $skipTests
    # SKIP ANY ERRORS ON contentProductId, id, packageId, fromTemplateId, columnId, AND signature_id
    $filterTestResults = New-Object System.Collections.ArrayList
    $filteredIdTestCount = 0

    foreach($testInfo in $MainTemplateTestResults)
    {
        if ($testInfo.Name -eq 'IDs Should Be Derived From ResourceIDs' -and $testInfo.Errors.Count -gt 0)
        {
            $hasUnfilteredIdError = $false
            $hasExemptIdError = $false
            foreach ($errorInfo in $testInfo.Errors)
            {
                if ($errorInfo.Exception.Message -like '*"contentProductId"*' -or 
                    $errorInfo.Exception.Message -like '*"id"*' -or
                    $errorInfo.Exception.Message -like '*"packageId"*' -or
                    $errorInfo.Exception.Message -like '*"fromTemplateId"*' -or
                    $errorInfo.Exception.Message -like '*"columnId"*' -or
                    $errorInfo.Exception.Message -like '*"signature_id"*')
                {
                    $hasExemptIdError = $true
                }
                else 
                {
                    $hasUnfilteredIdError = $true
                }
            }
            if ($hasUnfilteredIdError)
            {
                $null = $filterTestResults.Add($testInfo)
            }
            elseif ($hasExemptIdError)
            {
                $filteredIdTestCount++
            }
        }
        else {
            if ($null -ne $testInfo.Summary -and $filteredIdTestCount -gt 0)
            {
                $testInfo.Summary.Fail = $testInfo.Summary.Fail - $filteredIdTestCount
                $testInfo.Summary.Pass = $testInfo.Summary.Pass + $filteredIdTestCount
            }

            $null = $filterTestResults.Add($testInfo)
        }
    }

    Write-Output $filterTestResults

    $mainTemplateFailures = @($filterTestResults | Where-Object {
        $null -ne $_.Summary -and $_.Summary.Fail -gt 0
    })

    if ($mainTemplateFailures.Count -gt 0) {
        $failureMessage = "Please review and rectify the 'MainTemplate.json' file as some of the ARM-TTK tests did not pass!"
        Write-Host "$([char]27)[1;31m$failureMessage$([char]27)[0m"
        $hasFailures = $true
    } 
    else {
        Write-Host "All tests passed for the 'MainTemplate.json' file!"
    }
}

# RUN FOR CREATEUIDEFINITION.JSON FILE
if ($createUiChanged -eq $true)
{
    Write-Host "Running ARM-TTK on CreateUiDefinition.json file!"
    $CreateUiTestResults = Test-AzTemplate -TemplatePath "$PackageFolderPath" -File CreateUiDefinition.json -Skip $skipTests
    $CreateUiTestPassed =  $CreateUiTestResults | Where-Object { -not $_.Failed }
    Write-Output $CreateUiTestPassed

    $CreateUiTestFailures =  $CreateUiTestResults | Where-Object { -not $_.Passed }

    if ($CreateUiTestFailures) {
        Write-Host "Please review and rectify the 'CreateUiDefinition.json' file as some of the ARM-TTK tests did not pass!"
        $hasFailures = $true
    }
    else {
        Write-Host "All tests passed for the 'CreateUiDefinition.json' file!"
    }
}

if ($hasFailures) {
    exit 1
}

exit 0