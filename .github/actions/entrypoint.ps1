# Import the arm-ttk module we cloned in the dockerfile
Import-Module '/arm-ttk/arm-ttk/arm-ttk.psd1'

Write-Host 'hello'
# Path we cloned the repository into
$TemplatePath = '/home/runner/work/packagingrepo/packagingrepo/mainTemplate.json'

$TestResults = Test-AzTemplate -TemplatePath $TemplatePath
# We only want to return failures
$TestFailures =  $TestResults | Where-Object { -not $_.Passed }

# If files are returning invalid configurations
# Using exit code "1" to let Github actions node the test failed
if ($TestFailures) {
    Write-Host "One or more templates did not pass the selected tests:"
    $TestFailures.file.name | select-object -unique
    Write-Host "Results:"
    Write-Output $TestFailures
    exit 1
} 

# Else, all passes and exit using exit code 0 indicating a success
else {
    Write-Host "All files passed!"
    exit 0
}