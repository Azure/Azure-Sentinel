#Purpose: This is to create a parameterized function called AuditEventDataLookup_Func in the Log Analytics workspace.
#	  This function accepts Category/Subcategory/Change ID for Windows Event Auditing logs as string paramenter, and will return the value associate with the ID.

#Sample Usage: SecurityEvent | where EventID == 4719 | extend Category = AuditEventDataLookup_Func(CategoryId)


#Date: 14 Sept 2020


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
dynamic(
    {"%%8272":"System",
     "%%8273":"Logon/Logoff",
     "%%8274":"Object Access",
     "%%8275":"Privilege Use",
     "%%8276":"Detailed Tracking",
     "%%8277":"Policy Change",
     "%%8278":"Account Management",
     "%%8279":"DS Access",
     "%%8280":"Account Logon",
     "%%12288":"Security State Change",
     "%%12289":"Security System Extension",
     "%%12290":"System Integrity",
     "%%12291":"IPsec Driver",
     "%%12292":"Other System Events",
     "%%12544":"Logon",
     "%%12545":"Logoff",
     "%%12546":"Account Lockout",
     "%%12547":"IPsec Main Mode",
     "%%12548":"Special Logon",
     "%%12549":"IPsec Quick Mode",
     "%%12550":"IPsec Extended Mode",
     "%%12551":"Other Logon/Logoff Events",
     "%%12552":"Network Policy Server",
     "%%12553":"User/Device Claims",
     "%%12554":"Group Membership",
     "%%12800":"File System",
     "%%12801":"Registry",
     "%%12802":"Kernel Object",
     "%%12803":"SAM",
     "%%12804":"Other Object Access Events",
     "%%12805":"Certification Services",
     "%%12806":"Application Generated",
     "%%12807":"Handle Manipulation",
     "%%12808":"File Share",
     "%%12809":"Filtering Platform Packet Drop",
     "%%12810":"Filtering Platform Connection",
     "%%12811":"Detailed File Share",
     "%%12812":"Removable Storage",
     "%%12813":"Central Policy Staging",
     "%%13056":"Sensitive Privilege Use",
     "%%13057":"Non Sensitive Privilege Use",
     "%%13058":"Other Privilege Use Events",
     "%%13312":"Process Creation",
     "%%13313":"Process Termination",
     "%%13314":"DPAPI Activity",
     "%%13315":"RPC Events",
     "%%13316":"Plug and Play Events",
     "%%13317":"Token Right Adjusted Events",
     "%%13568":"Audit Policy Change",
     "%%13569":"Authentication Policy Change",
     "%%13570":"Authorization Policy Change",
     "%%13571":"MPSSVC Rule-Level Policy Change",
     "%%13572":"Filtering Platform Policy Change",
     "%%13573":"Other Policy Change Events",
     "%%13824":"User Account Management",
     "%%13825":"Computer Account Management",
     "%%13826":"Security Group Management",
     "%%13827":"Distribution Group Management",
     "%%13828":"Application Group Management",
     "%%13829":"Other Account Management Events",
     "%%14080":"Directory Service Access",
     "%%14081":"Directory Service Changes",
     "%%14082":"Directory Service Replication",
     "%%14083":"Detailed Directory Service Replication",
     "%%14336":"Credential Validation",
     "%%14337":"Kerberos Service Ticket Operations",
     "%%14338":"Other Account Logon Events",
     "%%14339":"Kerberos Authentication Service",
     "%%8448":"Success removed",
     "%%8449":"Success Added",
     "%%8450":"Failure removed",
     "%%8451":"Failure added",
     "%%8452":"Success include removed",
     "%%8453":"Success include added",
     "%%8454":"Success exclude removed",
     "%%8455":"Success exclude added",
     "%%8456":"Failure include removed",
     "%%8457":"Failure include added",
     "%%8458":"Failure exclude removed",
     "%%8459":"Failure exclude added"
})[ID]

"@


[PSCustomObject]$body = @{
"properties" = @{
    "Category" = "Function"
    "DisplayName" = "AuditEventDataLookup_Func"
    "FunctionAlias" = "AuditEventDataLookup_Func"
    "FunctionParameters" = "ID:string"
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


