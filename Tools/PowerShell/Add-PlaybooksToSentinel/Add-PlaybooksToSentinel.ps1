<#
Add-PlaybooksToSentinel.ps1
Authors: Tom Lilly @tlilly2010 (@TheTomLilly), Rich Lilly @richlilly2004 (@richlilly) - Netrix LLC (https://www.netrixllc.com)
From https://github.com/Azure/Azure-Sentinel/PLACEHOLDER
Last Updated Date: August 18, 2020

This PowerShell script will enumerate a local Github repository clone of https://github.com/Azure/Azure-Sentinel/Playbook, or a cloud repo can be provided (defaults to Azure/Azure-Sentinel) 
ask for a multi-select of the playbooks to import and import them.
At the time of authoring, additional API authorization will have to be completed, but this is being worked on :)

Select your Playbooks, Subscription, Resource Group, Username (for assignment)
NOTE: If there is a non-standard parameter (ie not playbook name or username, you will prompted for that field entry (ie API key, etc))

Profit :)

Reqirements: Local GitHub Repo or URI of online repo, PowerShell Module Az.Resources
RepoUri: Specify Github Repo in format https://github.com/<owner>/<repo>/tree/master/<
RepoDirectory: Specify local cloned repo, ie C:\Github\Azure-Sentinel\Playbooks
Permissions: Contributor on the Resource Group
#>
#Requires -Module Az.Resources

[CmdletBinding(DefaultParameterSetName = "CloudRepo")]
param (
    [Parameter(ParameterSetName = "CloudRepo")]
    [string]
    $repoUri = "https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks",

    [Parameter(ParameterSetName = "LocalRepo")]
    [string]
    $repoDirectory
)

if($PSCmdlet.ParameterSetName -eq "CloudRepo")
{
    $uriArray = $repoUri.Split("/")
    $gitOwner = $uriArray[3]
    $gitRepo = $uriArray[4]
    $gitPath = $uriArray[7]

    $apiUri = "https://api.github.com/repos/$gitOwner/$gitRepo/contents/$gitPath"

    $response = (Invoke-WebRequest $apiUri).Content | ConvertFrom-Json
    $playbooks = $response| Where-Object {$_.Name -notlike "*.*"} | Select-Object Name | Out-GridView -Title "Select Playbooks to Deploy" -PassThru

}
elseif($PSCmdlet.ParameterSetName -eq "LocalRepo")
{
    $playbooks = Get-ChildItem -LiteralPath $repoDirectory |Where-Object {$_.Name -notlike "*.*"} | Select-Object Name | Out-GridView -Title "Select Playbooks to Deploy" -PassThru
}

Connect-AzAccount

$subscription = Get-AzSubscription | Out-GridView -Title "Select Subscription to Deploy Playbooks to" -PassThru
Select-AzSubscription -SubscriptionName $subscription.Name
$rg = Get-AzResourceGroup | Out-GridView -Title "Select Resource Group to Deploy Playbooks to" -PassThru

$userName = Read-Host -Prompt "Enter the Username to use for API connections"
$playbookName = "PLACEHOLDER"

$armTemplateParameters = New-Object System.Collections.Arraylist

Write-Host -ForegroundColor Green "Extracting and consolidating all Playbook Parameters"
foreach($playbook in $playbooks.Name)
{
    if($PSCmdlet.ParameterSetName -eq "CloudRepo")
    {
        $playbookUri = "$apiUri/$playbook"
        $response = (Invoke-WebRequest $playbookUri).Content | ConvertFrom-Json 
        $templates = ($response |Where-Object {$_.download_url -like "*.json"}).download_url
    }
    elseif($PSCmdlet.ParameterSetName -eq "LocalRepo")
    {
        $templates = (Get-ChildItem "$repoDirectory\$($playbook)\*.json" | Select-Object -ExpandProperty VersionInfo).FileName
    }

    foreach($template in $templates)
    {
        if($PSCmdlet.ParameterSetName -eq "CloudRepo")
        {
            $templateObj = Invoke-WebRequest $template | ConvertFrom-Json
        }
        elseif($PSCmdlet.ParameterSetName -eq "LocalRepo")
        {
            $templateObj = Get-Content $template | ConvertFrom-Json
        }
    
        $params = $templateObj.parameters | Get-Member -MemberType NoteProperty | Select-Object Name
        Write-Host "Sentinel Workbook: $($playbook)"
        Write-Host "Parameters: $($params.Name)"

        foreach($param in $params.Name)
        {
            $armTemplateParameters.Add($param) | Out-Null
        }    
    }
}

Write-Host -ForegroundColor Green "Populating values for Playbook Parameters"
$armTemplateParametersUnique = $armTemplateParameters | Select-Object -Unique

foreach($armTemplateParameter in $armTemplateParametersUnique)
{
    try {
        $paramValue = (Get-Variable $armTemplateParameter -ErrorAction Stop).Value
    }
    catch {
        Write-Host -ForegroundColor Red "Unable to find value for parameter $armTemplateParameter"
        $paramValue = Read-Host "Please enter a value for parameter $armTemplateParameter"
        New-Variable -Name $armTemplateParameter -Value $paramValue
    }
}

Write-Host -ForegroundColor Green "Deploying Playbooks"
foreach($playbook in $playbooks.Name)
{
    if($PSCmdlet.ParameterSetName -eq "CloudRepo")
    {
        $playbookUri = "$apiUri/$playbook"
        $response = (Invoke-WebRequest $playbookUri).Content | ConvertFrom-Json 
        $templates = ($response |Where-Object {$_.download_url -like "*.json"}).download_url
    }
    elseif($PSCmdlet.ParameterSetName -eq "LocalRepo")
    {
        $templates = (Get-ChildItem "$repoDirectory\$($playbook)\*.json" | Select-Object -ExpandProperty VersionInfo).FileName
    }

    Set-Variable -Name "PlaybookName" -Value $playbook

    foreach($template in $templates)
    {
        if($PSCmdlet.ParameterSetName -eq "CloudRepo")
        {
            $templateObj = Invoke-WebRequest $template | ConvertFrom-Json
        }
        elseif($PSCmdlet.ParameterSetName -eq "LocalRepo")
        {
            $templateObj = Get-Content $template | ConvertFrom-Json
        }
    
        $params = $templateObj.parameters | Get-Member -MemberType NoteProperty | Select-Object Name
        Write-Host "Sentinel Workbook: $($playbook)"
        Write-Host "Parameters: $($params.Name)"

        $templateParamTable = @{}

        foreach($param in $params.Name)
        {
            $paramValue = (Get-Variable -Name $param).Value
            $templateParamTable.Add($param,$paramValue)
        }
        
        Write-Host -ForegroundColor Yellow "Deploying Playbook $playbook"
        if($PSCmdlet.ParameterSetName -eq "CloudRepo")
        {
            New-AzResourceGroupDeployment -Name "SentinelPlaybook-$($playbook)" -ResourceGroupName $rg.ResourceGroupName -TemplateUri $template -TemplateParameterObject $templateParamTable

        }
        elseif($PSCmdlet.ParameterSetName -eq "LocalRepo")
        {
            New-AzResourceGroupDeployment -Name "SentinelPlaybook-$($playbook)" -ResourceGroupName $rg.ResourceGroupName -TemplateFile $template -TemplateParameterObject $templateParamTable
        }
    }
}