# Exchange Admin Audit Logs Parser

```Kusto
// Title:           ESI - Exchange Admin Audit Logs Parser
// Author:          Microsoft
// Version:         1.4.0
// Last Updated:    11/03/2025
// Comment:  
//      v1.4 :
//          - Update Documentation Link to new repository
//      v1.3 :
//          - Implement a VIP search in all VIP information (DisplayName, UPN, ObjectGUID ...). MESCheckVIP parser is now mandatory
//      v1.2 :
//          - The fuzzyTable need to have an objectGuid in a Guid format to be aligned with the watchlist.
//      v1.1 :
//          - Watchlist ExchangeVIP is not mandatory anymore
//      v1.0 : 
//          - Function initilisation for Sentinel Solution
//  
// DESCRIPTION:
// This parser takes raw Exchange Admin Audit Logs and add elements like ESI Environment, VIP information, sensitive information, etc...
//
// USAGE:
// 1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the query below and paste into the Logs query window. 
// 2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter the Function Name "ExchangeAdminAuditLogs".
// 3. Function App usually take 10-15 minutes to activate. You can then use Function Alias for other queries
//
// DEPENDENCY:
// This parser is linked to "ExchangeVIP" whatchlist
//
// REFERENCE: 
// Using functions in Azure monitor log queries: https://docs.microsoft.com/azure/azure-monitor/log-query/functions
//
// LOG SAMPLES:
// This parser assumes that MS Exchange Management Logs from Exchange Servers Event Logs are collected in Log Analytics.
//
//
let CmdletCheck = externaldata (Cmdlet:string, UserOriented:string, RestrictToParameter:string, Parameters:string)[h"https://raw.githubusercontent.com/Azure/Azure-Sentinel/refs/heads/master/Solutions/Microsoft%20Exchange%20Security%20-%20Exchange%20Online/%23%20-%20General%20Content/Operations/Watchlists/CmdletWatchlist.csv"]with(format="csv",ignoreFirstRecord=true);
let SensitiveCmdlets = CmdletCheck | project tostring(Cmdlet) ;
let Check = (T:(*)) {
    let fuzzyWatchlist = datatable(displayName:string, userPrincipalName:string, sAMAccountName:string, objectSID:string, objectGUID:guid, canonicalName:string, comment:string) [
        "NONE","NONE","NONE","NONE","00000001-0000-1000-0000-100000000000","NONE","NONE"];
    let Watchlist = union isfuzzy=true withsource=TableName _GetWatchlist('ExchangeVIP'), fuzzyWatchlist | where objectGUID != "00000001-0000-1000-0000-100000000000" | project-away TableName;
    let SearchUserDisplayName = T | join Watchlist on $left.TargetObject == $right.displayName | project TargetObject,SearchKey;
    let SearchUserUPN = T | join Watchlist on $left.TargetObject == $right.userPrincipalName | project TargetObject,SearchKey;
    let SearchUserCanonicalName = T | join Watchlist on $left.TargetObject == $right.canonicalName | project TargetObject,SearchKey;
    let SearchUserSAMAccountName = T | join Watchlist on $left.TargetObject == $right.sAMAccountName | project TargetObject,SearchKey;
    let SearchUserObjectSID = T | join Watchlist on $left.TargetObject == $right.objectSID | project TargetObject,SearchKey;
    let SearchUserObjectGUID = T | join (Watchlist | extend objectGuidString = tostring(objectGUID)) on $left.TargetObject == $right.objectGuidString | project TargetObject,SearchKey;
    let SearchUserDistinguishedName = T | join Watchlist on $left.TargetObject == $right.distinguishedName | project TargetObject,SearchKey;
    union isfuzzy=true withsource=TableName 
        SearchUserDisplayName, 
        SearchUserUPN, 
        SearchUserCanonicalName, 
        SearchUserSAMAccountName,
        SearchUserObjectSID,
        SearchUserObjectGUID,
        SearchUserDistinguishedName
    };
let Env = ExchangeConfiguration(SpecificSectionList="ESIEnvironment")
| extend DomainFQDN_ = tostring(CmdletResultValue.DomainFQDN)
| project DomainFQDN_, ESIEnvironment;
let EventList = Event
    | where EventLog == 'MSExchange Management'
    | where EventID in (1,6) // 1 = Success, 6 = Failure
    | parse ParameterXml with '<Param>' CmdletName '</Param><Param>' CmdletParameters '</Param><Param>' Caller '</Param><Param>' *
    | extend TargetObject = iif( CmdletParameters has "-Identity ", split(split(CmdletParameters,'-Identity ')[1],'"')[1], iif( CmdletParameters has "-Name ", split(split(CmdletParameters,'-Name ')[1],'"')[1], ""));
let MSExchange_Management = (){
   EventList
    | extend Status = case( EventID == 1, 'Success', 'Failure')
    | join kind=leftouter (EventList | project TargetObject | invoke Check()) on TargetObject
    | extend IsVIP = iif(SearchKey == "", false, true)
    | join kind=leftouter  ( 
        MESCheckVIP() ) on SearchKey
    | extend CmdletNameJoin = tolower(CmdletName)
    | join kind=leftouter  ( 
        CmdletCheck
    | extend CmdletNameJoin = tolower(Cmdlet)
    ) on CmdletNameJoin
    | extend DomainEnv = replace_string(Computer,strcat(tostring(split(Computer,'.',0)[0]),'.'),'')
    | join kind=leftouter  ( 
        Env
    ) on $left.DomainEnv == $right.DomainFQDN_
    | extend ESIEnvironment = iif (isnotempty(ESIEnvironment), ESIEnvironment, strcat("Unknown-",DomainEnv))
    | extend IsSenstiveCmdlet = iif( isnotempty(CmdletNameJoin1) , true, false) 
    | extend IsRestrictedCmdLet = iif(IsSenstiveCmdlet == true, iif( RestrictToParameter == "Yes", true, false), dynamic(null))
    | extend RestrictedParameters = iif(IsSenstiveCmdlet == true, split(tolower(Parameters),';'), dynamic(null))
    | extend ExtractedParameters = iif(IsSenstiveCmdlet == true,extract_all(@"\B(-\w+)", tolower(CmdletParameters)), dynamic(null))
    | extend IsSenstiveCmdletParameters = iif(IsSenstiveCmdlet == true,iif( array_length(set_difference(ExtractedParameters,RestrictedParameters)) == array_length(ExtractedParameters), false, true ) , false)
    | extend IsSensitive = iif( ( IsSenstiveCmdlet == true and IsRestrictedCmdLet == false ) or (IsSenstiveCmdlet == true and IsRestrictedCmdLet == true and IsSenstiveCmdletParameters == true ), true, false )
    | project TimeGenerated,Computer,Status,Caller,TargetObject,IsVIP,canonicalName,displayName,distinguishedName,objectGUID,objectSID,sAMAccountName,userPrincipalName,CmdletName,CmdletParameters,IsSenstiveCmdlet,IsRestrictedCmdLet,ExtractedParameters,RestrictedParameters,IsSenstiveCmdletParameters,IsSensitive,UserOriented, ESIEnvironment
};
MSExchange_Management
```
