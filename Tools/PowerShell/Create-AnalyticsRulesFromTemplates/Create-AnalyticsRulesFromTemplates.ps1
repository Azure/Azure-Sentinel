<#
    .SYNOPSIS
        This command creates Sentinel Alert Rules from all available alert rule templates for which data connectors are configured.
    .DESCRIPTION
        This command creates Sentinel Alert Rules from all available alert rule templates for which data connectors are configured.
    .PARAMETER WorkSpaceName
        Enter the Log Analytics workspace name (required)
    .PARAMETER ResourceGroupName
        Enter the Resource Group name of Log Analytics workspace (required)
    .NOTES
        AUTHOR: Tobias Kritten
        LASTEDIT: 14 Feb 2021
    .EXAMPLE
        Create-AzSentinelAnalyticsRulesFromTemplates -WorkspaceName "workspacename" -ResourceGroupName "rgname"
        The script will create Azure Sentinel Alert Rules in Workspace "workspacename"      
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $true)]
    [string]$WorkSpaceName,

    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName
    
)

Function Get-AzSentinelAnalyticsRuleTemplates ($workspaceName, $resourceGroupName) {    
    # Configure the authentication header needed for REST calls
    $context = Get-AzContext
    $profile = [Microsoft.Azure.Commands.Common.Authentication.Abstractions.AzureRmProfileProvider]::Instance.Profile
    $profileClient = New-Object -TypeName Microsoft.Azure.Commands.ResourceManager.Common.RMProfileClient -ArgumentList ($profile)
    $token = $profileClient.AcquireAccessToken($context.Subscription.TenantId)
    $SubscriptionId = (Get-AzContext).Subscription.Id
	
	$authHeader = @{
        'Content-Type'  = 'application/json' 
        'Authorization' = 'Bearer ' + $token.AccessToken 
    }
    
    $urlTemplates = "https://management.azure.com/subscriptions/$($subscriptionId)/resourceGroups/$($resourceGroupName)/providers/Microsoft.OperationalInsights/workspaces/$($workspaceName)/providers/Microsoft.SecurityInsights/alertruletemplates?api-version=2019-01-01-preview"
	$urlDataConnectors = "https://management.azure.com/subscriptions/$($subscriptionId)/resourceGroups/$($resourceGroupName)/providers/Microsoft.OperationalInsights/workspaces/$($workspaceName)/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2019-01-01-preview"
	
	Write-Host -ForegroundColor Cyan "Fetching configured Data Connectors"
	$resultDataConnectors = (Invoke-RestMethod -Method "GET" -Uri $urlDataConnectors -Headers $authHeader ).value
	
	Write-Host -ForegroundColor Cyan "Fetching Alert Templates"
	$resultAlertTemplates = (Invoke-RestMethod -Method "GET" -Uri $urlTemplates -Headers $authHeader ).value
		
    foreach ($template in $resultAlertTemplates) {
		# skip if Alert has already been created from this template
		if($template.properties.alertRulesCreatedByTemplateCount -gt 0)
		{
			continue
		}
		
		# add only alerts for configured DataConnectors
		$dcExist = $false
		foreach($requiredDC in $template.properties.requiredDataConnectors)
		{
			foreach($existingDC in $resultDataConnectors)
			{				
				if($requiredDC.connectorId -eq $existingDC.kind)
				{					
					$dcExist = $true
				}
			}
		}
		
		if($dcExist)
		{			
			[void]$alertCreationTemplates.Add($template)
		}		
    }	
}

