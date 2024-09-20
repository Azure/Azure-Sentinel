#Purpose: This is to create a nested parameterized function called EnrichAuditEvents_Func in the Log Analytics workspace.
#	  This function accepts table records from the SecurityEvent table and will invoke another function (AuditEventDataLookup_Func) to perform enrichment.

#Sample Usage: let AuditEvents = (SecurityEvent | where EventID == 4719); EnrichAuditEvents_Func(AuditEvents)

#Date: 23 Sept 2020

#Setup Variables
$ResourceGroup = "<ResourceGroup>"
$WorkspaceName = "<WorkspaceName>"
$SubscriptionID = "<SubscriptionID>"

#Setup the environment
$workspaceid = "https://management.azure.com/subscriptions/${SubscriptionID}/resourceGroups/${ResourceGroup}/providers/Microsoft.OperationalInsights/workspaces/${WorkspaceName}"

#Connect to your workspace
Clear-AzContext -force

Connect-AzAccount

Get-AzSubscription
Select-AzSubscription -SubscriptionId $SubscriptionID


#Create the Parameter Function

$Query = @"
Tbl
| extend Category = AuditEventDataLookup_Func(CategoryId)
| extend SubCategory = AuditEventDataLookup_Func(SubcategoryId)
| extend AuditPolicyChangesParse = parse_csv(AuditPolicyChanges)
| extend AuditPolicyChange = trim_end(",", strcat(AuditEventDataLookup_Func(AuditPolicyChangesParse[0]) ,",",AuditEventDataLookup_Func(trim(" ",tostring(AuditPolicyChangesParse[1])))))
| project TimeGenerated, Computer, Activity, Category, SubCategory, AuditPolicyChange 
"@


[PSCustomObject]$body = @{
"properties" = @{
    "Category" = "Function"
    "DisplayName" = "EnrichAuditEvents_Func"
    "FunctionAlias" = "EnrichAuditEvents_Func"
    "FunctionParameters" = "Tbl:(TimeGenerated:datetime, Computer:string,Activity:string,CategoryId:string,SubcategoryId:string,AuditPolicyChanges:string)"
    "Query" = $Query
}
}


#Get auth token
#$token = Get-AzCachedAccessToken
$azProfile = [Microsoft.Azure.Commands.Common.Authentication.Abstractions.AzureRmProfileProvider]::Instance.Profile
if (-not $azProfile.Accounts.Count) {
       Write-Error "Ensure you have logged in (Connect-AzAccount) before calling this function."
    }

$currentAzureContext = Get-AzContext

$profileClient = New-Object Microsoft.Azure.Commands.ResourceManager.Common.RMProfileClient($azProfile)
Write-Output ("Getting access token for tenant" + $currentAzureContext.Subscription.TenantId)
$token = $profileClient.AcquireAccessToken($currentAzureContext.Subscription.TenantId)


#Build the API header with the auth token
$authHeader = @{
'Content-Type'='application/json'
'Authorization'='Bearer ' + $token.AccessToken
}


#Invoke WebRequest
try{
    $uri = "${workspaceId}/savedSearches/$((New-Guid).Guid)?api-version=2020-08-01"
    $result = Invoke-WebRequest -Uri $uri -Method Put -Headers $authHeader -Body($body | ConvertTo-Json -Depth 10)
    Write-Output "Successfully created function: $($DisplayName) with status: $($result.StatusDescription)"
    Write-Output ($body.properties | Format-Table)
    Write-Output $result.Content
    }
catch {
    Write-Verbose $_
    Write-Error "Unable to invoke webrequest with error message: $($_.Exception.Message)" -ErrorAction Stop
}


