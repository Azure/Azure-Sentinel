# Azure Sentinel Information Model (ASIM) DNS parsers 

This template deploys all ASIM DNS parsers. The template is part of the Azure Sentinel Information Mode (ASIM).

The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

For more information, see:

- [Normalization and the Azure Sentinel Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)
- [Azure Sentinel DNS normalization schema reference](https://aka.ms/AzSentinelDnsDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelDnsARM)

<br>

The template deploys the following:
* imDns - DNS events from all normalized DNS providers
* vimDnsMicrosoft - DNS Events from Microsoft OMS
* vimDnsCisco - DNS Events from Cisco Umbrella
* vimDnsInfoblox - DNS Events from Infoblox NIOS 
* vimDnsEmpty - Emtpy ASIM DNS table

Note: the template asks for the list of Infoblox computers. You can ignore this input if you do not use Infoblox.  

<br>

## Version History

<br>

| Version | Date | Notes |
|---------|-----------|------|
| 0.1.0 | June 2021 | Initial release |
| 0.1.1 | July 2021 | Update to better align with OSSEM. The following field names where changed and the original left as an alias:<br> - Query -> DnsQuery<br> - QueryType -> DnsQueryType<br> - QueryTypeName -> DnsQueryTypeName<br> - ResponseName -> DnsResponseName<br> - ResponseCodeName -> DnsResponseCodeName<br> - ResponseCode -> DnsResponseCode<br> - QueryClass -> DnsQueryClass<br> - QueryClassName -> DnsQueryClassName<br> - Flags -> DnsFlags |

