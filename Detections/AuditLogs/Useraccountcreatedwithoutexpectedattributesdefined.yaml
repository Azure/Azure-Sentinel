id: dc99e38c-f4e9-4837-94d7-353ac0b01a77
name: User account created without expected attributes defined
description: |
  'This query looks for accounts being created that do not have attributes populated that are commonly populated in the tenant.
    Attackers may attempt to add accounts as a means of establishing persistant access to an environment, looking for anomalies in created accounts may help identify illegitimately created accounts.
    Created accounts should be investigated to ensure they were legitimated created.
    Ref: https://docs.microsoft.com/azure/active-directory/fundamentals/security-operations-user-accounts#accounts-not-following-naming-policies'
severity: Low
requiredDataConnectors:
  - connectorId: AzureActiveDirectory
    dataTypes:
      - AuditLogs
queryFrequency: 1d
queryPeriod: 1d
triggerOperator: gt
triggerThreshold: 0
tactics:
  - Persistence
relevantTechniques:
  - T1136.003
tags:
  - AADSecOpsGuide
query: |
    let threshold = 10;
    let default_ad_attributes = dynamic(["LastDirSyncTime", "StsRefreshTokensValidFrom", "Included Updated Properties", "AccountEnabled", "Action Client Name", "SourceAnchor"]);
    let addUsers = AuditLogs
    | where OperationName =~ "Add user"
    | where Result =~ "success"
    | extend AccountProperties = TargetResources[0].modifiedProperties
    | mv-expand AccountProperties
    ;
    addUsers
    | evaluate bag_unpack(AccountProperties) : (displayName:string, oldValue: string, newValue: string , TenantId : string, SourceSystem : string, TimeGenerated : datetime, ResourceId : string, OperationName : string, OperationVersion : string, Category : string, ResultType : string, ResultSignature : string, ResultDescription : string, DurationMs : long, CorrelationId : string, Resource : string, ResourceGroup : string, ResourceProvider : string, Identity : string, Level : string, Location : string, AdditionalDetails : dynamic, Id : string, InitiatedBy : dynamic, LoggedByService : string, Result : string, ResultReason : string, TargetResources : dynamic, AADTenantId : string, ActivityDisplayName : string, ActivityDateTime : datetime, AADOperationType : string, Type : string)
    | extend displayName = column_ifexists("displayName", "Unknown Value")
    | summarize count() by displayName, TenantId
    | where displayName !in (default_ad_attributes)
    | top threshold by count_ desc
    | summarize make_set(displayName) by TenantId
    | join kind=inner (
    addUsers
    | extend CreatingUserPrincipalName = tostring(parse_json(tostring(InitiatedBy.user)).userPrincipalName)
    | extend CreatingAadUserId = tostring(InitiatedBy.user.id)
    | extend CreatingUserIPAddress = tostring(InitiatedBy.user.ipAddress)
    | extend CreatedUserPrincipalName = tostring(TargetResources[0].userPrincipalName)
    | extend PropName = tostring(AccountProperties.displayName)) 
    on TenantId
    | summarize makeset(PropName) by TimeGenerated, CorrelationId, CreatedUserPrincipalName, CreatingUserPrincipalName, CreatingAadUserId, CreatingUserIPAddress, tostring(set_displayName)
    | extend missing_props = set_difference(todynamic(set_displayName), set_PropName)
    | where array_length(missing_props) > 0
    | join kind=innerunique (
    AuditLogs
    | where Result =~ "success"
    | where OperationName =~ "Add user"
    | extend CreatedUserPrincipalName = tostring(TargetResources[0].userPrincipalName)) 
    on CorrelationId, CreatedUserPrincipalName
    | extend ExpectedProperties = set_displayName
    | project-away set_displayName, set_PropName
    | extend InitiatingAccountName = tostring(split(CreatingUserPrincipalName, "@")[0]), InitiatingAccountUPNSuffix = tostring(split(CreatingUserPrincipalName, "@")[1])
    | extend TargetAccountName = tostring(split(CreatedUserPrincipalName, "@")[0]), TargetAccountUPNSuffix = tostring(split(CreatedUserPrincipalName, "@")[1])
entityMappings:
  - entityType: Account
    fieldMappings:
      - identifier: FullName
        columnName: CreatingUserPrincipalName
      - identifier: Name
        columnName: InitiatingAccountName
      - identifier: UPNSuffix
        columnName: InitiatingAccountUPNSuffix
  - entityType: Account
    fieldMappings:
      - identifier: AadUserId
        columnName: CreatingAadUserId
  - entityType: Account
    fieldMappings:
      - identifier: FullName
        columnName: CreatedUserPrincipalName
      - identifier: Name
        columnName: TargetAccountName
      - identifier: UPNSuffix
        columnName: TargetAccountUPNSuffix
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: CreatingUserIPAddress
version: 1.1.0
kind: Scheduled
metadata:
    source:
        kind: Community
    author:
        name: Microsoft Security Research
    support:
        tier: Community
    categories:
        domains: [ "Security - Others" ]
