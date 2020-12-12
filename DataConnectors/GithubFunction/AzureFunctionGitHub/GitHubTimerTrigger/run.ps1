<#  
    Title:          GitHub Repo Logs Data Connector
    Language:       PowerShell
    Version:        1.1
    Author:         Nicholas Dicola, Sreedhar Ande
    Last Modified:  12/11/2020
    Comment:        Inital Release

    DESCRIPTION
    This Function App calls the GitHub REST API (https://api.github.com/) to pull the GitHub
    Audit, Repo and Vulnerability logs. The response from the GitHub API is recieved in JSON format. This function will build the signature and authorization header 
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. The Function App will post each log type to their individual tables in Log Analytics, for example,
    Github_CL and GitHubRepoLogs_CL.
#>

# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"

# Main
if ($env:MSI_SECRET -and (Get-Module -ListAvailable Az.Accounts)){
    Connect-AzAccount -Identity
}


$AzureWebJobsStorage = $env:AzureWebJobsStorage
$personalAccessToken = $env:PersonalAccessToken
$workspaceId = $env:WorkspaceId
$workspaceKey = $env:WorkspaceKey
$storageAccountContainer = "github-repo-logs"
$AuditLogTable = "GitHub_CL"
$RepoLogTable = "GitHubRepoLogs_CL"
$ResourceID = ""
$TimeStampField = ""
#The AzureTenant variable is used to specify other cloud environments like Azure Gov(.us) etc.,
$AzureTenant = $env:AZURE_TENANT

$currentStartTime = (get-date).ToUniversalTime() | get-date  -Format yyyy-MM-ddTHH:mm:ss:ffffffZ

#function to create HTTP Header signature required to authenticate post
Function New-BuildSignature {
    param(
        $customerId, 
        $sharedKey, 
        $date, 
        $contentLength, 
        $method, 
        $contentType, 
        $resource )
    
    $xHeaders = "x-ms-date:" + $date
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource
    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash)
    $keyBytes = [Convert]::FromBase64String($sharedKey)
    $sha256 = New-Object System.Security.Cryptography.HMACSHA256
    $sha256.Key = $keyBytes
    $calculatedHash = $sha256.ComputeHash($bytesToHash)
    $encodedHash = [Convert]::ToBase64String($calculatedHash)
    $authorization = 'SharedKey {0}:{1}' -f $customerId, $encodedHash
    return $authorization
}
        
