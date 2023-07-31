param(
    [Parameter(Mandatory = $true)][string]$ResourceGroup,
    [Parameter(Mandatory = $true)][string]$Workspace,
    [Parameter(Mandatory = $true)][string]$Region,
    [Parameter(Mandatory = $false)][string[]]$Solutions,
    [Parameter(Mandatory = $false)][string[]]$SeveritiesToInclude = @("Informational", "Low", "Medium", "High")
)

$context = Get-AzContext


if (!$context) {
    Connect-AzAccount
    $context = Get-AzContext
}

$SubscriptionId = $context.Subscription.Id
Write-Host "Connected to Azure with subscription: " + $context.Subscription

# Get a list of all the solutions
$url = "https://catalogapi.azure.com/offers?api-version=2018-08-01-beta&%24filter=categoryIds%2Fany%28cat%3A+cat+eq+%27AzureSentinelSolution%27%29+or+keywords%2Fany%28key%3A+contains%28key%2C%27f1de974b-f438-4719-b423-8bf704ba2aef%27%29%29"
$allSolutions = (Invoke-RestMethod -Method "Get" -Uri $url -Headers $authHeader ).items

#Deploy each single solution
$templateParameter = @{"workspace-location" = $Region; workspace = $Workspace }
foreach ($deploySolution in $Solutions) {
    $singleSolution = $allSolutions | Where-Object  -Property "displayName" -Contains $deploySolution
    if ($null -eq $singleSolution) {
        Write-Error "Unable to get find solution with name $deploySolution" 
    }
    else {
        $templateUri = $singleSolution.plans.artifacts | Where-Object -Property "name" -EQ "DefaultTemplate"
        Write-Host "Deploying solution:  $deploySolution"
        New-AzResourceGroupDeployment -ResourceGroupName $ResourceGroup -TemplateUri $templateUri.uri -TemplateParameterObject $templateParameter
        Write-Host "Deployed solution:  $deploySolution"
    }

}


$baseUri = "/subscriptions/${SubscriptionId}/resourceGroups/${ResourceGroup}/providers/Microsoft.OperationalInsights/workspaces/${Workspace}"
$alertUri = "$baseUri/providers/Microsoft.SecurityInsights/alertRules/"


#####
#create rules from any rule templates that came from solutions
#####

if (($SeveritiesToInclude -eq "None") -or ($null -eq $SeveritiesToInclude)) {
    Exit
}

$solutionURL = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01"
  
#We only care about those rule templates that were created by Microsoft Sentinel solutions so
#this query will make sure to filter out anything else as well as provide some overview data (which is not used)
$query = @"
    Resources 
    | where type =~ 'Microsoft.Resources/templateSpecs/versions' 
    | where tags['hidden-sentinelContentType'] =~ 'AnalyticsRule' 
    and tags['hidden-sentinelWorkspaceId'] =~ '/subscriptions/$($SubscriptionId)/resourceGroups/$($ResourceGroup)/providers/Microsoft.OperationalInsights/workspaces/$($Workspace)' 
    | extend version = name 
    | extend parsed_version = parse_version(version) 
    | extend resources = parse_json(parse_json(parse_json(properties).template).resources) 
    | extend metadata = parse_json(resources[array_length(resources)-1].properties)
    | extend contentId=tostring(metadata.contentId) 
    | summarize arg_max(parsed_version, version, properties) by contentId 
    | project contentId, version, properties
"@

$body = @{
    "subscriptions" = @($SubscriptionId)
    "query"         = $query
}

$azureProfile = [Microsoft.Azure.Commands.Common.Authentication.Abstractions.AzureRmProfileProvider]::Instance.Profile
$profileClient = New-Object -TypeName Microsoft.Azure.Commands.ResourceManager.Common.RMProfileClient -ArgumentList ($azureProfile)
$token = $profileClient.AcquireAccessToken($context.Subscription.TenantId)
$authHeader = @{
    'Content-Type'  = 'application/json'
    'Authorization' = 'Bearer ' + $token.AccessToken
}

#Load all the rule templates from solutions
$results = Invoke-RestMethod -Uri $solutionURL -Method POST -Headers $authHeader -Body ($body | ConvertTo-Json -EnumsAsStrings -Depth 5)
Write-Host "results..." $results


