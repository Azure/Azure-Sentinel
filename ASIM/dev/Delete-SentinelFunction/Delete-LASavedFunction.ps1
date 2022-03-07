    <#
        .SYNOPSIS
        Deletes saved searches from Log Analytics workspace

        .DESCRIPTION
        Deletes functions from Log Analytics workspace.
        Takes a list of strings for the function names.

        .PARAMETER FunctionName
        Specifies a comma delimited list of saved function name to be deleted. Accepts wildchars. 

        .PARAMETER WorkspaceName
        Specifies the workspace where functions are saved.

        .PARAMETER ResourceGroup
        Specifies the resource group of workspace.

        
        .PARAMETER Force
        If set the user will not be prompted for approval. Be causious!.

        .PARAMETER Category
        Specifies the category of deleted functions.

        
        .EXAMPLE
        PS> Delete-LASavedFunction DeleteM*, TestFunction* -Subscription "Contoso Production" -Workspace contosoc_ws -ResourceGroup soc_rg

        .LINK
        https://aka.ms/ASimDeleFunctionScript
    #>
[CmdletBinding(PositionalBinding=$false)]
param(
    [Parameter(Mandatory=$true ,HelpMessage="Comma delimited function names to delete.", Position=0 )]
    [SupportsWildcards()]
    [string[]]$FunctionName,

    [Parameter(Mandatory=$true)]
    [string]$WorkspaceName,

    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup,


    [Parameter(Mandatory=$false)]
    [switch]$Force,

    [Parameter(Mandatory=$false)]
    [string]$Category,

    [Parameter(Mandatory=$false)]
    [string]$Subscription
)

Import-Module Az.OperationalInsights

if ((Get-AzContext) -eq $null)
{
   Connect-AzAccount
}

$default_subscription = (Get-AzContext).Subscription.Name
if ($PSBoundParameters.ContainsKey("Subscription") )
{
    $context = $Subscription
    Write-Host "Running on subscription: $context."
}
else
{
    $context = $default_subscription
    Write-Host "Running on default subscription: $context. To run on a different subscription use parameter -Subscription"
}
if ($context -ne $default_subscription){
    $suppress=Set-AzContext -Subscription $context
}

$yestoall=$PSBoundParameters.ContainsKey('Force')
$queries= Get-AzOperationalInsightsSavedSearch -ResourceGroupName $ResourceGroup -WorkspaceName $WorkspaceName

foreach ($query in $queries.Value) {
    $category_matches = (-not $category_set -or $query.Properties.Category -ieq $Category)
    $savedfunctionname = $query.Properties.FunctionAlias
    if ($category_matches -and  (%{$FunctionName | %{$savedfunctionname -like $_}}) -contains $true )  {
       Write-Host "Deleting $savedfunctionname ...`n"
       if ($yestoall -eq $false)       {
           $approved = Read-Host -Prompt "`t Are you sure (default: Skip)? [Y] Yes, [A] Yes to all, [S] Skip, [Q] quit"
           if ($approved -ieq "A")
           {
               $yestoall = $true
           }
        }
        if ($yestoall -or ($approved -ieq "Y"))  {
           Remove-AzOperationalInsightsSavedSearch -WorkspaceName $WorkspaceName -ResourceGroupName $ResourceGroup -SavedSearchId $query.Name  
        }
        elseif ($approved -ieq "Q"){
            break
            }
          
    }
}
if ($context -ne $default_subscription){
    $suppress=Set-AzContext -Subscription $default_subscription
}

