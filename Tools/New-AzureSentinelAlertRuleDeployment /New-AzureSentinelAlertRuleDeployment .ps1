<#
.SYNOPSIS
    Combine JSON template file into one object before deployment
.DESCRIPTION
    This function will combine all the Microsoft Sentinel Alert rule JSON file's from source folder into one PS object before deploying to Azure.
    This way you don't need to loop over each ARM template which is time consuming.
    Result is that we speed up the deployment by creating the rules in parallel through Azure Resource Manager
.EXAMPLE
    New-AzureSentinelAlertRuleDeployment -templatePath "./rules" -resourceGroupName "RG Name" -workspaceName "WorkspaceName"
.NOTES
    AUTHOR: Pouyan Khabazi
    LASTEDIT: 28-03-2022
#>

function New-AzureSentinelAlertRuleDeployment {
    param (
        $templatePath,
        $resourceGroupName,
        $workspaceName
    )
    $template = @{
        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
        contentVersion = "1.0.0.0"
        Parameters     = @{
            Workspace = @{
                type = "string"
            }
        }
        resources      = @()
    }

    Get-ChildItem -Path $templatePath -Filter *.json -Recurse | ForEach-Object {
        $template.resources += ($_ | Get-Content -Raw | ConvertFrom-Json -Depth 20 -AsHashtable | Select-Object resources).resources
    }

    if ($template.resources.count -gt 0) {
        $templateParameterObject = @{
            workspace = $workspaceName
        }
        try {
            $result = New-AzResourceGroupDeployment -ResourceGroupName $resourceGroupName -TemplateObject $template -TemplateParameterObject $templateParameterObject -ErrorAction Stop
            return $result
        }
        catch {
            Write-Error $_.Exception.Message
            break
        }
    }
    else {
        Write-Warning "No Rules found to deploy"
    }
}