#Iterate through all the rule templates
foreach ($result in $results.data) {
    #Make sure that the template's severity is one we want to include
    $severity = $result.properties.template.resources.properties.severity[0]
    Write-Host "Severity is... " $severity " of type " $severity.GetType()
    if ($SeveritiesToInclude.Contains($severity)) {
        Write-Host "Enabling alert rule template... " $result.properties.template.resources.properties.displayName
        #Get to the actual template data
        $template = $result.properties.template.resources.properties
        $kind = $result.properties.template.resources.kind
        $name = $result.contentId
        $body = ""

        #For some reason there is a null as the last entry in the tactics array so we need to remove it
        $tactics = ""
        # If there is only 1 entry and the null, then if we return just the entry, it gets returned
        # as a string so we need to make sure we return an array
        if ($template.tactics.Count -eq 2) {
            [String[]]$tactics = $template.tactics[0]
        }
        else {
            #Return only those entries that are not null
            $tactics = $template.tactics | Where-Object { $_ -ne $null }
        }

        #For some reason there is a null as the last entry in the techniques array so we need to remove it
        $techniques = ""
        # If there is only 1 entry and the null, then if we return just the entry, it gets returned
        # as a string so we need to make sure we return an array
        
        if ($template.techniques.Count -eq 2) {
            [String[]]$techniques = $template.techniques[0]
        }
        else {
            #Return only those entries that are not null
            $techniques = $template.techniques | Where-Object { $_ -ne $null }
        }

        #For some reason there is a null as the last entry in the entities array so we need to remove it as well
        #as any entry that is just ".nan"
        $entityMappings = $template.entityMappings | Where-Object { $_ -ne $null }
        #If the arrary of EntityMappings only contained one entry, it will not be returned as an arry
        # so we need to convert it into JSON while forcing it to be an array and then convert it back
        # without enumerating the output so that it remains an array
        if ($null -ne $entityMappings) {
            if ($entityMappings.GetType().BaseType.Name -ne "Array") {
                $entityMappings = $entityMappings | ConvertTo-Json -Depth 5 -AsArray | ConvertFrom-Json -NoEnumerate
            }
        }
        
        #Some entity mappings are stored as empty strings (not sure why) so we need 
        #to check for that and set to null if it is empty so no error gets thrown
        #if ([String]::IsNullOrWhiteSpace($entityMappings)) {
        #    $entityMappings = $null
        #}
        
        $templateVersion = $template.version | Where-Object { $_ -ne $null }
        $suppressionDuration = $template.suppressionDuration | Where-Object { $_ -ne $null }

        #Depending on the type of alert we are creating, the body has different parameters
        switch ($kind) {
            #Have not seen any Microsoft Security rule templates coming from solutions
            "MicrosoftSecurityIncidentCreation" {  
                $body = @{
                    "kind"       = "MicrosoftSecurityIncidentCreation"
                    "properties" = @{
                        "enabled"       = "true"
                        "productFilter" = $template.productFilter
                        "displayName"   = $template.displayName
                    }
                }
            }
            "NRT" {
                #For some reason, all the string values are returned as arrays (with null as the second entry)
                #and we only care about the first entry hence the [0] after everything
                $body = @{
                    "kind"       = "NRT"
                    "properties" = @{
                        "enabled"               = "true"
                        "alertRuleTemplateName" = $name
                        "displayName"           = $template.displayName[0]
                        "description"           = $template.description[0]
                        "severity"              = $template.severity[0]
                        "tactics"               = $tactics
                        "techniques"            = $techniques
                        "query"                 = $template.query[0]
                        "suppressionDuration"   = $suppressionDuration
                        "suppressionEnabled"    = $false
                        "eventGroupingSettings" = $template.eventGroupingSettings[0]
                        "templateVersion"       = $templateVersion
                        "entityMappings"        = $entityMappings
                    }
                }
            }
            "Scheduled" {
                #For some reason, all the string values are returned as arrays (with null as the second entry)
                #and we only care about the first entry hence the [0] after everything
                $body = @{
                    "kind"       = "Scheduled"
                    "properties" = @{
                        "alertRuleTemplateName" = $name
                        "description"           = $template.description[0]
                        "displayName"           = $template.displayName[0]
                        "enabled"               = "true"
                        "entityMappings"        = $entityMappings
                        "eventGroupingSettings" = $template.eventGroupingSettings[0]
                        "query"                 = $template.query[0]
                        "queryFrequency"        = $template.queryFrequency[0]
                        "queryPeriod"           = $template.queryPeriod[0]
                        "severity"              = $template.severity[0]
                        "suppressionDuration"   = $suppressionDuration
                        "suppressionEnabled"    = $false
                        "tactics"               = $tactics
                        "techniques"            = $techniques
                        "templateVersion"       = $templateVersion
                        "triggerOperator"       = $template.triggerOperator[0]
                        "triggerThreshold"      = $template.triggerThreshold[0]
                    }
                }
            }
            #Hopefully this won't be accessed
            Default { }
        }
        #If we have created the body...
        if ("" -ne $body) {
            #Create the GUId for the alert.
            $guid = New-Guid

            #Create the URI we need to create the alert.  Using the latest and greatest API call
            $alertUriGuid = $alertUri + $guid + '?api-version=2022-11-01-preview'

            try {
                Invoke-AzRestMethod -Path $alertUriGuid -Method PUT -Payload ($body | ConvertTo-Json -EnumsAsStrings -Depth 8)
            }
            catch {
                #Most likely any errors are due to the rule template having errors, typically in the query
                Write-Verbose $_
                Write-Error "Unable to create alert rule with error code: $($_.Exception.Message)" -ErrorAction Stop
            }
        }
    }
}

return $return
