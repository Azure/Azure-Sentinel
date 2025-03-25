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
// This parser takes raw ESI Exchange Configuration Collector to list Exchange Environments that are loaded in the tables. This is the same parser for Exchange On-Premises version and Exchange online version of the solution.
//
// USAGE:
// 1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the query below and paste into the Logs query window. 
// 2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter the Function Name "ExchangeEnvironmentList".
// Parameters : 1 parameter to add during creation. 
//    1. Target, type string, default value "On-Premises"
// 3. Function App usually take 10-15 minutes to activate. You can then use Function Alias for other queries
//
//
// REFERENCE: 
// Using functions in Azure monitor log queries: https://docs.microsoft.com/azure/azure-monitor/log-query/functions
//
// LOG SAMPLES:
// This parser assumes the raw log from the ESI Exchange Collector are on the ESIExchangeConfig_CL and/or ESIExchangeOnlineConfig_CL tables and are uploaded using the builtin REST API uploader of the Collector.
//
//
// Parameters simulation
// If you need to test the parser execution without saving it as a function, uncomment the bellow variable to simulate parameters values.
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