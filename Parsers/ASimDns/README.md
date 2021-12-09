# Advanced SIEM Information Model (ASIM) DNS parsers 

This template deploys all ASIM DNS parsers. The template is part of the Advanced SIEM Information Model (ASIM).

The Advanced SIEM Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced SIEM Information Model (ASIM)](https://aka.ms/MsASIM)
- [Microsoft Sentinel DNS normalization schema reference](https://aka.ms/ASimDnsDoc)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/ASimDnsARM)

<br>

## Parsers

The template deploys the following parsers:

- Source Agnostic parsers:
  - **ASimDns** - Use this parser when you want to query interactively your DNS logs.
  - **imDns** - Use this parser, which supports the filter parameters, when using DNS logs in your content such as detection, hunting queries or workbooks. You can also use it interactively if you want to optimize your query.
  - **vimDnsEmpty** - Empty ASIM DNS table

- Source Specific Parsers:
  - **Microsoft DNS Server**
    - Collected using the [DNS connector](https://docs.microsoft.com/azure/sentinel/data-connectors-reference#domain-name-server) and the Log Analytics Agent - ASimDnsMicrosoftOMS (regular), vimDnsMicrosoftOMS (parametrized)
    - Collected using NXlog - ASimDnsMicrosoftNXlog (regular), vimDnsMicrosoftNXlog (parameterized)
  - **Azure Firewall** - ASimDnsAzureFirewall (regular), vimDnsAzureFirewall (parameterized)
  - **Sysmon for Windows** (event 22), collected using either the Log Analytics Agent or the Azure Monitor Agent, supporting both the Event and WindowsEvent table, ASimDnsMicrosoftSysmon (regular), vimDnsMicrosoftSysmon (parametrized)
  - **Cisco Umbrella** - ASimDnsCiscoUmbrella (regular), vimDnsCiscoUmbrella (parametrized)
  - **Infoblox NIOS** - ASimDnsInfobloxNIOS (regular), vimDnsInfobloxNIOS (parametrized)
  - **GCP DNS** - ASimDnsGcp (regular), vimDnsGcp  (parametrized)
  - **Corelight Zeek DNS events** - ASimDnsCorelightZeek (regular), vimDnsCorelightZeek  (parametrized)
  - **zScaler ZIA** - AsimDnszScalerZIA (regular), vimDnszScalerZIA (parametrized) 


use regular parsers when you want to query interactively your DNS logs. Use parameterized parsers when using DNS logs in your content such as detection, hunting queries or workbooks. You can also use it interactively if you want to optimize your query. For more information see 
