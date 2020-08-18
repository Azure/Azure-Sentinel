<#
Add-PlaybooksToSentinel.ps1
Authors: Tom Lilly @tlilly2010 (@TheTomLilly), Rich Lilly @richlilly2004 (@richlilly) - Netrix LLC (https://www.netrixllc.com)
From https://github.com/Azure/Azure-Sentinel/PLACEHOLDER
Last Updated Date: August 18, 2020

This PowerShell script will enumerate a local Github repository clone of https://github.com/Azure/Azure-Sentinel/Playbook, 
ask for a multi-select of the playbooks to import and import them.
At the time of authoring, additional API authorization will have to be completed, but this is being worked on :)

Select your Playbooks, Subscription, LA instance, Resource Group, Sentinel instance, Username (for assignment)
NOTE: If there is a non-standard parameter (ie not playbook name or username, you will prompted for that field entry (ie API key, etc))

Profit :)

Reqirements: Github repo synced locally, PowerShell Module Az.Resources
Directory: Specify local cloned repo, ie C:\Github\Azure-Sentinel\Playbooks
Permissions: Contributor on the Resource Group
#>
#Requires -Module Az.Resources

$repoDirectory = Read-Host -Prompt "Enter the directory containing all playbooks to deploy"
$playbooks = Get-ChildItem -LiteralPath $repoDirectory |Where-Object {$_.Name -notlike "*.*"} | Select-Object Name | Out-GridView -Title "Select Playbooks to Deploy" -PassThru

Connect-AzAccount

$subscription = Get-AzSubscription | Out-GridView -Title "Select Subscription to Deploy Playbooks to" -PassThru
Select-AzSubscription -SubscriptionName $subscription.Name
$rg = Get-AzResourceGroup | Out-GridView -Title "Select Resource Group to Deploy Playbooks to" -PassThru

$workspace = Get-AzResource -ResourceGroupName $rg.ResourceGroupName -ResourceType "Microsoft.OperationalInsights/workspaces" | Out-GridView -Title "Select Sentiel Workspace" -PassThru

$userName = Read-Host -Prompt "Enter the Username to use for Sentinel connections"

foreach($playbook in $playbooks)
{
    $template = "$repoDirectory\$($playbook.Name)\azuredeploy.json"
    $templateObj = Get-Content $template |ConvertFrom-Json
    $params = $templateObj.parameters | Get-Member -MemberType NoteProperty | Select-Object Name
    Write-Host "Sentinel Workbook: $($playbook.Name)"
    Write-Host "Parameters: $($params.Name)"
    $templateParamTable = @{}
    foreach($param in $params.Name)
    {
        switch ($param) {
            UserName {
                $templateParamTable.Add($param, $userName)
            }
            AzureSentinelResourceGroup {
                $templateParamTable.Add($param, $rg.ResourceGroupName)
            }
            AzureSentinelSubscriptionID {
                $templateParamTable.Add($param, $subscription.Id)
            }
            AzureSentinelWorkspaceId {
                $templateParamTable.Add($param, $workspace)
            }
            AzureSentinelWorkspaceName {
                $templateParamTable.Add($param, $workspace.Name)
            }
            AzureSentinelLogAnalyticsWorkspaceName {
                $templateParamTable.Add($param, $workspace.Name)
            }
            AzureSentinelLogAnalyticsWorkspaceResourceGroupName {
                $templateParamTable.Add($param, $rg.ResourceGroupName)
            }
            PlaybookName {
                $templateParamTable.Add($param, $playbook.Name)
            }
            Default {
                Write-Host -ForegroundColor Red "Unrecognized parameter: $param"
                $value = Read-Host "Provide value for parameter $param"
                $templateParamTable.Add($param, $value)
            }
        }
    }

    New-AzResourceGroupDeployment -Name "SentinelPlaybook-$($playbook.Name)" -ResourceGroupName $rg.ResourceGroupName -TemplateFile $template -TemplateParameterObject $templateParamTable
}