# CyberArk Enterprise Password Vault (EPV) Events

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Cyberark |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyberark.com/services-support/technical-support/](https://www.cyberark.com/services-support/technical-support/) |
| **Categories** | domains |
| **First Published** | 2022-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [[Deprecated] CyberArk Enterprise Password Vault (EPV) Events via Legacy Agent](../connectors/cyberark.md)

**Publisher:** Cyber-Ark

### [[Deprecated] CyberArk Privilege Access Manager (PAM) Events via AMA](../connectors/cyberarkama.md)

**Publisher:** Cyber-Ark

CyberArk Privilege Access Manager generates an xml Syslog message for every action taken against the Vault.  The PAM will send the xml messages through the Microsoft Sentinel.xsl translator to be converted into CEF standard format and sent to a syslog staging server of your choice (syslog-ng, rsyslog). The Log Analytics agent installed on your syslog staging server will import the messages into Microsoft Log Analytics. Refer to the [CyberArk documentation](https://docs.cyberark.com/privilege-cloud-standard/Latest/en/Content/Privilege%20Cloud/privCloud-connect-siem.htm) for more guidance on SIEM integrations.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [template_CyberArkAMA.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CyberArk%20Enterprise%20Password%20Vault%20%28EPV%29%20Events/Data%20Connectors/template_CyberArkAMA.json) |

[→ View full connector details](../connectors/cyberarkama.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [[Deprecated] CyberArk Enterprise Password Vault (EPV) Events via Legacy Agent](../connectors/cyberark.md), [[Deprecated] CyberArk Privilege Access Manager (PAM) Events via AMA](../connectors/cyberarkama.md) |

[← Back to Solutions Index](../solutions-index.md)
