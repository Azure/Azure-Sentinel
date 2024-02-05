param(
    [Parameter(Mandatory = $true)][string]$ResourceGroup,
    [Parameter(Mandatory = $true)][string]$Workspace,
    [Parameter(Mandatory = $false)][string[]]$Connectors,
    [Parameter(Mandatory = $false)][string[]]$SeveritiesToInclude = @("Informational", "Low", "Medium", "High")
)

$context = Get-AzContext

if (!$context) {
    Connect-AzAccount
    $context = Get-AzContext
}

$SubscriptionId = $context.Subscription.Id

Write-Host "Connected to Azure with subscription: " + $context.Subscription

$baseUri = "/subscriptions/${SubscriptionId}/resourceGroups/${ResourceGroup}/providers/Microsoft.OperationalInsights/workspaces/${Workspace}"
$templatesUri = "$baseUri/providers/Microsoft.SecurityInsights/alertRuleTemplates?api-version=2023-04-01-preview"
$alertUri = "$baseUri/providers/Microsoft.SecurityInsights/alertRules/"


try {
    $alertRulesTemplates = ((Invoke-AzRestMethod -Path $templatesUri -Method GET).Content | ConvertFrom-Json).value
}
catch {
    Write-Verbose $_
    Write-Error "Unable to get alert rules with error code: $($_.Exception.Message)" -ErrorAction Stop
}

$return = @()

if ($Connectors) {
    foreach ($item in $alertRulesTemplates) {
        #Make sure that the template's severity is one we want to include
        if ($SeveritiesToInclude.Contains($item.properties.severity)) {
            switch ($item.kind) {
                "Scheduled" {
                    foreach ($connector in $item.properties.requiredDataConnectors) {
                        if ($connector.connectorId -in $Connectors) {
                            #$return += $item.properties
                            $guid = New-Guid
                            $alertUriGuid = $alertUri + $guid + '?api-version=2023-02-01'

                            $properties = @{
                                displayName           = $item.properties.displayName
                                enabled               = $true
                                suppressionDuration   = "PT5H"
                                suppressionEnabled    = $false
                                alertRuleTemplateName = $item.name
                                description           = $item.properties.description
                                query                 = $item.properties.query
                                queryFrequency        = $item.properties.queryFrequency
                                queryPeriod           = $item.properties.queryPeriod
                                severity              = $item.properties.severity
                                tactics               = $item.properties.tactics
                                triggerOperator       = $item.properties.triggerOperator
                                triggerThreshold      = $item.properties.triggerThreshold
                                techniques            = $item.properties.techniques
                                eventGroupingSettings = $item.properties.eventGroupingSettings
                                templateVersion       = $item.properties.version
                                entityMappings        = $item.properties.entityMappings
                            }

                            $alertBody = @{}
                            $alertBody | Add-Member -NotePropertyName kind -NotePropertyValue $item.kind -Force
                            $alertBody | Add-Member -NotePropertyName properties -NotePropertyValue $properties

                            try {
                                Invoke-AzRestMethod -Path $alertUriGuid -Method PUT -Payload ($alertBody | ConvertTo-Json -Depth 5)
                            }
                            catch {
                                Write-Host "Can't enable rule template with connectors: " $item.properties.requiredDataConnectors
                                Write-Verbose $_
                                Write-Error "Unable to create alert rule with error code: $($_.Exception.Message)" -ErrorAction Stop
                            }

                            break
                        }
                    }
                }
                "NRT" {
                    foreach ($connector in $item.properties.requiredDataConnectors) {
                        if ($connector.connectorId -in $Connectors) {
                            #$return += $item.properties
                            $guid = New-Guid
                            $alertUriGuid = $alertUri + $guid + '?api-version=2022-12-01-preview'

                            $properties = @{
                                displayName           = $item.properties.displayName
                                enabled               = $true
                                suppressionDuration   = "PT5H"
                                suppressionEnabled    = $false
                                alertRuleTemplateName = $item.name
                                description           = $item.properties.description
                                query                 = $item.properties.query
                                severity              = $item.properties.severity
                                tactics               = $item.properties.tactics
                                techniques            = $item.properties.techniques
                                eventGroupingSettings = $item.properties.eventGroupingSettings
                                templateVersion       = $item.properties.version
                                entityMappings        = $item.properties.entityMappings
                            }

                            $alertBody = @{}
                            $alertBody | Add-Member -NotePropertyName kind -NotePropertyValue $item.kind -Force
                            $alertBody | Add-Member -NotePropertyName properties -NotePropertyValue $properties

                            try {
                                Invoke-AzRestMethod -Path $alertUriGuid -Method PUT -Payload ($alertBody | ConvertTo-Json -Depth 3)
                            }
                            catch {
                                Write-Host "Can't enable rule template with connectors: " $item.properties.requiredDataConnectors
                                Write-Verbose $_
                                Write-Error "Unable to create alert rule with error code: $($_.Exception.Message)" -ErrorAction Stop
                            }

                            break
                        }
                    }
                }
            }
        }
    
    }
}

#####
#create rules from any rule templates that came from solutions
#####

$solutionURL = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01"
  
#We only care about those rule templates that were created by Microsoft Sentinel solutions so
#this query will make sure to filter out anything else as well as provide some overview data (which is not used)
$query = @"
    Resources 
    | where type =~ 'Microsoft.Resources/templateSpecs/versions' 
    | where tags['hidden-sentinelContentType'] =~ 'AnalyticsRule' 
    and tags['hidden-sentinelWorkspaceId'] =~ '/subscriptions/$($subscriptionId)/resourceGroups/$($ResourceGroup)/providers/Microsoft.OperationalInsights/workspaces/$($Workspace)' 
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
    'Content-Type'  = 'application/json'
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
    Write-Host "Severities to include..." $SeveritiesToInclude
    Write-Host "condition is..." $SeveritiesToInclude.Contains($severity)   
    if ($SeveritiesToInclude.Contains($severity)) {
        Write-Host "Enabling solution rule template... " $result.properties.template.resources.properties.displayName
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
        $entityMappings = $template.entityMappings  | Where-Object { $_ -ne $null } | Where-Object { $_ -ne ".nan" }
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
        if ([String]::IsNullOrWhiteSpace($entityMappings)) {
            $entityMappings = $null
        }

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
                        "suppressionDuration"   = "PT5H"
                        "suppressionEnabled"    = $false
                        "eventGroupingSettings" = $template.eventGroupingSettings[0]
                        "templateVersion"       = $template.version[0]
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
                        "enabled"               = "true"
                        "alertRuleTemplateName" = $name
                        "displayName"           = $template.displayName[0]
                        "description"           = $template.description[0]
                        "severity"              = $template.severity[0]
                        "tactics"               = $tactics
                        "techniques"            = $techniques
                        "query"                 = $template.query[0]
                        "queryFrequency"        = $template.queryFrequency[0]
                        "queryPeriod"           = $template.queryPeriod[0]
                        "triggerOperator"       = $template.triggerOperator[0]
                        "triggerThreshold"      = $template.triggerThreshold[0]
                        "suppressionDuration"   = "PT5H"
                        "suppressionEnabled"    = $false
                        "eventGroupingSettings" = $template.eventGroupingSettings[0]
                        "templateVersion"       = $template.version[0]
                        "entityMappings"        = $entityMappings
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
            $alertUriGuid = $alertUri + $guid + '?api-version=2022-12-01-preview'

            try {
                Invoke-AzRestMethod -Path $alertUriGuid -Method PUT -Payload ($body | ConvertTo-Json -EnumsAsStrings -Depth 5)
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
