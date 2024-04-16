<# Input Variables #>
<# $EnvironmentEndpointURL = Read-Host -Prompt 'Input Metallic RingURL / Commvault endpoint URL / examples: m102.metallic.io | 10.0.0.5' #>
<# $apiAccessToken = Read-Host -Prompt 'Input Commvault RestAPI user AccessToken' #>
<# $userIdentity = Read-Host -Prompt 'Enter User email or UPN' #>

Param(
[Parameter(Mandatory = $true)]
[String] $apiAccessToken,

[Parameter(Mandatory = $true)]
[String] $EnvironmentEndpointURL,

[Parameter(Mandatory = $true)]
[String] $userIdentity
)

<# End of Input Variables #>

<# Extract the userIdentity from the given userIdentity string #>

<# End of extraction #>

<# Global Variables #>
$headers = @{}
$headers.add("Accept", "application/json")
$headers.add("Content-Type","application/json")
$authToken = "QSDK "+$apiAccessToken
$headers.add("Authtoken",$authToken) 
<# End of Global Variables #> 

<# Get all Tenant Users #>
$getUsersURL = "https://$EnvironmentEndpointURL/commandcenter/api/User?level=10"
$getUsersResult = Invoke-RestMethod $getUsersURL -Method GET -Headers $headers
<# End of Get all Tenant Users #>

<# Select User based on email or UPN #>
$selectedUserID = "Empty"
$selectedUser = $getUsersResult.users | Where-Object { $_.email -eq $userIdentity -or $_.UPN -eq $userIdentity}
if ($selectedUser.email -eq $userIdentity -or $selectedUser.UPN -eq $userIdentity){
        $selectedUserID = $selectedUser.userEntity[0].userId
} else {Write-Output "User $userIdentity was not found"; Exit}
<# End of Select User based on email or UPN #>

<# Get selected user details #>
$getSelectedUserDetailsURL = "https://$EnvironmentEndpointURL/commandcenter/api/User/$selectedUserID"
$getSelectedUserDetailsResult = Invoke-RestMethod $getSelectedUserDetailsURL -Method GET -Headers $headers
<# End of Get selected user details #>

<# Check user if user is enabled and take action #>
if ($getSelectedUserDetailsResult.users.enableUser -eq $true) {
    $disableUserURL = "https://$EnvironmentEndpointURL/commandcenter/api/User/$selectedUserID/Disable"
    $disableUserResult = Invoke-RestMethod $disableUserURL -Method PUT -Headers $headers
    $disableUserResulterrorCode = $disableUserResult.response.errorCode
    if ($disableUserResulterrorCode -eq 0) {Write-Output "User $userIdentity was succesfully disabled"} else {
        Write-Output "Something went wrong. Error code $disableUserResulterrorCode for disabling User account $userIdentity do not indicate success."
    }
} elseif ($getSelectedUserDetailsResult.users.enableUser -eq $false) {
    Write-Output "User $userIdentity is already disabled. No action taken."
    } else {Write-Output "Something went wrong. Cannot retrieve status for user $userIdentity"}
<# End of Check user if user is enabled and take action #>

<# Get Selected User Sessions #>
$getSelectedUserSessionsURL = "https://$EnvironmentEndpointURL/commandcenter/api/Session?userId=$selectedUserID"
$getSelectedUserSessionsResult = Invoke-RestMethod $getSelectedUserSessionsURL -Method GET -Headers $headers
$expectedSelectedUserSessionsResult="*"
<# End of Get Selected User Sessions #>