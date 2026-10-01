# MESCheckVIP

```Kusto
// Title:           ESI - Check VIP Parser
// Author:          Microsoft
// Version:         1.0.0
// Last Updated:    01/11/2023
// Comment:  
//      v1.0 : 
//          - Function initialization for the Microsoft Sentinel solution
//  
// DESCRIPTION:
// This parser determines whether a user is listed as a VIP for the Microsoft Exchange Security solution.
//
// USAGE:
// 1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the query below and paste into the Logs query window. 
// 2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter the Function Name "MESCheckVIP".
// Parameters: add this parameter when creating the function.
//    1. UserToCheck, type string, default value "All"
// 3. A saved function can take 10-15 minutes to become available. You can then call the function alias from other queries.
//
// DEPENDENCY:
// This parser uses the "ExchangeVIP" watchlist when it is available.
//
// REFERENCE: 
// Using functions in Azure Monitor log queries: https://learn.microsoft.com/azure/azure-monitor/logs/functions
//
// LOG SAMPLES:
// This parser assumes that ExchangeVIP Watchlist is created (but works without the watchlist, returning an empty table)
//
//
// Parameters simulation
// To test the parser without saving it as a function, uncomment the variable below to simulate the parameter value.
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
