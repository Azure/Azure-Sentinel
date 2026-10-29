# Zscaler Private Access ASIM Authentication Normalization Parser

ARM template for ASIM Authentication schema parser for Zscaler Private Access.

This ASIM filtering parser normalizes Zscaler Private Access (ZPA) User Activity logs, ingested into the ZPA_CL custom table, to the ASIM Authentication schema.
The parser handles ZPN_STATUS_AUTHENTICATED, ZPN_STATUS_AUTH_FAILED and ZPN_STATUS_DISCONNECTED sessions and supports the standard Authentication filtering parameters.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM Authentication normalization schema reference](https://aka.ms/ASimAuthenticationDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/CHANGELOG/vimAuthenticationZscalerZPA.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuthentication%2FARM%2FvimAuthenticationZscalerZPA%2FvimAuthenticationZscalerZPA.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuthentication%2FARM%2FvimAuthenticationZscalerZPA%2FvimAuthenticationZscalerZPA.json)
