# AIShield AI Security Monitoring

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | AIShield |
| **Support Tier** | Partner |
| **Support Link** | [https://azuremarketplace.microsoft.com/marketplace/apps/rbei.bgsw_aishield_product/](https://azuremarketplace.microsoft.com/marketplace/apps/rbei.bgsw_aishield_product/) |
| **Categories** | domains |
| **First Published** | 2022-01-11 |
| **Last Updated** | 2025-03-06 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [AIShield](../connectors/boschaishield.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AIShield_CL`](../tables/aishield-cl.md) | [AIShield](../connectors/boschaishield.md) | Analytics, Workbooks |
| [`GuardianTest`](../tables/guardiantest.md) | - | Workbooks |
| [`Guardian_CL`](../tables/guardian-cl.md) | - | Analytics |

## Content Items

This solution includes **42 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 38 |
| Workbooks | 2 |
| Parsers | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [AIShield - Image Segmentation AI Model extraction high suspicious vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/ImageSegmentationModelExtractionHighSuspiciousVulnDetection.yaml) | High | - | [`AIShield_CL`](../tables/aishield-cl.md) |
| [AIShield - Image classification AI Model Evasion high suspicious vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/ImageClassficationModelEvasionHighSuspiciousVulnDetection.yaml) | High | - | [`AIShield_CL`](../tables/aishield-cl.md) |
| [AIShield - Image classification AI Model Evasion low suspicious vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/ImageClassficationModelEvasionLowSuspiciousVulnDetection.yaml) | High | - | [`AIShield_CL`](../tables/aishield-cl.md) |
| [AIShield - Image classification AI Model extraction high suspicious vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/ImageClassficationModelExtractionHighSuspiciousVulnDetection.yaml) | High | - | [`AIShield_CL`](../tables/aishield-cl.md) |
| [AIShield - Natural language processing AI model extraction high suspicious vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/NaturalLanguageProcessingModelExtractionHighSuspiciousVulDetection.yaml) | High | - | [`AIShield_CL`](../tables/aishield-cl.md) |
| [AIShield - Tabular classification AI Model Evasion high suspicious vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/TabularClassificationModelEvasionHighSuspiciousVulnDetection.yaml) | High | - | [`AIShield_CL`](../tables/aishield-cl.md) |
| [AIShield - Tabular classification AI Model Evasion low suspicious vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/TabularClassificationModelEvasionLowSuspiciousVulnDetection.yaml) | Medium | - | [`AIShield_CL`](../tables/aishield-cl.md) |
| [AIShield - Tabular classification AI Model extraction high suspicious vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/TabularClassificationModelExtractionHighSuspiciousVulnDetection.yaml) | High | - | [`AIShield_CL`](../tables/aishield-cl.md) |
| [AIShield - Timeseries Forecasting AI Model extraction high suspicious vulnerability detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/TimeSeriesForecastingModelExtractionHighSuspiciousVulnDetection.yaml) | High | - | [`AIShield_CL`](../tables/aishield-cl.md) |
| [Guardian- Additional check JSON Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/JSONPolicyViolationVulDetection.yaml) | Informational | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- BII Detection Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/BIIDetectionVulDetection.yaml) | High | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Ban Topic Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/BanTopicVulDetection.yaml) | Medium | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Block Competitor Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/BlockCompetitorVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Blocks specific strings of text Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/BlockSubstringVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Code Detection Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/CodeDetectionVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Content Access Control Allowed List Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/ContentAccessControlAllowedListVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Content Access Control Blocked List Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/ContentAccessControlBlockedListVulDetection.yaml) | Medium | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Content Safety Profanity Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/ContentSafetyProfanityVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Content Safety Toxicity Policy Violation Detection.](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/ContentSafetyToxicityVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Gender Bias Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/GenderBiasVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Input Output Relevance Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/InputOutputRelevanceVulDetection.yaml) | Informational | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Input Rate Limiter Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/InputRateLimiterVulDetection.yaml) | Informational | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Invisible Text Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/InvisibleTextVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Language Detection Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/LanguageDetectionVulDetection.yaml) | Informational | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Malicious URL Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/MaliciousURLDetectionVulDetection.yaml) | Medium | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- No LLM Output Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/NoLLMOutputVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Not Safe For Work Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/NotSafeForWorkVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Privacy Protection PII Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/PrivacyProtectionPIIVulDetection.yaml) | High | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Racial Bias Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/RacialBiasVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Regex Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/RegexVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Same Input/Output Language Detection Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/SameInOpLanguageDetectionVulDetection.yaml) | Informational | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Secrets Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/SecretsVulDetection.yaml) | Medium | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Security Integrity Checks Prompt Injection Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/SecurityIntegrityChecksPIIVulDetection.yaml) | High | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Sentiment Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/SentimentVulDetection.yaml) | Low | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Special PII Detection Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/SpecialPIIDetectionVulDetection.yaml) | High | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- Token Limit Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/TokenLimitVulDetection.yaml) | Informational | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- URL Detection Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/URLDetectionVulDetection.yaml) | Informational | - | [`Guardian_CL`](../tables/guardian-cl.md) |
| [Guardian- URL Reachability Policy Violation Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Analytic%20Rules/URLReachabilityVulDetection.yaml) | Informational | - | [`Guardian_CL`](../tables/guardian-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [AIShield](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Workbooks/AIShield.json) | [`AIShield_CL`](../tables/aishield-cl.md) |
| [GuardianDashboard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Workbooks/GuardianDashboard.json) | [`GuardianTest`](../tables/guardiantest.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [AIShield](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Parsers/AIShield.yaml) | - | - |
| [Guardian](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AIShield%20AI%20Security%20Monitoring/Parsers/Guardian.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                               |
|-------------|--------------------------------|------------------------------------------------------------------|
|  3.0.1      |  06-03-2025                    | Added new **Analytic Rules**. <br>Added new **Workbook** GuardianDashboard.json. <br>Added new **Parser** Guardian.yaml |
|  3.0.0      |  15-01-2023                    | Added Entity Mapping and remove alertactics Column Name to **Analytic Rules**. <br>Added new **Analytic Rules** and updated existing **Analytic Rules** and (AIShield) **Parser**.  |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
