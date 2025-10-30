param (
    [parameter(Mandatory = $false)]
    [string]$FilesPath,
    
    [parameter(Mandatory = $false)]
    [string]$logLevel
)

## Make sure any modules we depend on are installed
$modulesToInstall = @(
    'Pester'
    'powershell-yaml'
)

$modulesToInstall | ForEach-Object {
    if (-not (Get-Module -ListAvailable -All $_)) {
        Write-Output "Module [$_] not found, INSTALLING..."
        Install-Module $_ -Force
    }
}

$modulesToInstall | ForEach-Object {
    Write-Output "Importing Module [$_]"
    Import-Module $_ -Force
}

# Import Mitre Att&ck mapping
Write-Output 'Loading Mitre Att&ck framework'
$global:attack = (Get-ChildItem -Path "$($PSScriptRoot)\mitre.csv" -Recurse | Get-Content | ConvertFrom-CSV)

if ($FilesPath -ne '.') {
    Write-Output  "Selected filespath is [$FilesPath]"
    Get-ChildItem "*.tests.ps1" | Copy-Item -Destination $FilesPath -Force
    $global:detectionsPath = $FilesPath
}

$PesterConfig = [PesterConfiguration]@{
    Run         = @{
        Path = "$($PSScriptRoot)"
    }
    Output      = @{
        Verbosity = "$logLevel"
    }
    TestResults = @{
        OutputFormat = 'NuUnitXml'
        OutputPath   = "."
    }
    Should      = @{
        ErrorAction = 'Continue'
    }
}

Invoke-Pester -Configuration $PesterConfig
