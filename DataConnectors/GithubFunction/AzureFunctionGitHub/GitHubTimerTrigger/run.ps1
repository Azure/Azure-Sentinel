<#  
    Title:          GitHub Repo Logs Data Connector
    Language:       PowerShell
    Version:        1.2
    Author:         Nicholas Dicola, Sreedhar Ande
    Last Modified:  03/29/2021
    
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
$LAURI = $env:LAURI
$storageAccountContainer = "github-repo-logs"
$AuditLogTable = "GitHub_CL"
$RepoLogTable = "GitHubRepoLogs_CL"

$currentStartTime = (get-date).ToUniversalTime() | get-date  -Format yyyy-MM-ddTHH:mm:ss:ffffffZ

if (-Not [string]::IsNullOrEmpty($LAURI)){
	if($LAURI.Trim() -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
	{
		Write-Error -Message "DocuSign-SecurityEvents: Invalid Log Analytics Uri." -ErrorAction Stop
		Exit
	}
}

function Write-OMSLogfile {
    <#
    .SYNOPSIS
    Inputs a hashtable, date and workspace type and writes it to a Log Analytics Workspace.
    .DESCRIPTION
    Given a  value pair hash table, this function will write the data to an OMS Log Analytics workspace.
    Certain variables, such as Customer ID and Shared Key are specific to the OMS workspace data is being written to.
    This function will not write to multiple OMS workspaces.  BuildSignature and post-analytics function from Microsoft documentation
    at https://docs.microsoft.com/azure/log-analytics/log-analytics-data-collector-api
    .PARAMETER DateTime
    date and time for the log.  DateTime value
    .PARAMETER Type
    Name of the logfile or Log Analytics "Type".  Log Analytics will append _CL at the end of custom logs  String Value
    .PARAMETER LogData
    A series of key, value pairs that will be written to the log.  Log file are unstructured but the key should be consistent
    withing each source.
    .INPUTS
    The parameters of data and time, type and logdata.  Logdata is converted to JSON to submit to Log Analytics.
    .OUTPUTS
    The Function will return the HTTP status code from the Post method.  Status code 200 indicates the request was received.
    .NOTES
    Version:        2.0
    Author:         Travis Roberts
    Creation Date:  7/9/2018
    Purpose/Change: Crating a stand alone function    
    #>
    [cmdletbinding()]
    Param(
        [Parameter(Mandatory = $true, Position = 0)]
        [datetime]$dateTime,
        [parameter(Mandatory = $true, Position = 1)]
        [string]$type,
        [Parameter(Mandatory = $true, Position = 2)]
        [psobject]$logdata,
        [Parameter(Mandatory = $true, Position = 3)]
        [string]$CustomerID,
        [Parameter(Mandatory = $true, Position = 4)]
        [string]$SharedKey
    )
    Write-Verbose -Message "DateTime: $dateTime"
    Write-Verbose -Message ('DateTimeKind:' + $dateTime.kind)
    Write-Verbose -Message "Type: $type"
    write-Verbose -Message "LogData: $logdata"   

    # Supporting Functions
    # Function to create the auth signature
    function BuildSignature ($CustomerID, $SharedKey, $Date, $ContentLength, $method, $ContentType, $resource) {
        $xheaders = 'x-ms-date:' + $Date
        $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource
        $bytesToHash = [text.Encoding]::UTF8.GetBytes($stringToHash)
        $keyBytes = [Convert]::FromBase64String($SharedKey)
        $sha256 = New-Object System.Security.Cryptography.HMACSHA256
        $sha256.key = $keyBytes
        $calculateHash = $sha256.ComputeHash($bytesToHash)
        $encodeHash = [convert]::ToBase64String($calculateHash)
        $authorization = 'SharedKey {0}:{1}' -f $CustomerID, $encodeHash
        return $authorization
    }
    # Function to create and post the request
    Function PostLogAnalyticsData ($CustomerID, $SharedKey, $Body, $Type) {
        $method = "POST"
        $ContentType = 'application/json'
        $resource = '/api/logs'
        $rfc1123date = ($dateTime).ToString('r')
        $ContentLength = $Body.Length
        $signature = BuildSignature `
            -customerId $CustomerID `
            -sharedKey $SharedKey `
            -date $rfc1123date `
            -contentLength $ContentLength `
            -method $method `
            -contentType $ContentType `
            -resource $resource
        
		# Compatible with previous version
		if ([string]::IsNullOrEmpty($LAURI)){
			$LAURI = "https://" + $CustomerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"
		}
		else
		{
			$LAURI = $LAURI + $resource + "?api-version=2016-04-01"
		}
		
        $headers = @{
            "Authorization"        = $signature;
            "Log-Type"             = $type;
            "x-ms-date"            = $rfc1123date
            "time-generated-field" = $dateTime
        }
        $response = Invoke-WebRequest -Uri $LAURI -Method $method -ContentType $ContentType -Headers $headers -Body $Body -UseBasicParsing
        Write-Verbose -message ('Post Function Return Code ' + $response.statuscode)
        return $response.statuscode
    }

    # Check if time is UTC, Convert to UTC if not.
    # $dateTime = (Get-Date)
    if ($dateTime.kind.tostring() -ne 'Utc') {
        $dateTime = $dateTime.ToUniversalTime()
        Write-Verbose -Message $dateTime
    }

    # Add DateTime to hashtable
    #$logdata.add("DateTime", $dateTime)
    $logdata | Add-Member -MemberType NoteProperty -Name "DateTime" -Value $dateTime

    #Build the JSON file
    $logMessage = ($logdata | ConvertTo-Json -Depth 20)
    Write-Verbose -Message $logMessage

    #Submit the data
    $returnCode = PostLogAnalyticsData -CustomerID $CustomerID -SharedKey $SharedKey -Body $logMessage -Type $type
    Write-Verbose -Message "Post Statement Return Code $returnCode"
    return $returnCode
}

function SendToLogA ($gitHubData, $customLogName) {    
    #Test Size; Log A limit is 30MB
    $tempdata = @()
    $tempDataSize = 0
    
    if ((($gitHubData |  Convertto-json -depth 20).Length) -gt 25MB) {        
		Write-Host "Upload is over 25MB, needs to be split"									 
        foreach ($record in $gitHubData) {            
            $tempdata += $record
            $tempDataSize += ($record | ConvertTo-Json -depth 20).Length
            if ($tempDataSize -gt 25MB) {
                Write-OMSLogfile -dateTime (Get-Date) -type $customLogName -logdata $tempdata -CustomerID $workspaceId -SharedKey $workspaceKey
                write-Host "Sending data = $TempDataSize"
                $tempdata = $null
                $tempdata = @()
                $tempDataSize = 0
            }
        }
        Write-Host "Sending left over data = $Tempdatasize"
        Write-OMSLogfile -dateTime (Get-Date) -type $customLogName -logdata $gitHubData -CustomerID $workspaceId -SharedKey $workspaceKey
    }
    Else {
        #Send to Log A as is        
        Write-OMSLogfile -dateTime (Get-Date) -type $customLogName -logdata $gitHubData -CustomerID $workspaceId -SharedKey $workspaceKey
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
    Get-AzStorageBlobContent -Blob ORGS.json -Container $storageAccountContainer -Context $storageAccountContext -Destination "$env:temp\orgs.json" -Force
    $githubOrgs = Get-Content "$env:temp\orgs.json" | ConvertFrom-Json
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
        Get-AzStorageBlobContent -Blob "lastrun-Audit.json" -Container $storageAccountContainer -Context $storageAccountContext -Destination "$env:temp\lastrun-Audit.json" -Force
        $lastRunAuditContext = Get-Content "$env:temp\lastrun-Audit.json" | ConvertFrom-Json
    }
    else {
        #no blob create the context
        $lastRun = $currentStartTime
        $lastRunAudit = @"
{
"org":$orgName
"lastRun": "$lastRun",
"lastContext": ""
}
"@
        $lastRunAudit | Out-File "$env:temp\lastrun-Audit.json"
        $lastRunAuditContext = $lastRunAudit | ConvertFrom-Json
    }

    #Build query based on previous lastruncontext or not
    $lastRunContext = $lastRunAuditContext | Where-Object {$_.org -eq $orgName}
    if([string]::IsNullOrEmpty($lastRunContext.lastContext)){
        $AuditQuery = '{"query": "query { organization(login: \"'+$orgName+'\") { auditLog(first: 100 orderBy: { direction: ASC field: CREATED_AT }) { edges { node { ... on AuditEntry { action actor actorIp actorLocation { city country countryCode region regionCode } actorLogin actorResourcePath actorUrl createdAt operationType user { email } userLogin userResourcePath } ... on MembersCanDeleteReposClearAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposDisableAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposEnableAuditEntry { organizationName enterpriseSlug } ... on OauthApplicationCreateAuditEntry { applicationUrl oauthApplicationName organizationName state } ... on OrgAddBillingManagerAuditEntry { invitationEmail organizationName } ... on OrgAddMemberAuditEntry { organizationName permission } ... on OrgBlockUserAuditEntry { organizationName blockedUserName } ... on OrgConfigDisableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgConfigEnableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgCreateAuditEntry { organizationName } ... on OrgDisableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgDisableSamlAuditEntry { organizationName } ... on OrgDisableTwoFactorRequirementAuditEntry { organizationName } ... on OrgEnableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgEnableSamlAuditEntry { organizationName } ... on OrgEnableTwoFactorRequirementAuditEntry { organizationName } ... on OrgInviteMemberAuditEntry { email organizationName } ... on OrgInviteToBusinessAuditEntry { organizationName enterpriseSlug } ... on OrgOauthAppAccessApprovedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessDeniedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessRequestedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgRemoveBillingManagerAuditEntry { organizationName reason } ... on OrgRemoveMemberAuditEntry { organizationName membershipTypes reason } ... on OrgRemoveOutsideCollaboratorAuditEntry { organizationName membershipTypes reason } ... on OrgRestoreMemberAuditEntry { organizationName restoredMembershipsCount restoredRepositoriesCount restoredMemberships { ... on OrgRestoreMemberMembershipOrganizationAuditEntryData { organizationName } ... on OrgRestoreMemberMembershipRepositoryAuditEntryData { repositoryName } ... on OrgRestoreMemberMembershipTeamAuditEntryData { teamName } } } ... on OrgUnblockUserAuditEntry { blockedUserName organizationName } ... on OrgUpdateDefaultRepositoryPermissionAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberRepositoryCreationPermissionAuditEntry { canCreateRepositories organizationName visibility } ... on OrgUpdateMemberRepositoryInvitationPermissionAuditEntry { canInviteOutsideCollaboratorsToRepositories organizationName } ... on PrivateRepositoryForkingDisableAuditEntry { enterpriseSlug organizationName repositoryName } ... on PrivateRepositoryForkingEnableAuditEntry { enterpriseSlug organizationName repositoryName } ... on RepoAccessAuditEntry { organizationName repositoryName visibility } ... on RepoAddMemberAuditEntry { organizationName repositoryName visibility } ... on RepoAddTopicAuditEntry { organizationName repositoryName topicName } ... on RepoArchivedAuditEntry { organizationName repositoryName visibility } ... on RepoChangeMergeSettingAuditEntry { isEnabled mergeType organizationName repositoryName } ... on RepoConfigDisableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigDisableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigEnableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigEnableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigLockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigUnlockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoCreateAuditEntry { forkParentName forkSourceName organizationName repositoryName visibility } ... on RepoDestroyAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveMemberAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveTopicAuditEntry { organizationName repositoryName topicName } ... on RepositoryVisibilityChangeDisableAuditEntry { enterpriseSlug organizationName } ... on RepositoryVisibilityChangeEnableAuditEntry { enterpriseSlug organizationName } ... on TeamAddMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamAddRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } ... on TeamChangeParentTeamAuditEntry { organizationName parentTeamName parentTeamNameWas teamName } ... on TeamRemoveMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamRemoveRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } }"}'
    }
    else {
        $AuditQuery = '{"query": "query { organization(login: \"'+$orgName+'\") { auditLog(first: 100 orderBy: { direction: ASC field: CREATED_AT } after: \"'+$lastRunContext.lastContext+'\") { edges { node { ... on AuditEntry { action actor actorIp actorLocation { city country countryCode region regionCode } actorLogin actorResourcePath actorUrl createdAt operationType user { email } userLogin userResourcePath } ... on MembersCanDeleteReposClearAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposDisableAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposEnableAuditEntry { organizationName enterpriseSlug } ... on OauthApplicationCreateAuditEntry { applicationUrl oauthApplicationName organizationName state } ... on OrgAddBillingManagerAuditEntry { invitationEmail organizationName } ... on OrgAddMemberAuditEntry { organizationName permission } ... on OrgBlockUserAuditEntry { organizationName blockedUserName } ... on OrgConfigDisableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgConfigEnableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgCreateAuditEntry { organizationName } ... on OrgDisableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgDisableSamlAuditEntry { organizationName } ... on OrgDisableTwoFactorRequirementAuditEntry { organizationName } ... on OrgEnableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgEnableSamlAuditEntry { organizationName } ... on OrgEnableTwoFactorRequirementAuditEntry { organizationName } ... on OrgInviteMemberAuditEntry { email organizationName } ... on OrgInviteToBusinessAuditEntry { organizationName enterpriseSlug } ... on OrgOauthAppAccessApprovedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessDeniedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessRequestedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgRemoveBillingManagerAuditEntry { organizationName reason } ... on OrgRemoveMemberAuditEntry { organizationName membershipTypes reason } ... on OrgRemoveOutsideCollaboratorAuditEntry { organizationName membershipTypes reason } ... on OrgRestoreMemberAuditEntry { organizationName restoredMembershipsCount restoredRepositoriesCount restoredMemberships { ... on OrgRestoreMemberMembershipOrganizationAuditEntryData { organizationName } ... on OrgRestoreMemberMembershipRepositoryAuditEntryData { repositoryName } ... on OrgRestoreMemberMembershipTeamAuditEntryData { teamName } } } ... on OrgUnblockUserAuditEntry { blockedUserName organizationName } ... on OrgUpdateDefaultRepositoryPermissionAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberRepositoryCreationPermissionAuditEntry { canCreateRepositories organizationName visibility } ... on OrgUpdateMemberRepositoryInvitationPermissionAuditEntry { canInviteOutsideCollaboratorsToRepositories organizationName } ... on PrivateRepositoryForkingDisableAuditEntry { enterpriseSlug organizationName repositoryName } ... on PrivateRepositoryForkingEnableAuditEntry { enterpriseSlug organizationName repositoryName } ... on RepoAccessAuditEntry { organizationName repositoryName visibility } ... on RepoAddMemberAuditEntry { organizationName repositoryName visibility } ... on RepoAddTopicAuditEntry { organizationName repositoryName topicName } ... on RepoArchivedAuditEntry { organizationName repositoryName visibility } ... on RepoChangeMergeSettingAuditEntry { isEnabled mergeType organizationName repositoryName } ... on RepoConfigDisableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigDisableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigEnableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigEnableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigLockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigUnlockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoCreateAuditEntry { forkParentName forkSourceName organizationName repositoryName visibility } ... on RepoDestroyAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveMemberAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveTopicAuditEntry { organizationName repositoryName topicName } ... on RepositoryVisibilityChangeDisableAuditEntry { enterpriseSlug organizationName } ... on RepositoryVisibilityChangeEnableAuditEntry { enterpriseSlug organizationName } ... on TeamAddMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamAddRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } ... on TeamChangeParentTeamAuditEntry { organizationName parentTeamName parentTeamNameWas teamName } ... on TeamRemoveMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamRemoveRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } }"}'
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
            SendToLogA -gitHubData ($results.data.organization.auditLog.edges) -customLogName $AuditLogTable
        }
        $hasNextPage = $results.data.organization.auditLog.pageInfo.hasNextPage
        $lastRunContext.lastContext = $results.data.organization.auditLog.pageInfo.endCursor
        
        if ($lastRunContext.lastContext -eq $null){
            $lastRunContext.lastContext = ""
        }

        if($hasNextPage -ne $false){
            # if there is more data update the query with endcursor to use
            if([string]::IsNullOrEmpty($lastRunContext.lastContext)){
                $AuditQuery = '{"query": "query { organization(login: \"'+$orgName+'\") { auditLog(first: 100 orderBy: { direction: ASC field: CREATED_AT }) { edges { node { ... on AuditEntry { action actor actorIp actorLocation { city country countryCode region regionCode } actorLogin actorResourcePath actorUrl createdAt operationType user { email } userLogin userResourcePath } ... on MembersCanDeleteReposClearAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposDisableAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposEnableAuditEntry { organizationName enterpriseSlug } ... on OauthApplicationCreateAuditEntry { applicationUrl oauthApplicationName organizationName state } ... on OrgAddBillingManagerAuditEntry { invitationEmail organizationName } ... on OrgAddMemberAuditEntry { organizationName permission } ... on OrgBlockUserAuditEntry { organizationName blockedUserName } ... on OrgConfigDisableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgConfigEnableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgCreateAuditEntry { organizationName } ... on OrgDisableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgDisableSamlAuditEntry { organizationName } ... on OrgDisableTwoFactorRequirementAuditEntry { organizationName } ... on OrgEnableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgEnableSamlAuditEntry { organizationName } ... on OrgEnableTwoFactorRequirementAuditEntry { organizationName } ... on OrgInviteMemberAuditEntry { email organizationName } ... on OrgInviteToBusinessAuditEntry { organizationName enterpriseSlug } ... on OrgOauthAppAccessApprovedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessDeniedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessRequestedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgRemoveBillingManagerAuditEntry { organizationName reason } ... on OrgRemoveMemberAuditEntry { organizationName membershipTypes reason } ... on OrgRemoveOutsideCollaboratorAuditEntry { organizationName membershipTypes reason } ... on OrgRestoreMemberAuditEntry { organizationName restoredMembershipsCount restoredRepositoriesCount restoredMemberships { ... on OrgRestoreMemberMembershipOrganizationAuditEntryData { organizationName } ... on OrgRestoreMemberMembershipRepositoryAuditEntryData { repositoryName } ... on OrgRestoreMemberMembershipTeamAuditEntryData { teamName } } } ... on OrgUnblockUserAuditEntry { blockedUserName organizationName } ... on OrgUpdateDefaultRepositoryPermissionAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberRepositoryCreationPermissionAuditEntry { canCreateRepositories organizationName visibility } ... on OrgUpdateMemberRepositoryInvitationPermissionAuditEntry { canInviteOutsideCollaboratorsToRepositories organizationName } ... on PrivateRepositoryForkingDisableAuditEntry { enterpriseSlug organizationName repositoryName } ... on PrivateRepositoryForkingEnableAuditEntry { enterpriseSlug organizationName repositoryName } ... on RepoAccessAuditEntry { organizationName repositoryName visibility } ... on RepoAddMemberAuditEntry { organizationName repositoryName visibility } ... on RepoAddTopicAuditEntry { organizationName repositoryName topicName } ... on RepoArchivedAuditEntry { organizationName repositoryName visibility } ... on RepoChangeMergeSettingAuditEntry { isEnabled mergeType organizationName repositoryName } ... on RepoConfigDisableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigDisableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigEnableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigEnableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigLockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigUnlockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoCreateAuditEntry { forkParentName forkSourceName organizationName repositoryName visibility } ... on RepoDestroyAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveMemberAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveTopicAuditEntry { organizationName repositoryName topicName } ... on RepositoryVisibilityChangeDisableAuditEntry { enterpriseSlug organizationName } ... on RepositoryVisibilityChangeEnableAuditEntry { enterpriseSlug organizationName } ... on TeamAddMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamAddRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } ... on TeamChangeParentTeamAuditEntry { organizationName parentTeamName parentTeamNameWas teamName } ... on TeamRemoveMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamRemoveRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } }"}'
            }
            else {
                $AuditQuery = '{"query": "query { organization(login: \"'+$orgName+'\") { auditLog(first: 100 orderBy: { direction: ASC field: CREATED_AT } after: \"'+$lastRunContext.lastContext+'\") { edges { node { ... on AuditEntry { action actor actorIp actorLocation { city country countryCode region regionCode } actorLogin actorResourcePath actorUrl createdAt operationType user { email } userLogin userResourcePath } ... on MembersCanDeleteReposClearAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposDisableAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposEnableAuditEntry { organizationName enterpriseSlug } ... on OauthApplicationCreateAuditEntry { applicationUrl oauthApplicationName organizationName state } ... on OrgAddBillingManagerAuditEntry { invitationEmail organizationName } ... on OrgAddMemberAuditEntry { organizationName permission } ... on OrgBlockUserAuditEntry { organizationName blockedUserName } ... on OrgConfigDisableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgConfigEnableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgCreateAuditEntry { organizationName } ... on OrgDisableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgDisableSamlAuditEntry { organizationName } ... on OrgDisableTwoFactorRequirementAuditEntry { organizationName } ... on OrgEnableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgEnableSamlAuditEntry { organizationName } ... on OrgEnableTwoFactorRequirementAuditEntry { organizationName } ... on OrgInviteMemberAuditEntry { email organizationName } ... on OrgInviteToBusinessAuditEntry { organizationName enterpriseSlug } ... on OrgOauthAppAccessApprovedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessDeniedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessRequestedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgRemoveBillingManagerAuditEntry { organizationName reason } ... on OrgRemoveMemberAuditEntry { organizationName membershipTypes reason } ... on OrgRemoveOutsideCollaboratorAuditEntry { organizationName membershipTypes reason } ... on OrgRestoreMemberAuditEntry { organizationName restoredMembershipsCount restoredRepositoriesCount restoredMemberships { ... on OrgRestoreMemberMembershipOrganizationAuditEntryData { organizationName } ... on OrgRestoreMemberMembershipRepositoryAuditEntryData { repositoryName } ... on OrgRestoreMemberMembershipTeamAuditEntryData { teamName } } } ... on OrgUnblockUserAuditEntry { blockedUserName organizationName } ... on OrgUpdateDefaultRepositoryPermissionAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberRepositoryCreationPermissionAuditEntry { canCreateRepositories organizationName visibility } ... on OrgUpdateMemberRepositoryInvitationPermissionAuditEntry { canInviteOutsideCollaboratorsToRepositories organizationName } ... on PrivateRepositoryForkingDisableAuditEntry { enterpriseSlug organizationName repositoryName } ... on PrivateRepositoryForkingEnableAuditEntry { enterpriseSlug organizationName repositoryName } ... on RepoAccessAuditEntry { organizationName repositoryName visibility } ... on RepoAddMemberAuditEntry { organizationName repositoryName visibility } ... on RepoAddTopicAuditEntry { organizationName repositoryName topicName } ... on RepoArchivedAuditEntry { organizationName repositoryName visibility } ... on RepoChangeMergeSettingAuditEntry { isEnabled mergeType organizationName repositoryName } ... on RepoConfigDisableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigDisableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigEnableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigEnableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigLockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigUnlockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoCreateAuditEntry { forkParentName forkSourceName organizationName repositoryName visibility } ... on RepoDestroyAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveMemberAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveTopicAuditEntry { organizationName repositoryName topicName } ... on RepositoryVisibilityChangeDisableAuditEntry { enterpriseSlug organizationName } ... on RepositoryVisibilityChangeEnableAuditEntry { enterpriseSlug organizationName } ... on TeamAddMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamAddRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } ... on TeamChangeParentTeamAuditEntry { organizationName parentTeamName parentTeamNameWas teamName } ... on TeamRemoveMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamRemoveRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } }"}'
            }
        }
        else {
            # no more data write last run to az storage
			$lastRunContext.org = $orgName
            $lastRunContext.lastContext = $lastRunContext.lastContext
            $lastRunContext.lastRun = $currentStartTime
            $lastRunAuditContext | ConvertTo-Json | Out-File "$env:temp\lastrun-Audit.json"
            Set-AzStorageBlobContent -Blob "lastrun-Audit.json" -Container $storageAccountContainer -Context $storageAccountContext -File "$env:temp\lastrun-Audit.json" -Force
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
            if ($referrerLogs.Length -gt 0){
                $referrerLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $referrerLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $referrerLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Referrers
                #Send to log A;
                SendToLogA -gitHubData $referrerLogs -customLogName $RepoLogTable
            }
            

            $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/popular/paths"
            $pathLogs = $null
            $pathLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            if ($pathLogs.Length -gt 0){
                $pathLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $pathLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $pathLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Paths
                #Send to log A;
                SendToLogA -gitHubData $pathLogs -customLogName $RepoLogTable
            }
            
            $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/views"
            $viewLogs = $null
            $viewLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            if ($viewLogs.Length -gt 0){
                $viewLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $viewLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $viewLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Views
                #Send to log A
                SendToLogA -gitHubData $viewLogs -customLogName $RepoLogTable
            }

            $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/clones"
            $cloneLogs = $null
            $cloneLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            if ($cloneLogs.Length -gt 0){
                $cloneLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $cloneLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $cloneLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Clones
                #Send to log A
                SendToLogA -gitHubData $cloneLogs -customLogName $RepoLogTable
            }        

            $uri = "https://api.github.com/repos/$orgName/$repoName/commits"
            $commitLogs = $null
            $commitLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            if ($commitLogs.Length -gt 0){
                $commitLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $commitLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $commitLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Commits
                #Send to log A
                SendToLogA -gitHubData $commitLogs -customLogName $RepoLogTable
            }
            
            $uri = "https://api.github.com/repos/$orgName/$repoName/collaborators"
            $collaboratorLogs = $null
            $collaboratorLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            if ($collaboratorLogs.Length -gt 0){
                $collaboratorLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $collaboratorLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $collaboratorLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Collaborators
                #Send to log A
                SendToLogA -gitHubData $collaboratorLogs -customLogName $RepoLogTable
            }        

            $uri = "https://api.github.com/repos/$orgName/$repoName/forks"
            $forkLogs = $null
            $forkLogs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            if ($forkLogs.Length -gt 0){
                $forkLogs | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $forkLogs | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $forkLogs | Add-Member -NotePropertyName LogType -NotePropertyValue Forks
                #Send to log A
                SendToLogA -gitHubData $forkLogs -customLogName $RepoLogTable
            }

			$uri = "https://api.github.com/repos/$orgName/$repoName/secret-scanning/alerts"
            $secretscanningalerts = $null
            $secretscanningalerts = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
            if ($secretscanningalerts.Length -gt 0){
                $secretscanningalerts | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
                $secretscanningalerts | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
                $secretscanningalerts | Add-Member -NotePropertyName LogType -NotePropertyValue SecretScanningAlerts
                #Send to log A
                SendToLogA -gitHubData $secretscanningalerts -customLogName $RepoLogTable
            }      
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
            Get-AzStorageBlobContent -Blob "lastrun-$orgName-$repoName.json" -Container $storageAccountContainer -Context $storageAccountContext -Destination "$env:temp\lastrun-$orgName-$repoName.json" -Force
            $lastRunVulnContext = Get-Content "$env:temp\lastrun-$orgName-$repoName.json" | ConvertFrom-Json
        }
        else {
            $lastRun = $currentStartTime
            $lastRunVuln = @"
{
"lastRun": "$lastRun",
"lastContext": ""
}
"@
            $lastRunVuln| Out-File "$env:temp\lastrun-$orgName-$repoName.json"
            $lastRunVulnContext = $lastRunVuln | ConvertFrom-Json
            Set-AzStorageBlobContent -Container $storageAccountContainer -Context $storageAccountContext -File "$env:temp\lastrun-$orgName-$repoName.json" -Force
        }

        #Build the query based on previous context or not
        $lastRunContext = $lastRunVulnContext.lastContext
        if([string]::IsNullOrEmpty($lastRunContext)){
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
                if([string]::IsNullOrEmpty($lastRunContext)){
                    $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100) { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'
                }
                else {
                    $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100, after: \"'+$lastRunContext+'\") { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'
                }
            }
            else {
                $lastRunVulnContext.lastContext = $lastRunContext
                $lastRunVulnContext.lastRun = $currentStartTime
                $lastRunVulnContext | ConvertTo-Json | Out-File "$env:temp\lastrun-$orgName-$repoName.json"
                Set-AzStorageBlobContent -Blob "lastrun-$orgName-$repoName.json" -Container $storageAccountContainer -Context $storageAccountContext -File "$env:temp\lastrun-$orgName-$repoName.json" -Force
            }
        } until ($hasNextPage -eq $false)
    }
    #clear the repo list for next org
    $repoList = @()
	#clear the temp folder
	Remove-Item $env:temp\* -Recurse -Force -ErrorAction SilentlyContinue
}