# Log Analytics KQL function An ASIM function sets Hostname, Domain, DomainType and FQDN based for an FQDN or hostname provided as a parameter

ARM template for deploying the Log Analytics KQL function An ASIM function sets Hostname, Domain, DomainType and FQDN based for an FQDN or hostname provided as a parameter

This ASIM tabular function is intended for use in ASIM parsers and sets the Hostname entity fields based on an FQDN or hostname provided as a parameter. The function is invoked using the [invoke operator](https://docs.microsoft.com/azure/data-explorer/kusto/query/invokeoperator) and requires the source table to have a TimeGenerated field. The resulting fields have to be renamed to the needed final names, for example FQDN to DstFQDN.  


The Advanced SIEM Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information about Log Analytics functions refer to:

- [KQL user defined functions](https://docs.microsoft.com/azure/data-explorer/kusto/query/functions/user-defined-functions)
- [Managing user functions in Azure Monitor](https://docs.microsoft.com/azure/azure-monitor/logs/functions)

<br/>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2FLibrary%2FARM%2FASIM_ResolveFQDN%2FASIM_ResolveFQDN.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FASIM%2FLibrary%2FARM%2FASIM_ResolveFQDN%2FASIM_ResolveFQDN.json)
