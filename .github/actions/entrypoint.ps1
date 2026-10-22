
$mainTemplateChanged = (Get-Item env:mainTemplateChanged).value
$createUiChanged = (Get-Item env:createUiChanged).value
$hasFailures = $false

Import-Module '/dist/armttk/arm-ttk/arm-ttk.psd1' 
. (Join-Path $PSScriptRoot 'arm-ttk-sentinel-filters.ps1')
$PackageFolderPath = './dist/Package'

# RUN FOR MAINTEMPLATE.JSON FILE
if ($mainTemplateChanged -eq $true)
{
    Write-Host "Running ARM-TTK on MainTemplate.json file!"
    $mainTemplateText = Get-Content -Raw (Join-Path $PackageFolderPath 'mainTemplate.json')
    $testParameter = Get-SentinelArmTtkTestParameter -TemplateText $mainTemplateText
    $MainTemplateTestResults = Test-AzTemplate -TemplatePath "$PackageFolderPath" -File mainTemplate.json -TestParameter $testParameter
    $resolved = Resolve-SentinelArmTtkMainTemplateResults -Results @($MainTemplateTestResults)

    Write-Output $resolved.Results
    Write-Host "MainTemplate.json ARM-TTK: Pass=$($resolved.Pass) Fail=$($resolved.Fail) ExemptedIdErrors=$($resolved.ExemptedErrors)"

    if ($resolved.Fail -gt 0) {
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
    $CreateUiTestResults = Test-AzTemplate -TemplatePath "$PackageFolderPath" -File CreateUiDefinition.json
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