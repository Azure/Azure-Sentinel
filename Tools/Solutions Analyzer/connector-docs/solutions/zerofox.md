# ZeroFox

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | ZeroFox |
| **Support Tier** | Partner |
| **Support Link** | [https://www.zerofox.com/contact-us/](https://www.zerofox.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2023-07-28 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroFox](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroFox) |

## Data Connectors

This solution provides **2 data connector(s)**.

### [ZeroFox Enterprise - Alerts (Polling CCF)](../connectors/zerofoxalertsdefinition.md)

**Publisher:** ZeroFox Enterprise

### [ZeroFox CTI](../connectors/zerofoxctidataconnector.md)

**Publisher:** ZeroFox

The ZeroFox CTI data connectors provide the capability to ingest the different [ZeroFox](https://www.zerofox.com/threat-intelligence/) cyber threat intelligence alerts into Microsoft Sentinel.

| | |
|--------------------------|---|
| **Tables Ingested** | `ZeroFox_CTI_C2_CL` |
| | `ZeroFox_CTI_advanced_dark_web_CL` |
| | `ZeroFox_CTI_botnet_CL` |
| | `ZeroFox_CTI_breaches_CL` |
| | `ZeroFox_CTI_compromised_credentials_CL` |
| | `ZeroFox_CTI_credit_cards_CL` |
| | `ZeroFox_CTI_dark_web_CL` |
| | `ZeroFox_CTI_discord_CL` |
| | `ZeroFox_CTI_disruption_CL` |
| | `ZeroFox_CTI_email_addresses_CL` |
| | `ZeroFox_CTI_exploits_CL` |
| | `ZeroFox_CTI_irc_CL` |
| | `ZeroFox_CTI_malware_CL` |
| | `ZeroFox_CTI_national_ids_CL` |
| | `ZeroFox_CTI_phishing_CL` |
| | `ZeroFox_CTI_phone_numbers_CL` |
| | `ZeroFox_CTI_ransomware_CL` |
| | `ZeroFox_CTI_telegram_CL` |
| | `ZeroFox_CTI_threat_actors_CL` |
| | `ZeroFox_CTI_vulnerabilities_CL` |
| **Connector Definition Files** | [ZeroFoxCTI.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ZeroFox/Data%20Connectors/CTI/ZeroFoxCTI.json) |

[→ View full connector details](../connectors/zerofoxctidataconnector.md)

## Tables Reference

This solution ingests data into **21 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `ZeroFoxAlertPoller_CL` | [ZeroFox Enterprise - Alerts (Polling CCF)](../connectors/zerofoxalertsdefinition.md) |
| `ZeroFox_CTI_C2_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_advanced_dark_web_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_botnet_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_breaches_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_compromised_credentials_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_credit_cards_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_dark_web_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_discord_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_disruption_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_email_addresses_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_exploits_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_irc_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_malware_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_national_ids_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_phishing_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_phone_numbers_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_ransomware_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_telegram_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_threat_actors_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |
| `ZeroFox_CTI_vulnerabilities_CL` | [ZeroFox CTI](../connectors/zerofoxctidataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
