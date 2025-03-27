$psVersion = $PSVersionTable.PSVersion.Major

# Define the paths to your PowerShell 5 and PowerShell 7 script folders
$ps5ScriptFolder = ".\ScriptV5"
$ps7ScriptFolder = ".\ScriptV7"



if ($psVersion -lt 7) {
    Write-Output "Running PowerShell 5 script..."
    $scriptPath = Join-Path -Path $ps5ScriptFolder -ChildPath "ConfigAwsConnectorV5.ps1"
} else {
    Write-Output "Running PowerShell 7 script..."
    $scriptPath = Join-Path -Path $ps7ScriptFolder -ChildPath "ConfigAwsConnector.ps1"
}

# Resolve the relative path to an absolute path
$resolvedScriptPath = Resolve-Path -Path $scriptPath

# Run the appropriate script
& $resolvedScriptPath
