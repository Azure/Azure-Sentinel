# MESCheckVIP

```Kusto
// Title:           ESI - Check VIP Parser
// Author:          Microsoft
// Version:         1.0.0
// Last Updated:    01/11/2023
// Comment:  
//      v1.0 : 
//          - Function initilisation for Sentinel Solution
//  
// DESCRIPTION:
// This parser could be used to find if a user is a VIP on Microsoft Exchange Security solution.
//
// USAGE:
// 1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the query below and paste into the Logs query window. 
// 2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter the Function Name "MESCheckVIP".
// Parameters : 1 parameter to add during creation. 
//    1. UserToCheck, type string, default value "All"
// 3. Function App usually take 10-15 minutes to activate. You can then use Function Alias for other queries
//
// DEPENDENCY:
// This parser is linked to "ExchangeVIP" whatchlist
//
// REFERENCE: 
// Using functions in Azure monitor log queries: https://docs.microsoft.com/azure/azure-monitor/log-query/functions
//
// LOG SAMPLES:
// This parser assumes that ExchangeVIP Watchlist is created (but works without the watchlist, returning an empty table)
//
//
// Parameters simulation
// If you need to test the parser execution without saving it as a function, uncomment the bellow variable to simulate parameters values.
//
//let UserToCheck = "SampleEntry";
//
let _UserToCheck = iif(UserToCheck == "" or UserToCheck == "All","All",tolower(UserToCheck));
let fuzzyWatchlist = datatable(userPrincipalName:string, sAMAccountName:string, objectSID:string, objectGUID:guid, canonicalName:string, comment:string) [
    "NONE","NONE","NONE","00000001-0000-1000-0000-100000000000","NONE","NONE"];
let Watchlist = union isfuzzy=true withsource=TableName _GetWatchlist('ExchangeVIP'), fuzzyWatchlist | where objectGUID != "00000001-0000-1000-0000-100000000000" | project-away TableName;
let SearchUser = Watchlist | where _UserToCheck =~ canonicalName 
    or _UserToCheck =~ displayName 
    or _UserToCheck =~ userPrincipalName 
    or _UserToCheck =~ sAMAccountName 
    or _UserToCheck =~ objectSID 
    or _UserToCheck =~ objectGUID 
    or _UserToCheck =~ distinguishedName
    or _UserToCheck == "All"
    | extend ValueChecked = iif(_UserToCheck=="All",strcat("#",displayName,"#",userPrincipalName,"#",sAMAccountName,"#",objectGUID,"#",objectSID,"#",distinguishedName,"#"),_UserToCheck);
SearchUser
```
