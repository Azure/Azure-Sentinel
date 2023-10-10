
#requires -version 6.2
<#
.SYNOPSIS

This command will generate a CSV file containing all the MS Sentinel solution information
    .DESCRIPTION
        Based on the parameters used, this command will eitehr generate a CSV file containing the information about all the Microsoft Sentinel
        MITRE tactics and techniques being used, or a listing of the rules that use the tactics and techniques
    .PARAMETER WorkspaceName
        Enter the Log Analytics workspace name, this is a required parameter
    .PARAMETER ResourceGroupName
        Enter the Log Analytics workspace name, this is a required parameter
    .PARAMETER FileName
        Enter the file name to use.  Defaults to "mitrerules" and ".csv" will be appended to all FileNames that do not already include it
   
    .NOTES
        AUTHOR= Gary Bushey
        LASTEDIT= 30 Sept 2022
    .EXAMPLE
        Export-AzSentineMITREIncidentsToCSV -WorkspaceName "WorkspaceName" -ResourceGroupName "rgname"
        In this example you will get the file named "mitrerules.csv" generated containing the count of the active rule's MITRE information
    .EXAMPLE
        Export-AzSentineMITREIncidentsToCSV -WorkspaceName "WorkspaceName" -ResourceGroupName "rgname" -FileName "test"
        In this example you will get the file named "test.csv" generated containing  the count of the active rule's MITRE information
#>

[CmdletBinding()]
param (
  ## The name of the workspace.  Required
  [Parameter(Mandatory = $true)]
  [string]$WorkspaceName,

  [Parameter(Mandatory = $true)]
  [string]$ResourceGroupName,

  [string]$FileName = "solutionexport.csv"
)

Add-Type -AssemblyName System.Collections

$outputObject = New-Object system.Data.DataTable
[void]$outputObject.Columns.Add('Index', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('SolutionName', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('SolutionType', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('SolutionDescription', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('ResourceType', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('ResourceName', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('RequiredDataConnectors', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('RequiredDataTypes', [string]::empty.GetType() )


Function Export-AzSentinelSolutionDataToCSV ($WorkspaceName, $ResourceGroupName, $FileName) {
  if (! $FileName.EndsWith(".csv")) {
    $FileName += ".csv"
  }

  #Setup the Authentication header needed for the REST calls
  $context = Get-AzContext
  $userProfile = [Microsoft.Azure.Commands.Common.Authentication.Abstractions.AzureRmProfileProvider]::Instance.Profile
  $profileClient = New-Object -TypeName Microsoft.Azure.Commands.ResourceManager.Common.RMProfileClient -ArgumentList ($userProfile)
  $token = $profileClient.AcquireAccessToken($context.Subscription.TenantId)
  $authHeader = @{
    'Content-Type'  = 'application/json' 
    'Authorization' = 'Bearer ' + $token.AccessToken 
  }
    
  $subscriptionId = (Get-AzContext).Subscription.Id
  $url = "https://management.azure.com/subscriptions/$($SubscriptionId)/resourceGroups/$($ResourceGroupName)/providers/Microsoft.OperationalInsights/workspaces/$($WorkspaceName)/providers/Microsoft.SecurityInsights/contentProductPackages?api-version=2023-04-01-preview"

  $solutions = (Invoke-RestMethod -Method "Get" -Uri $url -Headers $authHeader ).value
  $count = 1
  $total = $solutions.count

  $index = 1


  foreach ($solution in $solutions) {
    Write-Host $count " of " $total ": " $solution.properties.displayName
    $count = $count + 1
    <# if ($count -eq 10)
    {
      break;
    } #>
    $solutionUrl = "https://management.azure.com/subscriptions/$($SubscriptionId)/resourceGroups/$($ResourceGroupName)/providers/Microsoft.OperationalInsights/workspaces/$($WorkspaceName)/providers/Microsoft.SecurityInsights/contentProductPackages/" + $solution.name + "?api-version=2023-04-01-preview"
    $solutionData = (Invoke-RestMethod -Method "Get" -Uri $solutionUrl -Headers $authHeader )
    $requiredDataConnectors = ""
    $requiredDataTypes = "";
    #Solution
    if ($solution.properties.contentKind -eq "Solution") {
      foreach ($resource in $solutionData.properties.packagedContent.resources) {
        if (($null -ne $resource.properties.contentKind) -and ("Solution" -ne $resource.properties.contentKind)) {
          $newRow = $outputObject.NewRow()
          $newRow.Index = $index
          $newRow.SolutionName = $solution.properties.displayName
          $newRow.SolutionType = $solution.properties.contentKind
          $newRow.SolutionDescription = $solution.properties.descriptionHtml
          $newRow.ResourceType = $resource.properties.contentKind
          $newRow.ResourceName = $resource.properties.displayName
          if ($null -ne $resource.properties.mainTemplate.resources.properties.requiredDataConnectors.connectorId) { 
            $requiredDataConnectors = [String]::Join('|', $resource.properties.mainTemplate.resources.properties.requiredDataConnectors.connectorId) 
            $requiredDataTypes = [String]::Join('|', $resource.properties.mainTemplate.resources.properties.requiredDataConnectors.dataTypes) 
          }
          $newRow.RequiredDataConnectors = $requiredDataConnectors
          $newRow.RequiredDataTypes = $requiredDataConnectors
          [void]$outputObject.Rows.Add( $newRow )
          $index++
        }
      }
    }
    #StandAlone
    else {
      $resourceType = $solutionData.properties.packagedContent.resources[0].properties.contentKind
      $resourceName = $solutionData.properties.packagedContent.resources[1].properties.displayName
      $newRow = $outputObject.NewRow()
      $newRow.Index = $index
      $newRow.SolutionName = $solution.properties.displayName
      $newRow.SolutionType = $solution.properties.contentKind
      $newRow.SolutionDescription = $solution.properties.description
      $newRow.ResourceType = $resourceType
      $newRow.ResourceName = $resourceName
      $newRow.RequiredDataConnectors = $requiredDataConnectors
      $newRow.RequiredDataTypes = $requiredDataConnectors
      [void]$outputObject.Rows.Add( $newRow )
      $index++
    }
   
  }

  $outputObject |  Export-Csv -QuoteFields "SolutionName", "SolutionDescription", "ResourceName" -Path $FileName -Append
  $outputObject.Clear()
}



#Execute the code
Export-AzSentinelSolutionDataToCSV $WorkspaceName $ResourceGroupName $FileName 