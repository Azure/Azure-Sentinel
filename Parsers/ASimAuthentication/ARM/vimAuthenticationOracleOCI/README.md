# Oracle Cloud Infrastructure ASIM Authentication Normalization Parser

ARM template for ASIM Authentication schema parser for Oracle Cloud Infrastructure.

This ASIM filtering parser supports normalizing and filtering Oracle Cloud Infrastructure (OCI) authentication events, stored in the OCI_LogsV2_CL table, to the ASIM Authentication schema.
Covers FederatedLoginRequest, ReceiveSamlSpSsoResponse, SentSamlIdpSsoResponse, InteractiveLogin, AuthenticationUser, FactorMfa, InitiateSSOAuthFactor and SuccessAuthentication events.
Maps imAuthentication's username_has_any parameter to the OCI TargetUsername field.


The Advanced Security Information Model (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Microsoft Sentinel workspace.

For more information, see:

- [Normalization and the Advanced Security Information Model (ASIM)](https://aka.ms/AboutASIM)
- [Deploy all of ASIM](https://aka.ms/DeployASIM)
- [ASIM Authentication normalization schema reference](https://aka.ms/ASimAuthenticationDoc)

For the changelog, see:
- [CHANGELOG](https://github.com/Azure/Azure-Sentinel/blob/master/Parsers/ASimAuthentication/CHANGELOG/vimAuthenticationOracleOCI.md)

<br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuthentication%2FARM%2FvimAuthenticationOracleOCI%2FvimAuthenticationOracleOCI.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FParsers%2FASimAuthentication%2FARM%2FvimAuthenticationOracleOCI%2FvimAuthenticationOracleOCI.json)
