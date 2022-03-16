<#
.SYNOPSIS
    Convert Microsoft Sentinel YAML rules to JSON ARM format
.DESCRIPTION
    This function converts the Microsoft Sentinel rules published on Microsoft Sentinel GitHub in YAML format to the right ARM JSON format
.EXAMPLE
    ConvertSentinelRuleFrom-Yaml -Path './PathToYamlFolder'
    In This example all the YAML files in the folder will be converted to the right JSON format in the same folder
.EXAMPLE
    ConvertSentinelRuleFrom-Yaml -Path './pathToYAMLFolder' -OutputFolder ./PathToJsonFolder
    In this example all the YAML files in the fodler will be converted to JSON and exported to the OutPutFolder
.EXAMPLE
    ConvertSentinelRuleFrom-Yaml -Path './.tmp/ASimDNS/imDns_DomainEntity_DnsEvents.yaml'
    In this example one specific YAML file will be converted to the right JSON format
.PARAMETER Path
    Specifies the object to be processed.  ou can also pipe the objects to this command.
.OUTPUTS
    Output is the JSON file
.NOTES
    AUTHOR: P.Khabazi
    LASTEDIT: 16-03-2022
#>

function ConvertSentinelRuleFrom-Yaml {
    [CmdletBinding()]
    param (
        # [System.IO.Directory]$Path
        [System.IO.FileInfo] $Path,

        [Parameter(Mandatory = $false)]
        [System.IO.FileInfo]$OutputFolder
    )

    if (Get-Module -ListAvailable -Name powershell-yaml) {
        Write-Verbose "Module already installed"
    }
    else {
        Write-Host "Installing PowerShell-YAML module"
        try {
            Install-Module powershell-yaml -AllowClobber -Force -ErrorAction Stop
            Import-Module powershell-yaml
        }
        catch {
            Write-Error $_.Exception.Message
            break
        }
    }

    if ($OutputFolder) {
        if (Test-Path $OutputFolder) {
            $expPath = (Get-Item $OutputFolder).FullName
        }
        else {
            try {
                $script:expPath = (New-Item -Path $OutputFolder -ItemType Directory -Force).FullName
            }
            catch {
                Write-Error $_.Exception.Message
                break
            }
        }
    }


    <#
        Test if path exists and extract the data from folder or file
    #>
    if ($Path.Extension -in '.yaml', '.yml') {
        Write-Verbose "Singel YAML file selected"
        try {
            $content = Get-Item -Path $Path -ErrorAction Stop
        }
        catch {
            Write-Error $_.Exception.Message
        }
    }
    elseif ($Path.Extension -in '') {
        Write-Verbose "Folder defined"
        try {
            $content = Get-ChildItem -Path $Path -Filter *.yaml -Recurse -ErrorAction Stop
        }
        catch {
            Write-Error $_.Exception.Message
        }
    }
    else {
        Write-Error 'Wrong Path please see example'
    }

    if ($content) {
        Write-Verbose "'$($content.count)' templates found to convert"

        $content | ForEach-Object {
            $template = [PSCustomObject]@{
                '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
                contentVersion = "1.0.0.0"
                Parameters     = @{
                    Workspace = @{
                        type = "string"
                    }
                }
                resources      = @(
                    [PSCustomObject]@{
                        id         = ""
                        name       = ""
                        type       = "Microsoft.OperationalInsights/workspaces/providers/alertRules"
                        kind       = "Scheduled"
                        apiVersion = "2021-03-01-preview"
                        properties = [PSCustomObject]@{}
                    }
                )
            }

            $convert = $_ | Get-Content -Raw | ConvertFrom-Yaml -ErrorAction Stop | Select-Object * -ExcludeProperty relevantTechniques, kind, requiredDataConnectors, version, tags
            $($template.resources).id = "[concat(resourceId('Microsoft.OperationalInsights/workspaces/providers', parameters('workspace'), 'Microsoft.SecurityInsights'),'/alertRules/" + $convert.id + "')]"
            $($template.resources).name = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/" + $convert.id + "')]"
            $($template.resources).properties = ($convert | Select-Object * -ExcludeProperty id)

            if ($null -ne $expPath) {
                $outputFile = $expPath + "/" + $($_.BaseName) + ".json"
            }
            else {

                $outputFile = $($_.DirectoryName) + "/" + $($_.BaseName) + ".json"
            }

            try {
                $template | ConvertTo-Json -Depth 20 | Out-File $outputFile -ErrorAction Stop
            }
            catch {
                Write-Error $_.Exception.Message
            }
        }
    }
    else {
        Write-Error "No YAML templates found"
        break
    }
}
