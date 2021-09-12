# The Azure Sentinel Information Model (ASIM) Authentication parsers

This folder includes the the Azure Sentinel Information Model (ASIM) Authentication parsers. The parsers are provided in YAML and in ARM template formats. The latter can be used to deploy the parsers, while the former is provided for educational purposes. 

The Azure Sentinel Information Mode (ASIM) enables you to use and create source-agnostic content, simplifying your analysis of the data in your Azure Sentinel workspace.

For more information, see:

- [Normalization and the Azure Sentinel Information Model (ASIM)](https://aka.ms/AzSentinelNormalization)
- [Azure Sentinel Authentication normalization schema reference](https://aka.ms/AzSentinelAuthenticationDoc)

<br>

To deploy all parsers to your workspace using ARM templates use the button below:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://aka.ms/AzSentinelAuthenticationARM)

<br>

## Parsers

This template deploys the following parsers:

- Source agnostic parsers:
  - imAuthentication - Authentication events from all normalized authentication providers
  - vimAuthenticationEmpty - Empty ASim Authentication table

- Source specific parsers:
  - **AAD** signins:
    - Interactive Users - vimAuthenticationSigninLogs
    - Managed Identities - vimAuthenticationAADManagedIdentitySignInLogs
    - Non-Interactive Users - vimAuthenticationAADNonInteractiveUserSignInLogs
    - Service Principals - vimAuthenticationAADServicePrincipalSignInLogs
  - **AWS** - vimAuthenticationAWSCloudTrail
  - **Okta** - vimAuthenticationOktaSSO
  - **Windows Security Events** collecting using the Log Analytics Agent or Azure Monitor Agent - vimAuthenticationWindowsSecurityEvent
  - **Windows Events** collecting using the Azure Monitor Agent - vimAuthenticationMicrosoftWindowsEvent. Note that those are the same original events as Windows Security events, but collected to the WindowsEvent table, for example when collecting using Windows Event Forwarding.
  - **Microsoft Defender for IoT - Endpoint**, reporting Linux authentication events - vimAuthenticationMD4IoT
