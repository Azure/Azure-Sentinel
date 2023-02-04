
$mainTemplateChanged = (Get-Item env:mainTemplateChanged).value
$createUiChanged = (Get-Item env:createUiChanged).value

Import-Module '/dist/armttk/arm-ttk/arm-ttk.psd1'
$PackageFolderPath = './dist/Package'

# RUN FOR MAINTEMPLATE.JSON FILE
if ($mainTemplateChanged -eq $true)
{
    Write-Host "Running ARM-TTK on MainTemplate.json file!"
    $MainTemplateTestResults = Test-AzTemplate -TemplatePath "$PackageFolderPath" -File mainTemplate.json
    $MainTemplateTestPassed =  $MainTemplateTestResults | Where-Object { -not $_.Failed }
    Write-Output $MainTemplateTestPassed

    $MainTemplateTestFailures =  $MainTemplateTestResults | Where-Object { -not $_.Passed }

    if ($MainTemplateTestFailures) {
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
