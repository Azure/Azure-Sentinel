# Azure Sentinel Information Model (ASIM) DNS parsers 

This template deploys all ASIM DNS parsers. The template is part of the Azure Sentinel Information Mode (ASIM).

The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

For more information, see:

- [Normalization and the Azure Sentinel Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)
- [Azure Sentinel DNS normalization schema reference](https://aka.ms/AzSentinelDnsDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelDnsARM)

<br>

## Parsers

The template deploys the following parsers:

- Source Agnostic parsers:
  - **ASimDns** - Use this parser when you want to query interactively your DNS logs.
  - **imDns** - Use this parser, which supports the optimization parameters desribed below, when using DNS logs in your content such as detection, hunting queries or workbooks. You can also use it interactively if you want to optimize your query 
  - **vimDnsEmpty** - Emtpy ASIM DNS table

- Source Specific Parsers:
  - **Microsoft DNS Server**, collected using the Log Analytics Agent - ASimDnsMicrosoftOMS (regular), vimDnsMicrosoftOMS (parametrized)
  - **Cisco Umbrella** - ASimDnsCiscoUmbrella (regular), vimDnsCiscoUmbrella (parametrized)
  - **Infoblox NIOS** - ASimDnsInfobloxNIOS (regular), vimDnsInfobloxNIOS (parametrized)
  - **GCP DNS** - ASimDnsGcp (regular), vimDnsGcp  (parametrized)
  - **Corelight Zeek DNS events** - ASimDnsCorelightZeek (regular), vimDnsCorelightZeek  (parametrized)
  - **Sysmon for Windows** (event 22), collected using either the Log Analytics Agent or the Azure Monitor Agent, supporting both the Event and WindowsEvent table, ASimDnsMicrosoftSysmon (regular), vimDnsMicrosoftSysmon (parametrized)

use regular parsers when you want to query interactively your DNS logs. Use parameterized parsers when using DNS logs in your content such as detection, hunting queries or workbooks. You can also use it interactively if you want to optimize your query

## Parser parameters

Parametersize parsers support the following parameters which allow for pre-filtering and therefore significantly enhance parser perofrmance. All parameters are optional. The results will match all of the used parameters (AND logic).

To use parameters, set their value as you invoke the parser, for example

`imDns (srcipaddr = '192.168.0.1') | ...`

Supported parameters: 

| Name     | Type      | Default value |
|----------|-----------|---------------|
| starttime|  datetime | datetime(null)|
|  endtime |  datetime | datetime(null) |
|  srcipaddr |  string | '*' |
|  domain_has_any|  dynamic | dynamic([]) |
|  responsecodename |  string | '*' |
|  response_has_ipv4 |  string | '*' |
|  response_has_any|  dynamic| dynamic([])|
|  eventtype|  string | 'lookup' |


Note: the template asks for the list of Infoblox computers. You can ignore this input if you do not use Infoblox.  

<br>

## Version History

<br>

| Version | Date | Notes |
|---------|-----------|------|
| 0.1.0 | June 2021 | Initial release |
| 0.1.1 | July 2021 | Update to better align with OSSEM. The following field names where changed and the original left as an alias:<br> - Query -> DnsQuery<br> - QueryType -> DnsQueryType<br> - QueryTypeName -> DnsQueryTypeName<br> - ResponseName -> DnsResponseName<br> - ResponseCodeName -> DnsResponseCodeName<br> - ResponseCode -> DnsResponseCode<br> - QueryClass -> DnsQueryClass<br> - QueryClassName -> DnsQueryClassName<br> - Flags -> DnsFlags |
| 0.2.0 | September 2021 | Added support for parametrized parsers |

