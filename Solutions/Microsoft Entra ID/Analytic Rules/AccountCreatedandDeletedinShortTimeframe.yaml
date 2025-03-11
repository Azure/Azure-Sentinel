id: bb616d82-108f-47d3-9dec-9652ea0d3bf6
name: Account Created and Deleted in Short Timeframe
description: |
  'Search for user principal name (UPN) events. Look for accounts created and then deleted in under 24 hours. Attackers may create an account for their use, and then remove the account when no longer needed.
  Ref : https://docs.microsoft.com/azure/active-directory/fundamentals/security-operations-user-accounts#short-lived-account'
severity: High
requiredDataConnectors:
  - connectorId: AzureActiveDirectory
    dataTypes:
      - SigninLogs
queryFrequency: 1h
queryPeriod: 1d
triggerOperator: gt
triggerThreshold: 0
status: Available
tactics:
  - InitialAccess
relevantTechniques:
  - T1078.004
tags:
  - AADSecOpsGuide
query: |
  let queryfrequency = 1h;
  let queryperiod = 1d;
  AuditLogs
  | where TimeGenerated > ago(queryfrequency)
  | where OperationName =~ "Delete user"
  | mv-apply TargetResource = TargetResources on 
    (
        where TargetResource.type == "User"
        | extend TargetUserPrincipalName = extract(@'([a-f0-9]{32})?(.*)', 2, tostring(TargetResource.userPrincipalName))
    )
  | extend DeletedByApp = tostring(InitiatedBy.app.displayName),
  DeletedByAppServicePrincipalId = tostring(InitiatedBy.app.servicePrincipalId),
  DeletedByUserPrincipalName = tostring(InitiatedBy.user.userPrincipalName),
  DeletedByAadUserId = tostring(InitiatedBy.user.id),
  DeletedByIPAddress = tostring(InitiatedBy.user.ipAddress)
  | project Deletion_TimeGenerated = TimeGenerated, TargetUserPrincipalName, DeletedByApp, DeletedByAppServicePrincipalId, DeletedByUserPrincipalName, DeletedByAadUserId, DeletedByIPAddress, 
  Deletion_AdditionalDetails = AdditionalDetails, Deletion_InitiatedBy = InitiatedBy, Deletion_TargetResources = TargetResources
  | join kind=inner (
      AuditLogs
      | where TimeGenerated > ago(queryperiod)
      | where OperationName =~ "Add user"      
      | mv-apply TargetResource = TargetResources on 
        (
            where TargetResource.type == "User"
            | extend TargetUserPrincipalName = trim(@'"',tostring(TargetResource.userPrincipalName))
        )
      | project-rename Creation_TimeGenerated = TimeGenerated
  ) on TargetUserPrincipalName
  | extend TimeDelta = Deletion_TimeGenerated - Creation_TimeGenerated
  | where  TimeDelta between (time(0s) .. queryperiod)
  | extend CreatedByApp = tostring(InitiatedBy.app.displayName),
  CreatedByAppServicePrincipalId = tostring(InitiatedBy.app.servicePrincipalId),
  CreatedByUserPrincipalName = tostring(InitiatedBy.user.userPrincipalName),
  CreatedByAadUserId = tostring(InitiatedBy.user.id),
  CreatedByIPAddress = tostring(InitiatedBy.user.ipAddress)
  | project Creation_TimeGenerated, Deletion_TimeGenerated, TimeDelta, TargetUserPrincipalName, DeletedByApp, DeletedByAppServicePrincipalId, DeletedByUserPrincipalName, DeletedByAadUserId, DeletedByIPAddress, 
  CreatedByApp, CreatedByAppServicePrincipalId, CreatedByUserPrincipalName, CreatedByAadUserId, CreatedByIPAddress, Creation_AdditionalDetails = AdditionalDetails, Creation_InitiatedBy = InitiatedBy, Creation_TargetResources = TargetResources, Deletion_AdditionalDetails, Deletion_InitiatedBy, Deletion_TargetResources
  | extend TargetName = tostring(split(TargetUserPrincipalName,'@',0)[0]), TargetUPNSuffix = tostring(split(TargetUserPrincipalName,'@',1)[0])
  | extend CreatedByName = tostring(split(CreatedByUserPrincipalName,'@',0)[0]), CreatedByUPNSuffix = tostring(split(CreatedByUserPrincipalName,'@',1)[0])
  | extend DeletedByName = tostring(split(DeletedByUserPrincipalName,'@',0)[0]), DeletedByUPNSuffix = tostring(split(DeletedByUserPrincipalName,'@',1)[0])
entityMappings:
  - entityType: Account
    fieldMappings:
      - identifier: FullName
        columnName: TargetUserPrincipalName
      - identifier: Name
        columnName: TargetName
      - identifier: UPNSuffix
        columnName: TargetUPNSuffix
  - entityType: Account
    fieldMappings:
      - identifier: FullName
        columnName: CreatedByUserPrincipalName
      - identifier: Name
        columnName: CreatedByName
      - identifier: UPNSuffix
        columnName: CreatedByUPNSuffix
  - entityType: Account
    fieldMappings:
      - identifier: AadUserId
        columnName: CreatedByAadUserId
  - entityType: Account
    fieldMappings:
      - identifier: FullName
        columnName: DeletedByUserPrincipalName
      - identifier: Name
        columnName: DeletedByName
      - identifier: UPNSuffix
        columnName: DeletedByUPNSuffix
  - entityType: Account
    fieldMappings:
      - identifier: AadUserId
        columnName: DeletedByAadUserId
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: CreatedByIPAddress
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: DeletedByIPAddress
version: 1.1.0
kind: Scheduled
