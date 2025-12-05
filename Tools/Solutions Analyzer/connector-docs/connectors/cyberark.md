# [Deprecated] CyberArk Enterprise Password Vault (EPV) Events via Legacy Agent

| | |
|----------|-------|
| **Connector ID** | `CyberArk` |
| **Publisher** | Cyber-Ark |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [CyberArk Enterprise Password Vault (EPV) Events](../solutions/cyberark-enterprise-password-vault-(epv)-events.md) |
| **Connector Definition Files** | [CyberArk%20Data%20Connector.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events/Data%20Connectors/CyberArk%20Data%20Connector.json) |

CyberArk Enterprise Password Vault generates an xml Syslog message for every action taken against the Vault.  The EPV will send the xml messages through the Microsoft Sentinel.xsl translator to be converted into CEF standard format and sent to a syslog staging server of your choice (syslog-ng, rsyslog). The Log Analytics agent installed on your syslog staging server will import the messages into Microsoft Log Analytics. Refer to the [CyberArk documentation](https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/PASIMP/DV-Integrating-with-SIEM-Applications.htm) for more guidance on SIEM integrations.

[← Back to Connectors Index](../connectors-index.md)
