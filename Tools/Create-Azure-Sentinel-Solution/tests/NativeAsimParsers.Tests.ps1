#Requires -Version 7.0
<#
.SYNOPSIS
Verifies native ASIM and solution parser delivery, including shared-path confinement.
.DESCRIPTION
Run: pwsh -NoProfile -File Tools/Create-Azure-Sentinel-Solution/tests/NativeAsimParsers.Tests.ps1
Exercises the real saved-search generator; only the external catalog HTTP response is replaced.
#>
$ErrorActionPreference = 'Stop'
Import-Module powershell-yaml
. (Join-Path $PSScriptRoot '../common/commonFunctions.ps1')

function Assert-Equal($Actual, $Expected) {
    if (($Actual | ConvertTo-Json -Depth 100 -Compress) -cne
        ($Expected | ConvertTo-Json -Depth 100 -Compress)) {
        throw "Expected: $Expected; actual: $Actual"
    }
}
function Assert-Rejected([scriptblock]$Action) {
    try { & $Action | Out-Null }
    catch { return }
    throw 'Expected an invalid content path to be rejected.'
}
function Invoke-WebRequest { param([string]$Uri) return '{"items":[]}' }

$contentToImport = [pscustomobject]@{
    Name = 'Example'; Author = 'Example'; Version = '3.1.0'; TemplateSpec = $true
}
$global:solutionId = 'example.solution'
$details = returnContentResources '3.1.0'
$query = "datatable(Domain:string)['example.test'] | where not(disabled)"
$parameters = @(
    @{ Name = 'disabled'; Type = 'bool'; Default = 'false' },
    @{ Name = 'domain'; Type = 'string'; Default = '' }
)
$parserMetadata = @{ Title = 'Example DNS parser'; Version = '3.1.0'; LastUpdated = 'Nov 25, 2026' }
$documents = @(
    @{ Parser = $parserMetadata; ParserName = 'vimDnsExample'; ParserQuery = $query;
       ParserParams = $parameters; Description = 'Example DNS events' },
    @{ Function = $parserMetadata; FunctionName = 'vimDnsExample'; FunctionQuery = $query;
       FunctionParams = $parameters; Category = 'ASIM'; Description = 'Example DNS events' }
)
$generated = @()
foreach ($document in $documents) {
    $global:baseMainTemplate = Get-Content -Raw $baseMainTemplatePath | ConvertFrom-Json
    $global:parserCounter = 1
    $global:DependencyCriteria = @()
    $rawData = $document | ConvertTo-Yaml
    generateParserContent 'Parsers/ASimDns/Parsers/vimDnsExample.yaml' $contentToImport $details
    $saved = @($global:baseMainTemplate.resources | Where-Object {
        $_.type -eq 'Microsoft.OperationalInsights/workspaces/savedSearches'
    })
    Assert-Equal $saved.Count 1
    Assert-Equal $saved[0].properties.functionAlias 'vimDnsExample'
    Assert-Equal $saved[0].properties.query $query
    Assert-Equal $saved[0].properties.functionParameters "disabled:bool=false,domain:string=''"
    Assert-Equal $global:baseMainTemplate.variables.parserObject1.parserVersion1 '3.1.0'
    $generated += $saved[0] | ConvertTo-Json -Depth 100 -Compress
}
Assert-Equal $generated[0] $generated[1]

$temporary = Join-Path ([System.IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
$solutionRoot = Join-Path $temporary 'Solutions/Example'
$shared = 'Parsers/ASimDns/Parsers/vimDnsExample.yaml'
$local = 'Parsers/Customer.yaml'
try {
    New-Item -ItemType Directory -Path $solutionRoot -Force | Out-Null
    foreach ($path in @((Join-Path $temporary $shared), (Join-Path $solutionRoot $local))) {
        New-Item -ItemType Directory -Path (Split-Path $path -Parent) -Force | Out-Null
        Set-Content -LiteralPath $path -Value 'parser'
    }
    $resolved = Resolve-SolutionContentPath -SolutionRoot $solutionRoot -SolutionName Example `
        -ContentPath $shared -AllowSharedAsimParser -RequireFile
    Assert-Equal $resolved.FullPath ((Join-Path $temporary $shared).Replace('\', '/'))
    $resolved = Resolve-SolutionContentPath -SolutionRoot $solutionRoot -SolutionName Example `
        -ContentPath $local -AllowSharedAsimParser -RequireFile
    Assert-Equal $resolved.FullPath ((Join-Path $solutionRoot $local).Replace('\', '/'))
    Assert-Rejected { Resolve-SolutionContentPath -SolutionRoot $solutionRoot -SolutionName Example -ContentPath $shared -RequireFile }
    foreach ($invalid in @('../outside.yaml', 'Parsers/ASimDns/Parsers/../../outside.yaml',
                           'Parsers/ASimDns/Parsers//vimDnsExample.yaml', '/etc/passwd', 'https://example.test/parser.yaml')) {
        Assert-Rejected { Resolve-SolutionContentPath -SolutionRoot $solutionRoot -SolutionName Example -ContentPath $invalid -AllowSharedAsimParser -RequireFile }
    }
    $link = Join-Path $temporary 'Parsers/ASimDns/Parsers/vimDnsLink.yaml'
    New-Item -ItemType SymbolicLink -Path $link -Target (Join-Path $solutionRoot $local) | Out-Null
    Assert-Rejected { Resolve-SolutionContentPath -SolutionRoot $solutionRoot -SolutionName Example -ContentPath 'Parsers/ASimDns/Parsers/vimDnsLink.yaml' -AllowSharedAsimParser -RequireFile }
}
finally {
    Remove-Item -LiteralPath $temporary -Recurse -Force
}
Write-Host 'Native ASIM/legacy saved-search delivery parity and shared-path confinement passed.'
