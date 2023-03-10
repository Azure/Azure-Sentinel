    <#
        .SYNOPSIS
        Deletes saved functions from a Log Analytics workspace. 

        .DESCRIPTION
        This PowerShell script deletes saved functions from a Log Analytics workspace. It supports wildcards and enable batch cleaning the workspace from unneeded functions, especially when deploying a new function ARM tempalte such as those used by Microsoft Sentinel ASIM. 

        .PARAMETER FunctionName
        A comma delimited list of names or wildcard patterns of the function to be delete.  

        .PARAMETER WorkspaceName
        The workspace the functions should be deleted from.

        .PARAMETER ResourceGroup
        The resource group of the workspace.

        
        .PARAMETER Force
        If specified, the user is not prompted for confirmation, enabling using the script as part of an automation  (Optional).

        .PARAMETER Category
        Delete functions only if they belong to this category (Optional). For example, currently all ASIM functions use the category ASIM, which enables ensuring that the script delete only ASIM functions even when using wildcards.

        .PARAMETER Emulate
        If specified, the script will run without actually deleting, enabling you to list the functions about to be deleted first.

        .EXAMPLE
        PS> Delete-SentinelFunction TestFunction -Subscription "Contoso Production" -Workspace contosoc_ws -ResourceGroup soc_rg
        Delete a specific function

        .EXAMPLE
        PS> Delete-SentinelFunction * -Category ASIM -Subscription "Contoso Production" -Workspace contosoc_ws -ResourceGroup soc_rg
        Delete all ASIM functions (note that some older functions may not have this category)

        .EXAMPLE
        PS> Delete-SentinelFunction * -Emulate -Subscription "Contoso Production" -Workspace contosoc_ws -ResourceGroup soc_rg
        List of functions in a workspace

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
        [switch]$Emulate,
    
        [Parameter(Mandatory=$false)]
        [string]$Subscription
    )
    
    Import-Module Az.OperationalInsights
    
    if ((Get-AzContext) -eq $null)
    {
       $supress= Connect-AzAccount
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
    
    $yestoall=$Force
    
    $suppress=Set-AzContext -Subscription $context
    $queries= Get-AzOperationalInsightsSavedSearch -ResourceGroupName $ResourceGroup -WorkspaceName $WorkspaceName
    
    foreach ($query in $queries.Value) {
        $category_matches = (-not $category_set -or $query.Properties.Category -ieq $Category)
        $savedfunctionname = $query.Properties.FunctionAlias
        if ($category_matches -and ($savedfunctionname) -and  (%{$FunctionName | %{$savedfunctionname -like $_}}) -contains $true )  {
           Write-Host "Deleting $savedfunctionname ...`n"
           if ($yestoall -eq $false)       {
               $approved = Read-Host -Prompt "`t Are you sure (default: Skip)? [Y] Yes, [A] Yes to all, [S] Skip, [Q] quit"
               if ($approved -ieq "A")
               {
                   $yestoall = $true
               }
            }
            if ((-not $Emulate) -and ($yestoall -or ($approved -ieq "Y")))  {
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