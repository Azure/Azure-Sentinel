# Exchange Environment List

```Kusto
// Title:           ESI - Exchange Configuration Environment List Generator
// Author:          Microsoft
// Version:         1.2
// Last Updated:    19/09/2022
// Comment:         
//      v1.2 : 
//          - Adding fuzzy mode to be able to have only On-Premises or Online tables
//  
// DESCRIPTION:
// This parser lists the Exchange environments found in ESI Collector configuration tables. The same parser supports Exchange On-Premises and Exchange Online.
//
// USAGE:
// 1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the query below and paste into the Logs query window. 
// 2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter the Function Name "ExchangeEnvironmentList".
// Parameters: add this parameter when creating the function.
//    1. Target, type string, default value "On-Premises"
// 3. A saved function can take 10-15 minutes to become available. You can then call the function alias from other queries.
//
//
// REFERENCE: 
// Using functions in Azure Monitor log queries: https://learn.microsoft.com/azure/azure-monitor/logs/functions
//
// LOG SAMPLES:
// This parser reads configuration records from legacy ESIExchange* tables and Azure Monitor ESIAPIExchange* tables.
//
//
// Parameters simulation
// To test the parser without saving it as a function, uncomment the variable below to simulate the parameter value.
//
// let Target = 'On-Premises';
//
// Parameters definition
let _target = iff(isnull(Target) or isempty(Target),"On-Premises",Target);
let ScalarbaseRequest = union isfuzzy=true withsource=TableName ESIAPIExchange*,ESIExchange*
    | extend Source = iff (TableName contains "Online", "Online", "On-Premises")
    | where _target == 'All' or Source == _target;
// Base Request
ScalarbaseRequest | summarize by ESIEnvironment_s | project-rename ESIEnvironment = ESIEnvironment_s
```