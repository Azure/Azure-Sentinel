# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"


# Main
if ($env:MSI_SECRET -and (Get-Module -ListAvailable Az.Accounts)){
    Connect-AzAccount -Identity
}

#need to convert these to use $env variables in function
$storageAccountName = ""
$storageAccountKey = ""
$StorageAccountContainer = ""
$personalAccessToken = ""
$currentStartTime = (get-date).ToUniversalTime() | get-date  -Format yyyy-MM-ddTHH:mm:ss:ffffffZ

# header for API calls
$headers = @{
    Authorization = "bearer $personalAccessToken"
    'Content-Type' = "application/json"
}

#Get Orgs from ORGS.json in Az Storage
#change tmpdir to $env:HOME\Data\
# MAC is env:TMPDIR but in az function they say to use env:HOME\Data\
$storageAccountContext = New-AzStorageContext -StorageAccountName $storageAccountName -StorageAccountKey $storageAccountKey
$checkBlob = Get-AzStorageBlob -Blob ORGS.json -Container $StorageAccountContainer -Context $storageAccountContext
if($checkBlob -ne $null){
    Get-AzStorageBlobContent -Blob ORGS.json -Container $StorageAccountContainer -Context $storageAccountContext -Destination $env:TMPDIR\orgs.json -Force
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
    $checkBlob = Get-AzStorageBlob -Blob "lastrun-Audit.json" -Container $StorageAccountContainer -Context $storageAccountContext
    if($checkBlob -ne $null){
        #Blob found get data
        Get-AzStorageBlobContent -Blob "lastrun-Audit.json" -Container $StorageAccountContainer -Context $storageAccountContext -Destination "$env:TMPDIR\lastrun-Audit.json" -Force
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

    #Build the query based on previous lastruncontext or not
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
        $results = Invoke-RestMethod -Method Post -Uri $uri -Body $AuditQuery -Headers $headers
        if(($results.data.organization.auditLog.edges).Count -ne 0){
            #write to log a to be added later
        }
        $hasNextPage = $results.data.organization.auditLog.pageInfo.hasNextPage
        $lastRunContext = $results.data.organization.auditLog.pageInfo.endCursor
        if($hasNextPage -ne $false){
            # if there is more data update the query with endcursor to use
            $AuditQuery = '{"query": "query { organization(login: \"'+$orgName+'\") { auditLog(first: 100 orderBy: { direction: ASC field: CREATED_AT } after: \"'+$lastRunContext+'\") { edges { node { ... on AuditEntry { action actor actorIp actorLocation { city country countryCode region regionCode } actorLogin actorResourcePath actorUrl createdAt operationType user { email } userLogin userResourcePath } ... on MembersCanDeleteReposClearAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposDisableAuditEntry { organizationName enterpriseSlug } ... on MembersCanDeleteReposEnableAuditEntry { organizationName enterpriseSlug } ... on OauthApplicationCreateAuditEntry { applicationUrl oauthApplicationName organizationName state } ... on OrgAddBillingManagerAuditEntry { invitationEmail organizationName } ... on OrgAddMemberAuditEntry { organizationName permission } ... on OrgBlockUserAuditEntry { organizationName blockedUserName } ... on OrgConfigDisableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgConfigEnableCollaboratorsOnlyAuditEntry { organizationName } ... on OrgCreateAuditEntry { organizationName } ... on OrgDisableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgDisableSamlAuditEntry { organizationName } ... on OrgDisableTwoFactorRequirementAuditEntry { organizationName } ... on OrgEnableOauthAppRestrictionsAuditEntry { organizationName } ... on OrgEnableSamlAuditEntry { organizationName } ... on OrgEnableTwoFactorRequirementAuditEntry { organizationName } ... on OrgInviteMemberAuditEntry { email organizationName } ... on OrgInviteToBusinessAuditEntry { organizationName enterpriseSlug } ... on OrgOauthAppAccessApprovedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessDeniedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgOauthAppAccessRequestedAuditEntry { oauthApplicationName oauthApplicationUrl organizationName } ... on OrgRemoveBillingManagerAuditEntry { organizationName reason } ... on OrgRemoveMemberAuditEntry { organizationName membershipTypes reason } ... on OrgRemoveOutsideCollaboratorAuditEntry { organizationName membershipTypes reason } ... on OrgRestoreMemberAuditEntry { organizationName restoredMembershipsCount restoredRepositoriesCount restoredMemberships { ... on OrgRestoreMemberMembershipOrganizationAuditEntryData { organizationName } ... on OrgRestoreMemberMembershipRepositoryAuditEntryData { repositoryName } ... on OrgRestoreMemberMembershipTeamAuditEntryData { teamName } } } ... on OrgUnblockUserAuditEntry { blockedUserName organizationName } ... on OrgUpdateDefaultRepositoryPermissionAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberAuditEntry { organizationName permission permissionWas } ... on OrgUpdateMemberRepositoryCreationPermissionAuditEntry { canCreateRepositories organizationName visibility } ... on OrgUpdateMemberRepositoryInvitationPermissionAuditEntry { canInviteOutsideCollaboratorsToRepositories organizationName } ... on PrivateRepositoryForkingDisableAuditEntry { enterpriseSlug organizationName repositoryName } ... on PrivateRepositoryForkingEnableAuditEntry { enterpriseSlug organizationName repositoryName } ... on RepoAccessAuditEntry { organizationName repositoryName visibility } ... on RepoAddMemberAuditEntry { organizationName repositoryName visibility } ... on RepoAddTopicAuditEntry { organizationName repositoryName topicName } ... on RepoArchivedAuditEntry { organizationName repositoryName visibility } ... on RepoChangeMergeSettingAuditEntry { isEnabled mergeType organizationName repositoryName } ... on RepoConfigDisableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigDisableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigDisableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigEnableAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigEnableCollaboratorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableContributorsOnlyAuditEntry { organizationName repositoryName } ... on RepoConfigEnableSockpuppetDisallowedAuditEntry { organizationName repositoryName } ... on RepoConfigLockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoConfigUnlockAnonymousGitAccessAuditEntry { organizationName repositoryName } ... on RepoCreateAuditEntry { forkParentName forkSourceName organizationName repositoryName visibility } ... on RepoDestroyAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveMemberAuditEntry { organizationName repositoryName visibility } ... on RepoRemoveTopicAuditEntry { organizationName repositoryName topicName } ... on RepositoryVisibilityChangeDisableAuditEntry { enterpriseSlug organizationName } ... on RepositoryVisibilityChangeEnableAuditEntry { enterpriseSlug organizationName } ... on TeamAddMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamAddRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } ... on TeamChangeParentTeamAuditEntry { organizationName parentTeamName parentTeamNameWas teamName } ... on TeamRemoveMemberAuditEntry { isLdapMapped organizationName teamName } ... on TeamRemoveRepositoryAuditEntry { isLdapMapped organizationName repositoryName teamName } } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } }"}'
        }
        else {
            # no more data write last run to az storage
            $lastRunAuditContext.lastContext = $lastRunContext
            $lastRunAuditContext.lastRun = $currentStartTime
            $lastRunAuditContext | ConvertTo-Json | Out-File "$env:TMPDIR\lastrun-Audit.json"
            Set-AzStorageBlobContent -Blob "lastrun-Audit.json" -Container $StorageAccountContainer -Context $storageAccountContext -File "$env:TMPDIR\lastrun-Audit.json" -Force
        }
    } until ($hasNextPage -eq $false)
    $uri = $null
    $results = $null
    
    #get Org repos
    $hasMoreRepos = $true
    $pageNumber = 1
    do {
        $uri = "https://api.github.com/orgs/$orgName/repos?page=$pageNumber"
        $results = Invoke-RestMethod -Method GET -Uri $uri
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
        Write-Host "Starting to process ORG: $orgName Repo: $repoName"

        $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/popular/referrers"
        $results = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        $results | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
        $results | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
        $results | Add-Member -NotePropertyName LogType -NotePropertyValue Referrers
        #Send to log A

        $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/popular/paths"
        $results = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        $results | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
        $results | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
        $results | Add-Member -NotePropertyName LogType -NotePropertyValue Paths
        #Send to log A

        $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/popular/views"
        $results = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        $results | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
        $results | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
        $results | Add-Member -NotePropertyName LogType -NotePropertyValue Views
        #Send to log A

        $uri = "https://api.github.com/repos/$orgName/$repoName/traffic/popular/clones"
        $results = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        $results | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
        $results | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
        $results | Add-Member -NotePropertyName LogType -NotePropertyValue Clones
        #Send to log A

        $uri = "https://api.github.com/repos/$orgName/$repoName/commits"
        $results = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        $results | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
        $results | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
        $results | Add-Member -NotePropertyName LogType -NotePropertyValue Commits
        #Send to log A

        $uri = "https://api.github.com/repos/$orgName/$repoName/collaborators"
        $results = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        $results | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
        $results | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
        $results | Add-Member -NotePropertyName LogType -NotePropertyValue Collaborators
        #Send to log A

        $uri = "https://api.github.com/repos/$orgName/$repoName/forks"
        $results = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
        $results | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
        $results | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
        $results | Add-Member -NotePropertyName LogType -NotePropertyValue Forks
        #Send to log A
    }
    
    # get blobs for last run
    $blobs = Get-AzStorageBlob -Context $storageAccountContext -Container $StorageAccountContainer
    if($blobs.Name -contains "lastrun-$orgName-$reppName.json"){
        Get-AzStorageBlobContent -Blob "lastrun-$orgName-$repoName.json" -Container $StorageAccountContainer -Context $storageAccountContext -Destination "$env:TMPDIR\lastrun-$orgName-$repoName.json" -Force
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
        Set-AzStorageBlobContent -Container $StorageAccountContainer -Context $storageAccountContext -File "$env:TMPDIR\lastrun-$orgName-$repoName.json" -Force
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
    do {
        $uri = "https://api.github.com/graphql"
        $results = Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body $VulnQuery
        if(($results.data.organization.repository.vulnerabilityAlerts.nodes).Count -ne 0){
            $vulnList += $results.data.organization.repository.vulnerabilityAlerts.nodes
            $vulnList | Add-Member -NotePropertyName OrgName -NotePropertyValue $orgName
            $vulnList | Add-Member -NotePropertyName Repository -NotePropertyValue $repoName
            $vulnList | Add-Member -NotePropertyName LogType -NotePropertyValue vulnerabilityAlerts
            #send to log A
        }
        $hasNextPage = $results.data.organization.repository.vulnerabilityAlerts.pageInfo.hasNextPage
        $lastRunContext = $results.data.organization.repository.vulnerabilityAlerts.pageInfo.endCursor
        if($hasNextPage -ne $false){
            $VulnQuery = '{"query": "query {organization(login: \"'+$orgName+'\") {repository(name: \"'+$repoName+'\") { vulnerabilityAlerts(first: 100, after: \"'+$lastRunContext+'\") { nodes { createdAt dismissReason dismissedAt id vulnerableManifestFilename vulnerableManifestPath vulnerableRequirements securityAdvisory { databaseId description ghsaId id origin permalink publishedAt severity summary withdrawnAt } } pageInfo { endCursor hasNextPage hasPreviousPage startCursor } } } } }"}'            
        }
        else {
            $lastRunVulnContext.lastContext = $lastRunContext
            $lastRunVulnContext.lastRun = $currentStartTime
            $lastRunVulnContext | ConvertTo-Json | Out-File "$env:TMPDIR\lastrun-$orgName-$repoName.json"
            Set-AzStorageBlobContent -Blob "lastrun-$orgName-$repoName.json" -Container $StorageAccountContainer -Context $storageAccountContext -File "$env:TMPDIR\lastrun-Audit.json" -Force
        }
    } until ($hasNextPage -eq $false)
    
    #clear the repo list for next org
    $repoList = @()
}
