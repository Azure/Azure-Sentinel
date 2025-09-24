[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)]
    [alias("templates", "t")]
    [string]$FilesPath,

    [Parameter(Mandatory = $false)]
    [alias("dest", "d")]
    [string]$OutputFolder,

    [Parameter(Mandatory = $false)]
    [alias("--object", "-o")]
    [switch]$ReturnObject
)

#Region Install Modules
$modulesToInstall = @(
    'powershell-yaml'
)

$modulesToInstall | ForEach-Object {
    if (-not (Get-Module -ListAvailable -All $_)) {
        Write-Output "Module [$_] not found, INSTALLING..."
        Install-Module $_ -Force
        Import-Module $_ -Force
    }
}
#EndRegion Install Modules

#Region HelperFunctions
function ConvertTo-ARM {
    param (
        [Parameter(Mandatory = $true)]
        [object]$Value,

        [Parameter(Mandatory = $true)]
        [object]$Metadata,

        [Parameter(Mandatory = $false)]
        [string]$OutputPath,

        [Parameter(Mandatory = $false)]
        [bool]$ReturnObject

    )

    Write-Debug 'Creating ARM Template'
    $template = [PSCustomObject]@{
        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
        contentVersion = "1.0.0.0"
        metadata       = $metadata
        parameters     = @{
            workspace = [PSCustomObject]@{
                type     = "string"
                metadata = @{
                    description = "The Microsoft Sentinel workspace into which the function will be deployed. Has to be in the selected Resource Group."
                }
            }
        }
        resources      = @(
            [PSCustomObject]@{
                type       = "Microsoft.OperationalInsights/workspaces"
                apiVersion = "2022-10-01"
                name       = "[parameters('Workspace')]"
                location   = "[resourcegroup().location]"
                resources  = @([PSCustomObject]@{
                        type       = "savedSearches"
                        apiVersion = "2020-08-01"
                        name       = $($value.properties.FunctionAlias)
                        dependsOn  = @("[resourceId('Microsoft.OperationalInsights/workspaces', parameters('Workspace'))]")
                        properties = $value.properties
                    }
                )
            }
        )
    }

    if ($returnObject) {
        return $template
    }
    else {
        $template | ConvertTo-Json -Depth 20 | Out-File $OutputPath -ErrorAction Stop
    }
}
#EndRegion HelperFunctions

#Region Fetching Yaml Files
try {
    $yamlFiles = Get-ChildItem -Path $FilesPath -Include "*.yaml", "*.yml" -Recurse
    Write-Debug "Found $($yamlFiles.Count) yaml files"
}
catch {
    Write-Error $_.Exception.Message
    break
}
#EndRegion Fetching Yaml Files

#Region Processing Yaml Files
try {
    if ($null -ne $yamlFiles) {
        foreach ($item in $yamlFiles) {
            try {
                $yamlObject = Get-Content $item.FullName | ConvertFrom-Yaml
                Write-Debug "Processing $($item)"

                # Creating parameters from the parameters in the yaml file
                $null = $yamlObject.ParserParams | ForEach-Object {
                    ($stringParams = "$($stringParams), $($_.Name):$($_.Type)=$($_.Default)")
                }

                $properties = [pscustomobject]@{
                    "properties" = @{
                        etag               = "*"
                        displayName        = $yamlObject.Parser.Title
                        category           = 'ASIM'
                        FunctionAlias      = $yamlObject.ParserName
                        query              = $yamlObject.ParserQuery
                        version            = 1.0
                        functionParameters = $stringParams.replace("string=*", "string='*'").trim(', ')
                    }
                }

                #Clearing the variable for the next iteration
                $stringParams = ''

                $metadata = [PSCustomObject]@{
                    "title"       = $yamlObject.Parser.Title
                    "version"     = [single]$yamlObject.Parser.Version
                    "lastUpdated" = $yamlObject.Parser.lastUpdated
                    "description" = $yamlObject.Description
                }
            }
            catch {
                Write-Error $_.Exception.Message
                break
            }

            if ($OutputFolder) {
                $outputPath = $OutputFolder
            }
            else {
                $outputPath = $item.DirectoryName
            }

            $arguments = @{
                Value        = $properties
                Metadata     = $metadata
                OutputPath   = ('{0}/{1}.json' -f ($($outputPath), $($item.BaseName)))
                ReturnObject = $ReturnObject
            }

            ConvertTo-ARM @arguments
        }
    }
}
catch {
    Write-Error $_.Exception.Message
    break
}
#EndRegion Processing Yaml Files
