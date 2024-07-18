
$mainTemplateChanged = (Get-Item env:mainTemplateChanged).value
$createUiChanged = (Get-Item env:createUiChanged).value

Import-Module '/dist/armttk/arm-ttk/arm-ttk.psd1' 
$PackageFolderPath = './dist/Package'

# RUN FOR MAINTEMPLATE.JSON FILE
if ($mainTemplateChanged -eq $true)
{
    Write-Host "Running ARM-TTK on MainTemplate.json file!"
    $MainTemplateTestResults = Test-AzTemplate -TemplatePath "$PackageFolderPath" -File mainTemplate.json
    # SKIP ANY ERRORS ON contentProductId AND id 
    $filterTestResults = New-Object System.Collections.ArrayList
    $hasContentProductIdError = $false
    foreach($testInfo in $MainTemplateTestResults)
    {
        if ($testInfo.Name -eq 'IDs Should Be Derived From ResourceIDs' -and $testInfo.Errors.Count -gt 0)
        {
            foreach ($errorInfo in $testInfo.Errors)
            {
                if ($errorInfo.Exception.Message -like '*"contentProductId"*' -or 
                $errorInfo.Exception.Message -like '*"id"*')
                {
                    $hasContentProductIdError = $true
                }
                else 
                {
                    $filterTestResults.Add($testInfo)
                }
            }
        }
        else {
            if ($null -ne $testInfo.Summary -and $hasContentProductIdError -eq $true)
            {
                $testInfo.Summary.Fail = $testInfo.Summary.Fail - 1
                $testInfo.Summary.Pass = $testInfo.Summary.Pass + 1
            }

            $filterTestResults.Add($testInfo)
        }
    }

    Write-Output $filterTestResults

    if ($filterTestResults[$filterTestResults.Count - 1].Summary.Fail -gt 0) {
        Write-Host "Please review and rectify the 'MainTemplate.json' file as some of the ARM-TTK tests did not pass!"
        exit 1
    } 
    else {
        Write-Host "All tests passed for the 'MainTemplate.json' file!"
    }
}

# RUN FOR CREATEUIDEFINITION.JSON FILE
if ($createUiChanged -eq $true)
{
    Write-Host "Running ARM-TTK on CreateUiDefinition.json file!"
    $CreateUiTestResults = Test-AzTemplate -TemplatePath "$PackageFolderPath" -File CreateUiDefinition.json
    $CreateUiTestPassed =  $CreateUiTestResults | Where-Object { -not $_.Failed }
    Write-Output $CreateUiTestPassed

    $CreateUiTestFailures =  $CreateUiTestResults | Where-Object { -not $_.Passed }

    if ($CreateUiTestFailures) {
        Write-Host "Please review and rectify the 'CreateUiDefinition.json' file as some of the ARM-TTK tests did not pass!"
        exit 1
    }
    else {
        Write-Host "All tests passed for the 'CreateUiDefinition.json' file!"
    }
}

exit 0