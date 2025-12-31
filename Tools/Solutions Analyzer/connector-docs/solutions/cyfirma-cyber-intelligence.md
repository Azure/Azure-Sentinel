# Cyfirma Cyber Intelligence

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | CYFIRMA |
| **Support Tier** | Partner |
| **Support Link** | [https://www.cyfirma.com/contact-us/](https://www.cyfirma.com/contact-us/) |
| **Categories** | domains |
| **First Published** | 2025-05-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md)

## Tables Reference

This solution uses **4 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`CyfirmaCampaigns_CL`](../tables/cyfirmacampaigns-cl.md) | [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md) | - |
| [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) | [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md) | Analytics |
| [`CyfirmaMalware_CL`](../tables/cyfirmamalware-cl.md) | [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md) | - |
| [`CyfirmaThreatActors_CL`](../tables/cyfirmathreatactors-cl.md) | [CYFIRMA Cyber Intelligence](../connectors/cyfirmacyberintelligencedc.md) | - |

## Content Items

This solution includes **36 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 36 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [CYFIRMA - High severity Command & Control Network Indicators with Block Recommendation Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/C2NetworkIndicatorsBlockHighSeverityRule.yaml) | High | CommandAndControl, InitialAccess, Exfiltration | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Command & Control Network Indicators with Monitor Recommendation Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/C2NetworkIndicatorsMonitorHighSeverityRule.yaml) | High | CommandAndControl, InitialAccess, Exfiltration | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity File Hash Indicators with Block Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/FileHashIndicatorsBlockHighSeverityRule.yaml) | High | Execution, InitialAccess, DefenseEvasion, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity File Hash Indicators with Block Action and Malware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/MalwareFileHashIndicatorsBlockHighSeverityRule.yaml) | High | InitialAccess, Execution, Persistence, PrivilegeEscalation, DefenseEvasion, CredentialAccess, Discovery, LateralMovement, Collection, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity File Hash Indicators with Monitor Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/FileHashIndicatorsMonitorHighSeverityRule.yaml) | High | Execution, InitialAccess, DefenseEvasion, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity File Hash Indicators with Monitor Action and Malware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/MalwareFileHashIndicatorsMonitorHighSeverityRule.yaml) | High | DefenseEvasion, InitialAccess, Impact, Execution | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Malicious Network Indicators Associated with Malware - Block Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/MalwareNetworkIndicatorsBlockHighSeverityRule.yaml) | High | InitialAccess, Execution, CommandAndControl | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Malicious Network Indicators Associated with Malware - Monitor Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/MalwareNetworkIndicatorsMonitorHighSeverityRule.yaml) | High | InitialAccess, Execution, CommandAndControl | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Malicious Network Indicators with Block Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/NetworkIndicatorsBlockHighSeverityRule.yaml) | High | InitialAccess, Execution, Reconnaissance, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Malicious Network Indicators with Monitor Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/NetworkIndicatorsMonitorHighSeverityRule.yaml) | High | InitialAccess, Execution, Reconnaissance, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Malicious Phishing Network Indicators - Block Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/PhishingNetworkIndicatorsBlockHighSeverityRule.yaml) | High | InitialAccess, Execution, CredentialAccess, Exfiltration | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Malicious Phishing Network Indicators - Monitor Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/PhishingNetworkIndicatorsMonitorHighSeverityRule.yaml) | High | InitialAccess, Execution, CredentialAccess, Exfiltration | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity TOR Node Network Indicators - Block Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TORNodeNetworkIndicatorsBlockHighSeverityRule.yaml) | High | CommandAndControl, Exfiltration, InitialAccess, Persistence, Reconnaissance | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity TOR Node Network Indicators - Monitor Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TORNodeNetworkIndicatorsMonitorHighSeverityRule.yaml) | High | CommandAndControl, Exfiltration, InitialAccess, Persistence, Reconnaissance | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Trojan File Hash Indicators with Block Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TrojanFileHashIndicatorsBlockHighSeverityRule.yaml) | High | InitialAccess, Execution, Persistence, DefenseEvasion, CommandAndControl, CredentialAccess | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Trojan File Hash Indicators with Monitor Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TrojanFileHashIndicatorsMonitorHighSeverityRule.yaml) | High | InitialAccess, Execution, Persistence, DefenseEvasion, CommandAndControl, CredentialAccess | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Trojan Network Indicators - Block Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TrojanNetworkIndicatorsBlockHighSeverityRule.yaml) | High | Impact, Persistence, DefenseEvasion, CredentialAccess, CommandAndControl, Execution, InitialAccess | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - High severity Trojan Network Indicators - Monitor Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TrojanNetworkIndicatorsMonitorHighSeverityRule.yaml) | High | Impact, Persistence, DefenseEvasion, CredentialAccess, CommandAndControl, Execution, InitialAccess | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Command & Control Network Indicators with Block Recommendation Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/C2NetworkIndicatorsBlockMediumSeverityRule.yaml) | Medium | CommandAndControl, InitialAccess, Exfiltration | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Command & Control Network Indicators with Monitor Recommendation Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/C2NetworkIndicatorsMonitorMediumSeverityRule.yaml) | Medium | CommandAndControl, InitialAccess, Exfiltration | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity File Hash Indicators with Block Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/FileHashIndicatorsBlockMediumSeverityRule.yaml) | Medium | Execution, InitialAccess, DefenseEvasion, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity File Hash Indicators with Block Action and Malware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/MalwareFileHashIndicatorsBlockMediumSeverityRule.yaml) | Medium | InitialAccess, Execution, Persistence, PrivilegeEscalation, DefenseEvasion, CredentialAccess, Discovery, LateralMovement, Collection, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity File Hash Indicators with Monitor Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/FileHashIndicatorsMonitorMediumSeverityRule.yaml) | Medium | Execution, InitialAccess, DefenseEvasion, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity File Hash Indicators with Monitor Action and Malware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/MalwareFileHashIndicatorsMonitorMediumSeverityRule.yaml) | Medium | DefenseEvasion, InitialAccess, Impact, Execution | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Malicious Network Indicators Associated with Malware - Block Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/MalwareNetworkIndicatorsBlockMediumSeverityRule.yaml) | Medium | InitialAccess, Execution, CommandAndControl | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Malicious Network Indicators Associated with Malware - Monitor Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/MalwareNetworkIndicatorsMonitorMediumSeverityRule.yaml) | Medium | InitialAccess, Execution, CommandAndControl | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Malicious Network Indicators with Block Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/NetworkIndicatorsBlockMediumSeverityRule.yaml) | Medium | InitialAccess, Execution, Reconnaissance, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Malicious Network Indicators with Monitor Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/NetworkIndicatorsMonitorMediumSeverityRule.yaml) | Medium | InitialAccess, Execution, Reconnaissance, Impact | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Malicious Phishing Network Indicators - Block Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/PhishingNetworkIndicatorsBlockMediumSeverityRule.yaml) | Medium | InitialAccess, Execution, CredentialAccess, Exfiltration | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Malicious Phishing Network Indicators - Monitor Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/PhishingNetworkIndicatorsMonitorMediumSeverityRule.yaml) | Medium | InitialAccess, Execution, CredentialAccess, Exfiltration | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity TOR Node Network Indicators - Block Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TORNodeNetworkIndicatorsBlockMediumSeverityRule.yaml) | Medium | CommandAndControl, Exfiltration, InitialAccess, Persistence, Reconnaissance | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity TOR Node Network Indicators - Monitor Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TORNodeNetworkIndicatorsMonitorMediumSeverityRule.yaml) | Medium | CommandAndControl, Exfiltration, InitialAccess, Persistence, Reconnaissance | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Trojan File Hash Indicators with Block Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TrojanFileHashIndicatorsBlockMediumSeverityRule.yaml) | Medium | InitialAccess, Execution, Persistence, DefenseEvasion, CommandAndControl, CredentialAccess | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Trojan File Hash Indicators with Monitor Action Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TrojanFileHashIndicatorsMonitorMediumSeverityRule.yaml) | Medium | InitialAccess, Execution, Persistence, DefenseEvasion, CommandAndControl, CredentialAccess | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Trojan Network Indicators - Block Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TrojanNetworkIndicatorsBlockMediumSeverityRule.yaml) | Medium | Impact, Persistence, DefenseEvasion, CredentialAccess, CommandAndControl, Execution, InitialAccess | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |
| [CYFIRMA - Medium severity Trojan Network Indicators - Monitor Recommended Rule](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyfirma%20Cyber%20Intelligence/Analytic%20Rules/TrojanNetworkIndicatorsMonitorMediumSeverityRule.yaml) | Medium | Impact, Persistence, DefenseEvasion, CredentialAccess, CommandAndControl, Execution, InitialAccess | [`CyfirmaIndicators_CL`](../tables/cyfirmaindicators-cl.md) |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                     |
|-------------|--------------------------------|------------------------------------------------------------------------|
| 3.0.2       | 04-09-2025                     | Bugs fixes to **CCF Data Connector**.                                  |
| 3.0.1       | 24-07-2025                     | Minor changes and New analytics rules added to **CCF Data Connector**. |
| 3.0.0       | 17-06-2025                     | Initial Solution Release.                                              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