Function New-AzSentinelAnalyticsRulesFromTemplate ($workspaceName, $resourceGroupName, $templates) {    
    # Configure the authentication header needed for REST calls
    $context = Get-AzContext
    $profile = [Microsoft.Azure.Commands.Common.Authentication.Abstractions.AzureRmProfileProvider]::Instance.Profile
    $profileClient = New-Object -TypeName Microsoft.Azure.Commands.ResourceManager.Common.RMProfileClient -ArgumentList ($profile)
    $token = $profileClient.AcquireAccessToken($context.Subscription.TenantId)
	$SubscriptionId = (Get-AzContext).Subscription.Id
	
    $authHeader = @{
        'Content-Type'  = 'application/json' 
        'Authorization' = 'Bearer ' + $token.AccessToken 
    }
    
    # Iterate through all alert templates
    foreach($template in $templates)
	{
		$body = ""
		#Depending on the type of alert we are creating, the body has different parameters
		switch ($template.kind) {
			"MicrosoftSecurityIncidentCreation" {  
				$body = @{
					"kind"       = "MicrosoftSecurityIncidentCreation"
					"properties" = @{
						"enabled"       = "true"
						"productFilter" = $template.properties.productFilter
						"displayName"   = $template.properties.displayName
					}
				}
			}
			"Scheduled" {
				$body = @{
					"kind"       = "Scheduled"
					"properties" = @{
						"enabled"               = "true"
						"alertRuleTemplateName" = $template.name
						"displayName"           = $template.properties.displayName
						"description"           = $template.properties.description
						"severity"              = $template.properties.severity
						"tactics"               = $template.properties.tactics
						"query"                 = $template.properties.query
						"queryFrequency"        = $template.properties.queryFrequency
						"queryPeriod"           = $template.properties.queryPeriod
						"triggerOperator"       = $template.properties.triggerOperator
						"triggerThreshold"      = $template.properties.triggerThreshold
						"suppressionDuration"   = "PT5H"  #Azure Sentinel requires a value here, although suppression is disabled
						"suppressionEnabled"    = $false
					}
				}
			}
			"MLBehaviorAnalytics" {
				if ($template.properties.status -eq "Available") {
					$body = @{
						"kind"       = "MLBehaviorAnalytics"
						"properties" = @{
							"enabled"               = "true"
							"alertRuleTemplateName" = $template.name
						}
					}
				}
			}
			"Fusion" {
				if ($template.properties.status -eq "Available") {
					$body = @{
						"kind"       = "Fusion"
						"properties" = @{
							"enabled"               = "true"
							"alertRuleTemplateName" = $template.name
						}
					}
				}
			}
			Default { }
		}
		#If we have created the body...
		if ("" -ne $body) {
			#Create the GUId for the alert and create it.
			$guid = (New-Guid).Guid
			#Create the URI we need to create the alert.
			$uri = "https://management.azure.com/subscriptions/$($subscriptionId)/resourceGroups/$($resourceGroupName)/providers/Microsoft.OperationalInsights/workspaces/$($workspaceName)/providers/Microsoft.SecurityInsights/alertRules/$($guid)?api-version=2019-01-01-preview"
			try {
				Write-Host -ForegroundColor Cyan "Attempting to create rule $($template.properties.displayName)"				
				$verdict = Invoke-RestMethod -Uri $uri -Method Put -Headers $authHeader -Body ($body | ConvertTo-Json -EnumsAsStrings)
				Write-Host -ForegroundColor Green "Succeeded" 
			}
			catch {
				#The most likely error is that there is a missing dataset. There is a new
				#addition to the REST API to check for the existance of a dataset but
				#it only checks certain ones.  Hope to modify this to do the check
				#before trying to create the alert.
				$errorReturn = $_
				Write-Error $errorReturn
			}
			#This pauses for 2 second so that we don't overload the workspace.
			Start-Sleep -Seconds 2
		}                   
    }
}

$alertCreationTemplates = [System.Collections.ArrayList]@()

Get-AzSentinelAnalyticsRuleTemplates -workspaceName $workspaceName -resourceGroupName $resourceGroupName
New-AzSentinelAnalyticsRulesFromTemplate -workspaceName $workspaceName -resourceGroupName $resourceGroupName -templates $alertCreationTemplates