id: 99d589fa-7337-40d7-91a0-c96d0c4fa437
name: Account created from non-approved sources
description: |
  'This query looks for an account being created from a domain that is not regularly seen in a tenant.
    Attackers may attempt to add accounts from these sources as a means of establishing persistant access to an environment.
    Created accounts should be investigated to confirm expected creation.
    Ref: https://docs.microsoft.com/azure/active-directory/fundamentals/security-operations-user-accounts#short-lived-accounts'
severity: Medium
requiredDataConnectors:
  - connectorId: AzureActiveDirectory
    dataTypes:
      - SigninLogs
      - AuditLogs
queryFrequency: 1d
queryPeriod: 7d
triggerOperator: gt
triggerThreshold: 0
tactics:
  - Persistence
relevantTechniques:
  - T1136.003
tags:
  - AADSecOpsGuide
query: |
  let core_domains = (SigninLogs
    | where TimeGenerated > ago(7d)
    | where ResultType == 0
    | extend domain = tolower(split(UserPrincipalName, "@")[1])
    | summarize by tostring(domain));
    let alternative_domains = (SigninLogs
    | where TimeGenerated > ago(7d)
    | where isnotempty(AlternateSignInName)
    | where ResultType == 0
    | extend domain = tolower(split(AlternateSignInName, "@")[1])
    | summarize by tostring(domain));
    AuditLogs
    | where TimeGenerated > ago(1d)
    | where OperationName =~ "Add User"
    | extend InitiatingAppName = tostring(InitiatedBy.app.displayName)
    | extend InitiatingAppServicePrincipalId = tostring(InitiatedBy.app.servicePrincipalId)
    | extend InitiatingUserPrincipalName = tostring(InitiatedBy.user.userPrincipalName)
    | extend InitiatingAadUserId = tostring(InitiatedBy.user.id)
    | extend InitiatingIpAddress = tostring(iff(isnotempty(InitiatedBy.user.ipAddress), InitiatedBy.user.ipAddress, InitiatedBy.app.ipAddress))
    | extend UserAdded = tostring(TargetResources[0].userPrincipalName)
    | extend UserAddedDomain = case(
    UserAdded has "#EXT#", tostring(split(tostring(split(UserAdded, "#EXT#")[0]), "_")[1]),
    UserAdded !has "#EXT#", tostring(split(UserAdded, "@")[1]),
    UserAdded)
    | where UserAddedDomain !in (core_domains) and UserAddedDomain !in (alternative_domains)
    | extend AddedByName = case(
    InitiatingUserPrincipalName has "#EXT#", tostring(split(tostring(split(InitiatingUserPrincipalName, "#EXT#")[0]), "_")[0]),
    InitiatingUserPrincipalName !has "#EXT#", tostring(split(InitiatingUserPrincipalName, "@")[0]),
    InitiatingUserPrincipalName)
    | extend AddedByUPNSuffix = case(
    InitiatingUserPrincipalName has "#EXT#", tostring(split(tostring(split(InitiatingUserPrincipalName, "#EXT#")[0]), "_")[1]),
    InitiatingUserPrincipalName !has "#EXT#", tostring(split(InitiatingUserPrincipalName, "@")[1]),
    InitiatingUserPrincipalName)
    | extend UserAddedName = case(
    UserAdded has "#EXT#", tostring(split(tostring(split(UserAdded, "#EXT#")[0]), "_")[0]),
    UserAdded !has "#EXT#", tostring(split(UserAdded, "@")[0]),
    UserAdded)

entityMappings:
  - entityType: Account
    fieldMappings:
      - identifier: Name
        columnName: InitiatingAppName
      - identifier: AadUserId
        columnName: InitiatingAppServicePrincipalId
  - entityType: Account
    fieldMappings:
      - identifier: FullName
        columnName: InitiatingUserPrincipalName
      - identifier: Name
        columnName: AddedByName
      - identifier: UPNSuffix
        columnName: AddedByUPNSuffix
  - entityType: Account
    fieldMappings:
      - identifier: AadUserId
        columnName: InitiatingAadUserId
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: InitiatingIpAddress
  - entityType: Account
    fieldMappings:
      - identifier: FullName
        columnName: UserAdded
      - identifier: Name
        columnName: UserAddedName
      - identifier: UPNSuffix
        columnName: UserAddedDomain
version: 1.2.1
kind: Scheduled
metadata:
    source:
        kind: Community
    author:
        name: Microsoft Security Research
    support:
        tier: Community
    categories:
        domains: [ "Security - Others", "Identity" ]
