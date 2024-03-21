# Microsoft Exchange Security - Parsers information

Microsoft Exchange Security solutions use multiple parsers to be able to process correctly the raw data. Those parsers are used to create multiple workbooks, multiple analytic rules but parsers are also here to allow you to format correctly raw data to be used in your own queries.

Parsers are created [using functions in Azure monitor log queries](https://docs.microsoft.com/azure/azure-monitor/log-query/functions)

- [Microsoft Exchange Security - Parsers information](#microsoft-exchange-security---parsers-information)
  - [ExchangeConfiguration Parser](#exchangeconfiguration-parser)
    - [Parser Definition](#parser-definition)
    - [Parser Description](#parser-description)
    - [Parser Setup](#parser-setup)
    - [Linked tables](#linked-tables)
    - [Parameters simulation](#parameters-simulation)
  - [Exchange Configuration Environment List Parser](#exchange-configuration-environment-list-parser)
    - [Parser Definition](#parser-definition-1)
    - [Parser Description](#parser-description-1)
    - [Parser Setup](#parser-setup-1)
    - [Linked tables](#linked-tables-1)
    - [Parameters simulation](#parameters-simulation-1)
  - [Microsoft Exchange Security Check VIP Parser](#microsoft-exchange-security-check-vip-parser)
    - [Parser Definition](#parser-definition-2)
    - [Parser Description](#parser-description-2)
    - [Parser dependency](#parser-dependency)
    - [Parser Setup](#parser-setup-2)

## ExchangeConfiguration Parser

### Parser Definition

- Title:           ESI - Exchange Configuration Parser
- Version:         1.6.1
- Last Updated:    19/12/2023

|**Version**  |**Details**  |
|---------|-----------------------------------------------------------------------------------------------------------------------|
|v1.6.1    | <ul><li>Adding version in comment of the Parser</li></ul>  |
|v1.6     | <ul><li>Change consumption of Identity_Name_S by IdentityString_s. Requires CollectExchSecIns Script version 7.5.1 minimum</li></ul>  |
|v1.5     | <ul><li>Change the usage of TimeGenerated instead of EntryDate for filtering BaseRequest.</li><li>Change alllife duration to 1080 days instead of 90 days. </li></ul>       |
|v1.4     | <ul><li>Capacity to find all configuration without date limitation with the keyword "alllife" in SpecificConfigurationDate</li></ul>   |
|v1.3     | <ul><li>Adding fuzzy mode to be able to have only On-Premises or Online tables</li><li>Simplify the request</li></ul> |

### Parser Description

This parser takes raw ESI Exchange Configuration Collector to pivot raw information and retrieve a specific date configuration. This is the same parser for Exchange On-Premises version and Exchange online version of the solution.

### Parser Setup

 1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the query below and paste into the Logs query window.
 2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter the Function Name "ExchangeConfiguration".

>#### **Parameters:**
>
>4 parameters to add during creation.
>
> 1. SpecificSectionList, type string, default value ""
> 2. SpecificConfigurationDate, type string, default value "lastdate"
> 3. Target, type string, default value "On-Premises"
> 4. SpecificConfigurationEnv, type string, default value "All"

 3. Function App usually take 10-15 minutes to activate. You can then use Function Alias for other queries

### Linked tables

This parser assumes the raw log from the ESI Exchange Collector are on the ESIExchangeConfig_CL and/or ESIExchangeOnlineConfig_CL tables and are uploaded using the builtin REST API uploader of the Collector.

### Parameters simulation

If you need to test the parser execution without saving it as a function, add the bellow variable to simulate parameters values at the beginning.


```
let SpecificSectionList = '';
let SpecificConfigurationDate = 'lastdate';
let SpecificConfigurationEnv = 'All';
let Target = 'On-Premises';`
```

## Exchange Configuration Environment List Parser

### Parser Definition

- Title:           Exchange Configuration Environment List Generator
- Version:         1.2
- Last Updated:    19/09/2022

|**Version**  |**Details**  |
|---------|-----------------------------------------------------------------------------------------------------------------------|
|v1.2     | <ul><li>Adding fuzzy mode to be able to have only On-Premises or Online tables</li></ul> |

### Parser Description

This parser takes raw ESI Exchange Configuration Collector to list Exchange Environments that are loaded in the tables. This is the same parser for Exchange On-Premises version and Exchange online version of the solution.

### Parser Setup

 1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the query below and paste into the Logs query window.
 2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter the Function Name "ExchangeEnvironmentList".

>#### **Parameters:**
>
>1 parameter to add during creation : Target, type string, default value "On-Premises"

 3. Function App usually take 10-15 minutes to activate. You can then use Function Alias for other queries

### Linked tables

This parser assumes the raw log from the ESI Exchange Collector are on the ESIExchangeConfig_CL and/or ESIExchangeOnlineConfig_CL tables and are uploaded using the builtin REST API uploader of the Collector.

### Parameters simulation

If you need to test the parser execution without saving it as a function, add the bellow variable to simulate parameters values at the beginning.


```
let Target = 'On-Premises';
```

## Microsoft Exchange Security Check VIP Parser

### Parser Definition

- Title:           Microsoft Exchange Security Check VIP (MESCheckVIP) Parser
- Version:         1.0.0
- Last Updated:    01/11/2023

|**Version**  |**Details**  |
|---------|-----------------------------------------------------------------------------------------------------------------------|
|v1.0     | <ul><li>Function initilisation for Sentinel Solution</li></ul> |

### Parser Description

This parser verify if a user (by Display name, UPN, Canonical name, alias, SamAccountName, DN) is a VIP in ExchangeVIP Whatchlist or not.

### Parser dependency

This parser is linked to "ExchangeVIP" whatchlist

### Parser Setup

 1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the query below and paste into the Logs query window.
 2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter the Function Name "MESCheckVIP".

>#### **Parameters:**
>
>1 parameter to add during creation : UserToCheck, type string, default value "All"
 
 1. Function App usually take 10-15 minutes to activate. You can then use Function Alias for other queries