# Function to create and post the request
Function Invoke-LogAnalyticsData {
    Param( 
        $CustomerId, 
        $SharedKey, 
        $Body, 
        $LogTable, 
        $timeStampField,
        $resourceId)

    $method = "POST"
    $contentType = "application/json"
    $resource = "/api/logs"
    $rfc1123date = [DateTime]::UtcNow.ToString("r")
    $contentLength = $Body.Length
    $signature = New-BuildSignature `
        -customerId $CustomerId `
        -sharedKey $SharedKey `
        -date $rfc1123date `
        -contentLength $contentLength `
        -method $method `
        -contentType $contentType `
        -resource $resource
    
    if ([string]::IsNullOrEmpty($AzureTenant)){
		$uri = "https://" + $CustomerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"
	}
	else{		
        $uri = "https://" + $CustomerId + ".ods.opinsights.azure" +$AzureTenant + $resource + "?api-version=2016-04-01"
    }
    
    $headers1 = @{
        "Authorization"        = $signature;
        "Log-Type"             = $LogTable;
        "x-ms-date"            = $rfc1123date;
        "x-ms-AzureResourceId" = $resourceId;
        "time-generated-field" = $timeStampField;
    }  
    $status = $false
    do {
        $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers1 -Body $Body
        If ($reponse.StatusCode -eq 429) {
            $rand = get-random -minimum 10 -Maximum 80
            start-sleep -seconds $rand 
        }
        else { $status = $true }
    }until($status) 
    Remove-variable -name Body
    return $response.StatusCode    
}

function SendToLogA ($gitHubData, $customLogName) {    
    IF (($gitHubData.Length) -gt 28MB) {
		Write-Host "Log length is greater than 28 MB, splitting and sending to Log Analytics"
		$bits = [math]::Round(($gitHubData.length) / 20MB) + 1
		$TotalRecords = $gitHubData.Count
		$RecSetSize = [math]::Round($TotalRecords / $bits) + 1
		$start = 0
		For ($x = 0; $x -lt $bits; $X++) {
			IF ( ($start + $recsetsize) -gt $TotalRecords) {
				$finish = $totalRecords
			}
			ELSE {
				$finish = $start + $RecSetSize
			}
			$body = Convertto-Json ($gitHubData[$start..$finish]) -Depth 5 -Compress
			$result = Invoke-LogAnalyticsData -CustomerId $workspaceId -SharedKey $workspaceKey -Body $body -LogTable $customLogName -TimeStampField $TimeStampField -ResourceId $ResourceID			
			$start = $Finish + 1
		}
		$null = Remove-variable -name body        

	}
	Else {		
		$result = Invoke-LogAnalyticsData -CustomerId $workspaceId -SharedKey $workspaceKey -Body $gitHubData -LogTable $customLogName -TimeStampField $TimeStampField -ResourceId $ResourceID		
	}
}

# header for API calls
$headers = @{
    Authorization = "bearer $personalAccessToken"
    'Content-Type' = "application/json"
}

#Get Orgs from ORGS.json in Az Storage
$storageAccountContext = New-AzStorageContext -ConnectionString $AzureWebJobsStorage
$checkBlob = Get-AzStorageBlob -Blob ORGS.json -Container $storageAccountContainer -Context $storageAccountContext
if($checkBlob -ne $null){
    Get-AzStorageBlobContent -Blob ORGS.json -Container $storageAccountContainer -Context $storageAccountContext -Destination $env:TMPDIR\orgs.json -Force
    $githubOrgs = Get-Content $env:TMPDIR\orgs.json | ConvertFrom-Json
}
else{
    Write-Error "No ORGS.json file, exiting"
    exit
}


#Process each Org
$repoList = @()
foreach($org in $githubOrgs){
    $orgName = $org.org
    Write-Host "Starting to process ORG: $orgName"
    
    #Get Audit Entries
    #check for last run file
    $checkBlob = Get-AzStorageBlob -Blob "lastrun-Audit.json" -Container $storageAccountContainer -Context $storageAccountContext
    if($checkBlob -ne $null){
        #Blob found get data
        Get-AzStorageBlobContent -Blob "lastrun-Audit.json" -Container $storageAccountContainer -Context $storageAccountContext -Destination "$env:TMPDIR\lastrun-Audit.json" -Force
        $lastRunAuditContext = Get-Content "$env:TMPDIR\lastrun-Audit.json" | ConvertFrom-Json
    }
    else {
        #no blob create the context
        $lastRun = $currentStartTime
        $lastRunAudit = @"
{
"lastRun": "$lastRun",
"lastContext": ""
}
"@
        $lastRunAudit | Out-File "$env:TMPDIR\lastrun-Audit.json"
        $lastRunAuditContext = $lastRunAudit | ConvertFrom-Json
    }

    #Build query based on previous lastruncontext or not
    $lastRunContext = $lastRunAuditContext.lastContext
    if($lastRunContext -eq ""){
        $AuditQuery = '{"query": "query { organization(login: \"'+$orgName+'\") { auditLog(first: 100 orderBy: { direction: ASC field: CREATED_AT }) { edges { node { ... on AuditEntry { action actor actorIp actorLocation { city country countryCode region regionCode } actorLogin actorResourcePath actorUrl createdAt operationType user { email } userLogin userResourcePath } ... on MembersCanDeleteReposClearAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposDisableAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposEnableAuditEntry { organizationName enterpriseSlug } ... on OauthApplicationCreateAuditEntry { applicationUrl oauthApplicationName organizationName state } ... on OrgAddBillingManagerAuditEntry { invitationEmail organizationName } ... on OrgAddMemberAuditEntry { organizationName permission } ... on OrgBlockUserAuditEntry { organizationName blockedUserName } ... on OrgConfigDisableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgConfigEnableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgCreateAuditEntry { organizationName } ... on OrgDisableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgDisableSamlAuditEntry { organizationName } ... on OrgDisableTwoFactorRequirementAuditEntry { organizationName } ... on OrgEnableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgEnableSamlAuditEntry { organizationName } ... on OrgEnableTwoFactorRequirementAuditEntry { organizationName } ... on OrgInviteMemberAuditEntry { email organizationName } ... on OrgInviteToBusinessAuditEntry { organizationName enterpriseSlug } ... on OrgOauthAppAccessApprovedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessDeniedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessRequestedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgRemoveBillingManagerAuditEntry { organizationName reason } ... on OrgRemoveMemberAuditEntry { organizationName membershipTypes reason } ... on OrgRemoveOutsideCollaboratorAuditEntry { organizationName membershipTypes reason } ... on OrgRestoreMemberAuditEntry { organizationName restoredMembershipsCount restoredRepositoriesCount restoredMemberships { ... on OrgRestoreMemberMembershipOrganizationAuditEntryData { organizationName } ... on OrgRestoreMemberMembershipRepositoryAuditEntryData { repositoryName } ... on OrgRestoreMemberMembershipTeamAuditEntryData { teamName } } } ... on OrgUnblockUserAuditEntry { blockedUserName organizationName } ... on OrgUpdateDefaultRepositoryPermissionAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberRepositoryCreationPermissionAuditEntry { canCreateRepositories organizationName visibility } ... on OrgUpdateMemberRepositoryInvitationPermissionAuditEntry { canInviteOutsideCollaboratorsToRepositories organizationName } ... on PrivateRepositoryForkingDisableAuditEntry { enterpriseSlug organizationName repositoryName } ... on PrivateRepositoryForkingEnableAuditEntry { enterpriseSlug organizationName repositoryName } ... on RepoAccessAuditEntry { organizationName repositoryName visibility } ... on RepoAddMemberAuditEntry { organizationName repositoryName visibility } ... on RepoAddTopicAuditEntry { organizationName repositoryName topicName } ... on RepoArchivedAuditEntry { organizationName repositoryName visibility } ... on RepoChangeMergeSettingAuditEntry { isEnabled mergeType organizationName repositoryName } ... on RepoConfigDisableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigDisableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigEnableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigEnableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigLockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigUnlockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoCreateAuditEntry { forkParentName forkSourceName organizationName repositoryName visibility } ... on RepoDestroyAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveMemberAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveTopicAuditEntry { organizationName repositoryName topicName } ... on RepositoryVisibilityChangeDisableAuditEntry { enterpriseSlug organizationName } ... on RepositoryVisibilityChangeEnableAuditEntry { enterpriseSlug organizationName } ... on TeamAddMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamAddRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } ... on TeamChangeParentTeamAuditEntry { organizationName parentTeamName parentTeamNameWas teamName } ... on TeamRemoveMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamRemoveRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } }"}'
    }
    else {
        $AuditQuery = '{"query": "query { organization(login: \"'+$orgName+'\") { auditLog(first: 100 orderBy: { direction: ASC field: CREATED_AT } after: \"'+$lastRunContext+'\") { edges { node { ... on AuditEntry { action actor actorIp actorLocation { city country countryCode region regionCode } actorLogin actorResourcePath actorUrl createdAt operationType user { email } userLogin userResourcePath } ... on MembersCanDeleteReposClearAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposDisableAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposEnableAuditEntry { organizationName enterpriseSlug } ... on OauthApplicationCreateAuditEntry { applicationUrl oauthApplicationName organizationName state } ... on OrgAddBillingManagerAuditEntry { invitationEmail organizationName } ... on OrgAddMemberAuditEntry { organizationName permission } ... on OrgBlockUserAuditEntry { organizationName blockedUserName } ... on OrgConfigDisableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgConfigEnableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgCreateAuditEntry { organizationName } ... on OrgDisableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgDisableSamlAuditEntry { organizationName } ... on OrgDisableTwoFactorRequirementAuditEntry { organizationName } ... on OrgEnableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgEnableSamlAuditEntry { organizationName } ... on OrgEnableTwoFactorRequirementAuditEntry { organizationName } ... on OrgInviteMemberAuditEntry { email organizationName } ... on OrgInviteToBusinessAuditEntry { organizationName enterpriseSlug } ... on OrgOauthAppAccessApprovedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessDeniedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessRequestedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgRemoveBillingManagerAuditEntry { organizationName reason } ... on OrgRemoveMemberAuditEntry { organizationName membershipTypes reason } ... on OrgRemoveOutsideCollaboratorAuditEntry { organizationName membershipTypes reason } ... on OrgRestoreMemberAuditEntry { organizationName restoredMembershipsCount restoredRepositoriesCount restoredMemberships { ... on OrgRestoreMemberMembershipOrganizationAuditEntryData { organizationName } ... on OrgRestoreMemberMembershipRepositoryAuditEntryData { repositoryName } ... on OrgRestoreMemberMembershipTeamAuditEntryData { teamName } } } ... on OrgUnblockUserAuditEntry { blockedUserName organizationName } ... on OrgUpdateDefaultRepositoryPermissionAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberRepositoryCreationPermissionAuditEntry { canCreateRepositories organizationName visibility } ... on OrgUpdateMemberRepositoryInvitationPermissionAuditEntry { canInviteOutsideCollaboratorsToRepositories organizationName } ... on PrivateRepositoryForkingDisableAuditEntry { enterpriseSlug organizationName repositoryName } ... on PrivateRepositoryForkingEnableAuditEntry { enterpriseSlug organizationName repositoryName } ... on RepoAccessAuditEntry { organizationName repositoryName visibility } ... on RepoAddMemberAuditEntry { organizationName repositoryName visibility } ... on RepoAddTopicAuditEntry { organizationName repositoryName topicName } ... on RepoArchivedAuditEntry { organizationName repositoryName visibility } ... on RepoChangeMergeSettingAuditEntry { isEnabled mergeType organizationName repositoryName } ... on RepoConfigDisableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigDisableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigEnableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigEnableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigLockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigUnlockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoCreateAuditEntry { forkParentName forkSourceName organizationName repositoryName visibility } ... on RepoDestroyAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveMemberAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveTopicAuditEntry { organizationName repositoryName topicName } ... on RepositoryVisibilityChangeDisableAuditEntry { enterpriseSlug organizationName } ... on RepositoryVisibilityChangeEnableAuditEntry { enterpriseSlug organizationName } ... on TeamAddMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamAddRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } ... on TeamChangeParentTeamAuditEntry { organizationName parentTeamName parentTeamNameWas teamName } ... on TeamRemoveMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamRemoveRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } }"}'
    }
    
    #Get the Audit Entries
    Write-Host "Starting to process ORG: $orgName Audit Entries"
    $hasNextPage = $true
    $uri = "https://api.github.com/graphql"
    do {
        $results = $null
        $results = Invoke-RestMethod -Method Post -Uri $uri -Body $AuditQuery -Headers $headers
        if(($results.data.organization.auditLog.edges).Count -ne 0){
            #write to log A to be added later           
            SendToLogA -gitHubData ($results.data.organization.auditLog.edges |  Convertto-json -depth 20) -customLogName $AuditLogTable
        }
        $hasNextPage = $results.data.organization.auditLog.pageInfo.hasNextPage
        $lastRunContext = $results.data.organization.auditLog.pageInfo.endCursor
        
        if ($lastRunContext -eq $null){
            $lastRunContext = ""
        }

        if($hasNextPage -ne $false){
            # if there is more data update the query with endcursor to use
            if($lastRunContext -eq ""){
                $AuditQuery = '{"query": "query { organization(login: \"'+$orgName+'\") { auditLog(first: 100 orderBy: { direction: ASC field: CREATED_AT }) { edges { node { ... on AuditEntry { action actor actorIp actorLocation { city country countryCode region regionCode } actorLogin actorResourcePath actorUrl createdAt operationType user { email } userLogin userResourcePath } ... on MembersCanDeleteReposClearAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposDisableAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposEnableAuditEntry { organizationName enterpriseSlug } ... on OauthApplicationCreateAuditEntry { applicationUrl oauthApplicationName organizationName state } ... on OrgAddBillingManagerAuditEntry { invitationEmail organizationName } ... on OrgAddMemberAuditEntry { organizationName permission } ... on OrgBlockUserAuditEntry { organizationName blockedUserName } ... on OrgConfigDisableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgConfigEnableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgCreateAuditEntry { organizationName } ... on OrgDisableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgDisableSamlAuditEntry { organizationName } ... on OrgDisableTwoFactorRequirementAuditEntry { organizationName } ... on OrgEnableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgEnableSamlAuditEntry { organizationName } ... on OrgEnableTwoFactorRequirementAuditEntry { organizationName } ... on OrgInviteMemberAuditEntry { email organizationName } ... on OrgInviteToBusinessAuditEntry { organizationName enterpriseSlug } ... on OrgOauthAppAccessApprovedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessDeniedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessRequestedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgRemoveBillingManagerAuditEntry { organizationName reason } ... on OrgRemoveMemberAuditEntry { organizationName membershipTypes reason } ... on OrgRemoveOutsideCollaboratorAuditEntry { organizationName membershipTypes reason } ... on OrgRestoreMemberAuditEntry { organizationName restoredMembershipsCount restoredRepositoriesCount restoredMemberships { ... on OrgRestoreMemberMembershipOrganizationAuditEntryData { organizationName } ... on OrgRestoreMemberMembershipRepositoryAuditEntryData { repositoryName } ... on OrgRestoreMemberMembershipTeamAuditEntryData { teamName } } } ... on OrgUnblockUserAuditEntry { blockedUserName organizationName } ... on OrgUpdateDefaultRepositoryPermissionAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberRepositoryCreationPermissionAuditEntry { canCreateRepositories organizationName visibility } ... on OrgUpdateMemberRepositoryInvitationPermissionAuditEntry { canInviteOutsideCollaboratorsToRepositories organizationName } ... on PrivateRepositoryForkingDisableAuditEntry { enterpriseSlug organizationName repositoryName } ... on PrivateRepositoryForkingEnableAuditEntry { enterpriseSlug organizationName repositoryName } ... on RepoAccessAuditEntry { organizationName repositoryName visibility } ... on RepoAddMemberAuditEntry { organizationName repositoryName visibility } ... on RepoAddTopicAuditEntry { organizationName repositoryName topicName } ... on RepoArchivedAuditEntry { organizationName repositoryName visibility } ... on RepoChangeMergeSettingAuditEntry { isEnabled mergeType organizationName repositoryName } ... on RepoConfigDisableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigDisableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigEnableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigEnableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigLockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigUnlockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoCreateAuditEntry { forkParentName forkSourceName organizationName repositoryName visibility } ... on RepoDestroyAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveMemberAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveTopicAuditEntry { organizationName repositoryName topicName } ... on RepositoryVisibilityChangeDisableAuditEntry { enterpriseSlug organizationName } ... on RepositoryVisibilityChangeEnableAuditEntry { enterpriseSlug organizationName } ... on TeamAddMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamAddRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } ... on TeamChangeParentTeamAuditEntry { organizationName parentTeamName parentTeamNameWas teamName } ... on TeamRemoveMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamRemoveRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } }"}'
            }
            else {
                $AuditQuery = '{"query": "query { organization(login: \"'+$orgName+'\") { auditLog(first: 100 orderBy: { direction: ASC field: CREATED_AT } after: \"'+$lastRunContext+'\") { edges { node { ... on AuditEntry { action actor actorIp actorLocation { city country countryCode region regionCode } actorLogin actorResourcePath actorUrl createdAt operationType user { email } userLogin userResourcePath } ... on MembersCanDeleteReposClearAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposDisableAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposEnableAuditEntry { organizationName enterpriseSlug } ... on OauthApplicationCreateAuditEntry { applicationUrl oauthApplicationName organizationName state } ... on OrgAddBillingManagerAuditEntry { invitationEmail organizationName } ... on OrgAddMemberAuditEntry { organizationName permission } ... on OrgBlockUserAuditEntry { organizationName blockedUserName } ... on OrgConfigDisableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgConfigEnableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgCreateAuditEntry { organizationName } ... on OrgDisableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgDisableSamlAuditEntry { organizationName } ... on OrgDisableTwoFactorRequirementAuditEntry { organizationName } ... on OrgEnableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgEnableSamlAuditEntry { organizationName } ... on OrgEnableTwoFactorRequirementAuditEntry { organizationName } ... on OrgInviteMemberAuditEntry { email organizationName } ... on OrgInviteToBusinessAuditEntry { organizationName enterpriseSlug } ... on OrgOauthAppAccessApprovedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessDeniedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessRequestedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgRemoveBillingManagerAuditEntry { organizationName reason } ... on OrgRemoveMemberAuditEntry { organizationName membershipTypes reason } ... on OrgRemoveOutsideCollaboratorAuditEntry { organizationName membershipTypes reason } ... on OrgRestoreMemberAuditEntry { organizationName restoredMembershipsCount restoredRepositoriesCount restoredMemberships { ... on OrgRestoreMemberMembershipOrganizationAuditEntryData { organizationName } ... on OrgRestoreMemberMembershipRepositoryAuditEntryData { repositoryName } ... on OrgRestoreMemberMembershipTeamAuditEntryData { teamName } } } ... on OrgUnblockUserAuditEntry { blockedUserName organizationName } ... on OrgUpdateDefaultRepositoryPermissionAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberRepositoryCreationPermissionAuditEntry { canCreateRepositories organizationName visibility } ... on OrgUpdateMemberRepositoryInvitationPermissionAuditEntry { canInviteOutsideCollaboratorsToRepositories organizationName } ... on PrivateRepositoryForkingDisableAuditEntry { enterpriseSlug organizationName repositoryName } ... on PrivateRepositoryForkingEnableAuditEntry { enterpriseSlug organizationName repositoryName } ... on RepoAccessAuditEntry { organizationName repositoryName visibility } ... on RepoAddMemberAuditEntry { organizationName repositoryName visibility } ... on RepoAddTopicAuditEntry { organizationName repositoryName topicName } ... on RepoArchivedAuditEntry { organizationName repositoryName visibility } ... on RepoChangeMergeSettingAuditEntry { isEnabled mergeType organizationName repositoryName } ... on RepoConfigDisableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigDisableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigEnableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigEnableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigLockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigUnlockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoCreateAuditEntry { forkParentName forkSourceName organizationName repositoryName visibility } ... on RepoDestroyAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveMemberAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveTopicAuditEntry { organizationName repositoryName topicName } ... on RepositoryVisibilityChangeDisableAuditEntry { enterpriseSlug organizationName } ... on RepositoryVisibilityChangeEnableAuditEntry { enterpriseSlug organizationName } ... on TeamAddMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamAddRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } ... on TeamChangeParentTeamAuditEntry { organizationName parentTeamName parentTeamNameWas teamName } ... on TeamRemoveMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamRemoveRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } }"}'
            }
        }
        else {
            # no more data write last run to az storage
            $lastRunAuditContext.lastContext = $lastRunContext
            $lastRunAuditContext.lastRun = $currentStartTime
            $lastRunAuditContext | ConvertTo-Json | Out-File "$env:TMPDIR\lastrun-Audit.json"
            Set-AzStorageBlobContent -Blob "lastrun-Audit.json" -Container $storageAccountContainer -Context $storageAccountContext -File "$env:TMPDIR\lastrun-Audit.json" -Force
        }
    } until ($hasNextPage -eq $false)
    
    $uri = $null
    $results = $null
    
    #get Org repos
    $hasMoreRepos = $true
    $pageNumber = 1
    do {
        $uri = "https://api.github.com/orgs/$orgName/repos?page=$pageNumber"
        $results = Invoke-RestMethod -Method GET -Uri $uri -Headers $headers
        $repoList += $results
        if($results.Count -eq 0){
            Write-Host "No more repos found for Org: $orgName"
            $hasMoreRepos = $false
        }
        else {
            Write-Host "Getting more repos for Org: $orgName"
            $pageNumber++
        }
    } until ($hasMoreRepos -eq $false)
    
    $uri = $null
    $results = $null

    #For Each Repo in Org, get repo logs
    foreach($repo in $repoList){
        $repoName = $repo.Name        
        $uri = "https://api.github.com/repos/$orgName/$repoName/contributors"
        $contributorsInfo = Invoke-WebRequest -Method Get -Uri $uri -Headers $headers -UseBasicParsing
        Write-Host $contributorsInfo.statuscode
        # Status 204 represents No Content - ie., empty repo
        if ($contributorsInfo.statuscode -ne 204)
        {
            Write-Host "Starting to process ORG: $orgName Repo: $repoName"

            $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/popular/referrers"
            $referrerLogs = $null
            $referrerLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            $referrerLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
            $referrerLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
            $referrerLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Referrers
            #Send to log A;
            SendToLogA -gitHubData $referrerLogs -customLogName $RepoLogTable
            

            $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/popular/paths"
            $pathLogs = $null
            $pathLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            $pathLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
            $pathLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
            $pathLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Paths
            #Send to log A;
            SendToLogA -gitHubData $pathLogs -customLogName $RepoLogTable
            
            $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/views"
            $viewLogs = $null
            $viewLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            $viewLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
            $viewLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
            $viewLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Views
            #Send to log A
            SendToLogA -gitHubData $viewLogs -customLogName $RepoLogTable            

            $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/clones"
            $cloneLogs = $null
            $cloneLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            $cloneLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
            $cloneLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
            $cloneLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Clones
            #Send to log A
            SendToLogA -gitHubData $cloneLogs -customLogName $RepoLogTable            

            $uri = "https://api.github.com/repos/$orgName/$repoName/commits"
            $commitLogs = $null
            $commitLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            $commitLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
            $commitLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
            $commitLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Commits
            #Send to log A
            SendToLogA -gitHubData $commitLogs -customLogName $RepoLogTable
            
            $uri = "https://api.github.com/repos/$orgName/$repoName/collaborators"
            $collaboratorLogs = $null
            $collaboratorLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            $collaboratorLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
            $collaboratorLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
            $collaboratorLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Collaborators
            #Send to log A
            SendToLogA -gitHubData $collaboratorLogs -customLogName $RepoLogTable            

            $uri = "https://api.github.com/repos/$orgName/$repoName/forks"
            $forkLogs = $null
            $forkLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            $forkLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
            $forkLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
            $forkLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Forks
            #Send to log A
            SendToLogA -gitHubData $forkLogs -customLogName $RepoLogTable            
        }
        else {
            Write-Host "$repoName is empty"
            Write-Verbose "$repoName is empty"
        }
        
        
    }
    
    # get blobs for last run
    # For each repo get Github Vulnerability Alerts
    $blobs = Get-AzStorageBlob -Context $storageAccountContext -Container $storageAccountContainer
    foreach($repo in $repoList){
        $repoName = $repo.name
        if($blobs.Name -contains "lastrun-$orgName-$repoName.json"){
            Get-AzStorageBlobContent -Blob "lastrun-$orgName-$repoName.json" -Container $storageAccountContainer -Context $storageAccountContext -Destination "$env:TMPDIR\lastrun-$orgName-$repoName.json" -Force
            $lastRunVulnContext = Get-Content "$env:TMPDIR\lastrun-$orgName-$repoName.json" | ConvertFrom-Json
        }
        else {
            $lastRun = $currentStartTime
            $lastRunVuln = @"
{
"lastRun": "$lastRun",
"lastContext": ""
}
"@
            $lastRunVuln| Out-File "$env:TMPDIR\lastrun-$orgName-$repoName.json"
            $lastRunVulnContext = $lastRunVuln | ConvertFrom-Json
            Set-AzStorageBlobContent -Container $storageAccountContainer -Context $storageAccountContext -File "$env:TMPDIR\lastrun-$orgName-$repoName.json" -Force
        }

        #Build the query based on previous context or not
        $lastRunContext = $lastRunVulnContext.lastContext
        if($lastRunContext -eq ""){
            $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100) { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'
        }
        else {
            $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100, after: \"'+$lastRunContext+'\") { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'
        }

        $hasNextPage = $true
        $vulnList = @()
        $uri = $null
        do {
            $uri = "https://api.github.com/graphql"
            $results = $null
            $results = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $VulnQuery
            if(($results.data.organization.repository.vulnerabilityAlerts.nodes).Count -ne 0){
                $vulnList += $results.data.organization.repository.vulnerabilityAlerts.nodes
                $vulnList | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $vulnList | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $vulnList | Add-Member -NotePropertyName LogType -NotePropertyValue vulnerabilityAlerts
                #send to log A; Name:GitHubRepoLogs
                SendToLogA -gitHubData $vulnList -customLogName $RepoLogTable                
            }
            $hasNextPage = $results.data.organization.repository.vulnerabilityAlerts.pageInfo.hasNextPage
            $lastRunContext = $results.data.organization.repository.vulnerabilityAlerts.pageInfo.endCursor
            if ($lastRunContext -eq $null){
                $lastRunContext = ""
            }
            if($hasNextPage -ne $false){
                if($lastRunContext -eq ""){
                    $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100) { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'
                }
                else {
                    $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100, after: \"'+$lastRunContext+'\") { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'
                }
            }
            else {
                $lastRunVulnContext.lastContext = $lastRunContext
                $lastRunVulnContext.lastRun = $currentStartTime
                $lastRunVulnContext | ConvertTo-Json | Out-File "$env:TMPDIR\lastrun-$orgName-$repoName.json"
                Set-AzStorageBlobContent -Blob "lastrun-$orgName-$repoName.json" -Container $storageAccountContainer -Context $storageAccountContext -File "$env:TMPDIR\lastrun-$orgName-$repoName.json" -Force
            }
        } until ($hasNextPage -eq $false)
    }
    #clear the repo list for next org
    $repoList = @()
}