``` kusto
// Author : Alistair Ross - MSFT
//
//Example query for AzureActivity showing how to identify activities performed by users (not service principal) and extract the domain
//
AzureActivity
// Return only those accounts which is a UPN (Local or Guest)
| where Caller matches regex @"^\w+[+.\w-]*(#EXT#@|@)([\w\-]+.)*.([a-z]{2,4}|\d+)"
//
// Add a column if the account matches a guest account
| extend IsGuest = iif(Caller matches regex @"^\w+[+.\w-]*#EXT#@([\w\-]+.)*.([a-z]{2,4}|\d+)", true, false)
//
// Extract the domain from the caller
| extend Domain = tolower(extract(@"^(\w+[+.\w-]*(#EXT#@|@))(([\w\-]+.)*.([a-z]{2,4}|\d+))",3,Caller))
// 
// This could identify activities that have been performed by a user whom isn't in a trusted domain
| join kind= leftanti (
_GetWatchlist("TrustedDomains")
| project Domain = tolower(Domain)
) on Domain
```
