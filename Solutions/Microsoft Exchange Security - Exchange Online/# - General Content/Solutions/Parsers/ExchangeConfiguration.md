# Exchange Configuration Parser	

```Kusto
// Title:           ESI - Exchange Configuration Parser
// Author:          Microsoft
// Version:         1.6
// Last Updated:    13/10/2022
// Comment:  
//      v1.6 : 
//          - Change consumption of Identity_Name_S by IdentityString_s. Requires CollectExchSecIns Script version 7.5.1 minimum
//      v1.5 : 
//          - Change the usage of TimeGenerated instead of EntryDate for filtering BaseRequest.
//          - Change alllife duration to 1080 days instead of 90 days.  
//      v1.4 : 
//          - Capacity to find all configuration without date limitation with the keyword "alllife" in SpecificConfigurationDate    
//      v1.3 : 
//          - Adding fuzzy mode to be able to have only On-Premises or Online tables
//          - Simplify the request
//  
// DESCRIPTION:
// This parser takes raw ESI Exchange Configuration Collector to pivot raw information and retrieve a specific date configuration. This is the same parser for Exchange On-Premises version and Exchange online version of the solution.
//
// USAGE:
// 1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the query below and paste into the Logs query window. 
// 2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter the Function Name "ExchangeConfiguration".
// Parameters : 4 parameters to add during creation. 
//    1. SpecificSectionList, type string, default value ""
//    2. SpecificConfigurationDate, type string, default value "lastdate"
//    3. Target, type string, default value "On-Premises"
//    4. SpecificConfigurationEnv, type string, default value "All"
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
// let SpecificSectionList = '';
// let SpecificConfigurationDate = 'lastdate';
// let SpecificConfigurationEnv = 'All';
// let Target = 'On-Premises';
//
// Parameters definition
let _SpecificSectionList = split(SpecificSectionList,',');
let _configurationDate = iff(isnull(SpecificConfigurationDate) or isempty(SpecificConfigurationDate),"lastdate",tostring(SpecificConfigurationDate));
let _configurationEnv = split(iff(isnull(SpecificConfigurationEnv) or isempty(SpecificConfigurationEnv) or tolower(SpecificConfigurationEnv) == "all","All",tostring(SpecificConfigurationEnv)),',');
let _target = iff(isnull(Target) or isempty(Target),"On-Premises",Target);
// Building Base Request
let _targetDate = iff(_configurationDate == "lastdate", ago(7d), iif(_configurationDate == "alllife",ago(1080d),todatetime(_configurationDate)));
let baseRequest = materialize (union isfuzzy=true withsource=TableName ESIAPIExchange*,ESIExchange* 
    | where TimeGenerated > _targetDate
    | extend Source = iff (TableName contains "Online", "Online", "On-Premises")
    | where _target == 'All' or Source == _target
    | extend ScopedEnvironment = iff(_configurationEnv contains "All", "All",ESIEnvironment_s) 
    | where ScopedEnvironment in (_configurationEnv)
    | extend EntryDate = todatetime(EntryDate_s)
    | project-away EntryDate_s);
// Find Config Id (can be multiple id in all)
let findConfigDate = baseRequest
    | extend Env =strcat(Source, "_",ESIEnvironment_s)
    | summarize count() by GenerationInstanceID_g,Env,EntryDate
    | extend distance = iff(_configurationDate == "lastdate" or _configurationDate == "alllife", now() - EntryDate, (EntryDate - todatetime(_configurationDate)))
    | top-nested of Env by Ignore0=max(1), 
        top-nested 1 of distance by Ignore1 = min(distance) asc nulls last, 
        top-nested of GenerationInstanceID_g by Ignore2=max(2) 
    | project GenerationInstanceID_g;
// Parse Result
let ParseExchangeConfig = () { baseRequest 
 | join kind=leftsemi (findConfigDate) on $left.GenerationInstanceID_g == $right.GenerationInstanceID_g
 | where isempty(_SpecificSectionList[0]) or Section_s in (_SpecificSectionList)
 | extend TimeGenerated = EntryDate
 | extend Identity = IdentityString_s
 | extend CmdletResultValue = parse_json(rawData_s)
 | project-rename ConfigurationInstanceID = GenerationInstanceID_g, ESIEnvironment = ESIEnvironment_s, Section = Section_s, PSCmdlet = PSCmdL_s, CmdletResultType = ExecutionResult_s, WhenChanged = WhenChanged_t, WhenCreated = WhenCreated_t, Name = Name_s
 | project-away TenantId,SourceSystem,Type,EntryDate
};
ParseExchangeConfig
```