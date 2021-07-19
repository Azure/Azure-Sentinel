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

<br>

Note: the template asks for the list of Infoblox computers. You can ignore this input if you do not use Infoblox.  


