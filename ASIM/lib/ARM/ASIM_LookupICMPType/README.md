# Log Analytics KQL function An ASIM function to return the ICMP type name

ARM template for deploying the Log Analytics KQL function An ASIM function to return the ICMP type name

This ASIM function returns ICMP Type name associated with the numerical value provided as a parameter. For example, for 8, the function returns "Echo" (which is the type used by the ping command).  


The Advanced SIEM Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information about Log Analytics functions refer to:

- [KQL user defined functions](https://docs.microsoft.com/azure/data-explorer/kusto/query/functions/user-defined-functions)
- [Managing user functions in Azure Monitor](https://docs.microsoft.com/azure/azure-monitor/logs/functions)

<br/>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2FLibrary%2FARM%2FASIM_LookupICMPType%2FASIM_LookupICMPType.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2FLibrary%2FARM%2FASIM_LookupICMPType%2FASIM_LookupICMPType.json)
