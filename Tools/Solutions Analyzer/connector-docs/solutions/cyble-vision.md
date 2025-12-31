# Cyble Vision

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Cyble Support |
| **Support Tier** | Partner |
| **Support Link** | [https://cyble.com/talk-to-sales/](https://cyble.com/talk-to-sales/) |
| **Categories** | domains |
| **First Published** | 2025-05-05 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Cyble Vision Alerts](../connectors/cyblevisionalerts.md)

## Tables Reference

This solution uses **45 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Alerts_advisory`](../tables/alerts-advisory.md) | - | Analytics |
| [`Alerts_assets`](../tables/alerts-assets.md) | - | Analytics |
| [`Alerts_bit_bucket`](../tables/alerts-bit-bucket.md) | - | Analytics |
| [`Alerts_cloud_storage`](../tables/alerts-cloud-storage.md) | - | Analytics |
| [`Alerts_compromised_endpoints_cookies`](../tables/alerts-compromised-endpoints-cookies.md) | - | Analytics |
| [`Alerts_compromised_files`](../tables/alerts-compromised-files.md) | - | Analytics |
| [`Alerts_cyber_crime_forums`](../tables/alerts-cyber-crime-forums.md) | - | Analytics |
| [`Alerts_darkweb_data_breaches`](../tables/alerts-darkweb-data-breaches.md) | - | Analytics |
| [`Alerts_darkweb_marketplaces`](../tables/alerts-darkweb-marketplaces.md) | - | Analytics |
| [`Alerts_darkweb_ransomware`](../tables/alerts-darkweb-ransomware.md) | - | Analytics |
| [`Alerts_defacement_content`](../tables/alerts-defacement-content.md) | - | Analytics |
| [`Alerts_defacement_keyword`](../tables/alerts-defacement-keyword.md) | - | Analytics |
| [`Alerts_defacement_url`](../tables/alerts-defacement-url.md) | - | Analytics |
| [`Alerts_discord`](../tables/alerts-discord.md) | - | Analytics |
| [`Alerts_docker`](../tables/alerts-docker.md) | - | Analytics |
| [`Alerts_domain_expiry`](../tables/alerts-domain-expiry.md) | - | Analytics |
| [`Alerts_domain_watchlist`](../tables/alerts-domain-watchlist.md) | - | Analytics |
| [`Alerts_flash_report`](../tables/alerts-flash-report.md) | - | Analytics |
| [`Alerts_github`](../tables/alerts-github.md) | - | Analytics |
| [`Alerts_hacktivism`](../tables/alerts-hacktivism.md) | - | Analytics |
| [`Alerts_i2p`](../tables/alerts-i2p.md) | - | Analytics |
| [`Alerts_iocs`](../tables/alerts-iocs.md) | - | Analytics |
| [`Alerts_ip_risk_score`](../tables/alerts-ip-risk-score.md) | - | Analytics |
| [`Alerts_leaked_credentials`](../tables/alerts-leaked-credentials.md) | - | Analytics |
| [`Alerts_malicious_ads`](../tables/alerts-malicious-ads.md) | - | Analytics |
| [`Alerts_mobile_apps`](../tables/alerts-mobile-apps.md) | - | Analytics |
| [`Alerts_new_vulnerability`](../tables/alerts-new-vulnerability.md) | - | Analytics |
| [`Alerts_news_feed`](../tables/alerts-news-feed.md) | - | Analytics |
| [`Alerts_osint`](../tables/alerts-osint.md) | - | Analytics |
| [`Alerts_ot_ics`](../tables/alerts-ot-ics.md) | - | Analytics |
| [`Alerts_pastebin`](../tables/alerts-pastebin.md) | - | Analytics |
| [`Alerts_phishing`](../tables/alerts-phishing.md) | - | Analytics |
| [`Alerts_physical_threats`](../tables/alerts-physical-threats.md) | - | Analytics |
| [`Alerts_postman`](../tables/alerts-postman.md) | - | Analytics |
| [`Alerts_product_vulnerability`](../tables/alerts-product-vulnerability.md) | - | Analytics |
| [`Alerts_social_media_monitoring`](../tables/alerts-social-media-monitoring.md) | - | Analytics |
| [`Alerts_ssl_expiry`](../tables/alerts-ssl-expiry.md) | - | Analytics |
| [`Alerts_stealer_logs`](../tables/alerts-stealer-logs.md) | - | Analytics |
| [`Alerts_subdomains`](../tables/alerts-subdomains.md) | - | Analytics |
| [`Alerts_suspicious_domains`](../tables/alerts-suspicious-domains.md) | - | Analytics |
| [`Alerts_telegram_mentions`](../tables/alerts-telegram-mentions.md) | - | Analytics |
| [`Alerts_tor_links`](../tables/alerts-tor-links.md) | - | Analytics |
| [`Alerts_vulnerability`](../tables/alerts-vulnerability.md) | - | Analytics |
| [`Alerts_web_applications`](../tables/alerts-web-applications.md) | - | Analytics |
| [`CybleVisionAlerts_CL`](../tables/cyblevisionalerts-cl.md) | [Cyble Vision Alerts](../connectors/cyblevisionalerts.md) | Workbooks |

## Content Items

This solution includes **94 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 45 |
| Analytic Rules | 44 |
| Playbooks | 4 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Cyble Advisory Alerts Advisory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_advisory.yaml) | Low | Reconnaissance, ResourceDevelopment | [`Alerts_advisory`](../tables/alerts-advisory.md) |
| [Cyble Vision Alerts Assets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Assets.yaml) | Low | Reconnaissance | [`Alerts_assets`](../tables/alerts-assets.md) |
| [Cyble Vision Alerts Bitbucket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_BitBucket.yaml) | Low | CredentialAccess, Exfiltration, Discovery | [`Alerts_bit_bucket`](../tables/alerts-bit-bucket.md) |
| [Cyble Vision Alerts Cloud Storage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Cloud_Storage.yaml) | Low | Exfiltration, Discovery | [`Alerts_cloud_storage`](../tables/alerts-cloud-storage.md) |
| [Cyble Vision Alerts Compromised Endpoint Cookies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Compromised_Endpoints_Cookies.yaml) | Low | CredentialAccess, DefenseEvasion | [`Alerts_compromised_endpoints_cookies`](../tables/alerts-compromised-endpoints-cookies.md) |
| [Cyble Vision Alerts Compromised Files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Compromised_Files.yaml) | Low | CredentialAccess, Exfiltration | [`Alerts_compromised_files`](../tables/alerts-compromised-files.md) |
| [Cyble Vision Alerts Cyble Web Applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Web_Applications.yaml) | Low | Reconnaissance | [`Alerts_web_applications`](../tables/alerts-web-applications.md) |
| [Cyble Vision Alerts Darkweb Data Breaches](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Darkweb_Data_Breaches.yaml) | Low | Reconnaissance, InitialAccess, Exfiltration, Collection | [`Alerts_darkweb_data_breaches`](../tables/alerts-darkweb-data-breaches.md) |
| [Cyble Vision Alerts Darkweb Ransomware Leak](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_darkweb_ransomware_rule.yaml) | Low | Impact, Exfiltration, Reconnaissance | [`Alerts_darkweb_ransomware`](../tables/alerts-darkweb-ransomware.md) |
| [Cyble Vision Alerts Discord Keyword](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_discord_rule.yaml) | Low | Reconnaissance, InitialAccess | [`Alerts_discord`](../tables/alerts-discord.md) |
| [Cyble Vision Alerts Discovered Subdomain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_subdomains_rule.yaml) | Low | Reconnaissance | [`Alerts_subdomains`](../tables/alerts-subdomains.md) |
| [Cyble Vision Alerts Docker](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Docker.yaml) | Low | Exfiltration, Execution, Discovery | [`Alerts_docker`](../tables/alerts-docker.md) |
| [Cyble Vision Alerts Domain Expiry Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_domain_expiry_rule.yaml) | Low | Impact | [`Alerts_domain_expiry`](../tables/alerts-domain-expiry.md) |
| [Cyble Vision Alerts Domain Watchlist](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_domain_watchlist_rule.yaml) | Low | ResourceDevelopment | [`Alerts_domain_watchlist`](../tables/alerts-domain-watchlist.md) |
| [Cyble Vision Alerts Flash Report](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Flash_Report_Alerts.yaml) | Low | Reconnaissance | [`Alerts_flash_report`](../tables/alerts-flash-report.md) |
| [Cyble Vision Alerts Github](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_github.yaml) | Low | Collection, CredentialAccess | [`Alerts_github`](../tables/alerts-github.md) |
| [Cyble Vision Alerts Hacktivism](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_hacktivism.yaml) | Low | Reconnaissance, Impact, ResourceDevelopment | [`Alerts_hacktivism`](../tables/alerts-hacktivism.md) |
| [Cyble Vision Alerts I2P Monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_i2p_rule.yaml) | Low | ResourceDevelopment | [`Alerts_i2p`](../tables/alerts-i2p.md) |
| [Cyble Vision Alerts IOC'S](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_IOC%27S.yaml) | Low | Reconnaissance, InitialAccess, Discovery, CommandAndControl, Impact | [`Alerts_iocs`](../tables/alerts-iocs.md) |
| [Cyble Vision Alerts IP Risk Score](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_ip_risk_score_rule.yaml) | Low | Reconnaissance | [`Alerts_ip_risk_score`](../tables/alerts-ip-risk-score.md) |
| [Cyble Vision Alerts Leaked Credentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Leaked_Credentials.yaml) | Low | CredentialAccess, Discovery, Reconnaissance | [`Alerts_leaked_credentials`](../tables/alerts-leaked-credentials.md) |
| [Cyble Vision Alerts Malicious Ads Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Malicious_ads.yaml) | Low | InitialAccess, Execution | [`Alerts_malicious_ads`](../tables/alerts-malicious-ads.md) |
| [Cyble Vision Alerts New Vulnerability Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_new_vulnerability_rule.yaml) | Low | InitialAccess | [`Alerts_new_vulnerability`](../tables/alerts-new-vulnerability.md) |
| [Cyble Vision Alerts News Feed Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_News_Feed.yaml) | Low | Reconnaissance | [`Alerts_news_feed`](../tables/alerts-news-feed.md) |
| [Cyble Vision Alerts OSINT Mention Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_osint_rule.yaml) | Low | Reconnaissance, ResourceDevelopment | [`Alerts_osint`](../tables/alerts-osint.md) |
| [Cyble Vision Alerts OT/ICS Threat Activity Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_ot_ics_rule.yaml) | Low | Discovery, Collection | [`Alerts_ot_ics`](../tables/alerts-ot-ics.md) |
| [Cyble Vision Alerts Pastebin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_pastebin_rule.yaml) | Low | Reconnaissance | [`Alerts_pastebin`](../tables/alerts-pastebin.md) |
| [Cyble Vision Alerts Phishing Domain Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_phishing_rule.yaml) | Low | Reconnaissance | [`Alerts_phishing`](../tables/alerts-phishing.md) |
| [Cyble Vision Alerts Physical Threat Alert](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Physical_Threats.yaml) | Low | Impact | [`Alerts_physical_threats`](../tables/alerts-physical-threats.md) |
| [Cyble Vision Alerts Postman API Exposure Detection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Postman.yaml) | Low | Reconnaissance, CredentialAccess, Exfiltration | [`Alerts_postman`](../tables/alerts-postman.md) |
| [Cyble Vision Alerts Product Vulnerability Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_product_vulnerability_rule.yaml) | Low | InitialAccess, ResourceDevelopment | [`Alerts_product_vulnerability`](../tables/alerts-product-vulnerability.md) |
| [Cyble Vision Alerts SSL Certificate Expiry](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_ssl_expiry.yaml) | Low | InitialAccess, Impact | [`Alerts_ssl_expiry`](../tables/alerts-ssl-expiry.md) |
| [Cyble Vision Alerts Social Media Monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Social_Media_Monitoring.yaml) | Low | Reconnaissance, ResourceDevelopment | [`Alerts_social_media_monitoring`](../tables/alerts-social-media-monitoring.md) |
| [Cyble Vision Alerts Suspicious Domain](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Suspicious_Domain.yaml) | Low | Reconnaissance | [`Alerts_suspicious_domains`](../tables/alerts-suspicious-domains.md) |
| [Cyble Vision Alerts TOR Links](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_TOR_Links.yaml) | Low | ResourceDevelopment, Reconnaissance | [`Alerts_tor_links`](../tables/alerts-tor-links.md) |
| [Cyble Vision Alerts Vulnerability](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Vulnerability.yaml) | Low | Reconnaissance, Execution, Discovery | [`Alerts_vulnerability`](../tables/alerts-vulnerability.md) |
| [Cyble Vision Alerts Website Defacement Content](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Defacement_Content.yaml) | Low | Impact | [`Alerts_defacement_content`](../tables/alerts-defacement-content.md) |
| [Cyble Vision Alerts Website Defacement Keyword](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_defacement_keyword_rule.yaml) | Low | Impact, Reconnaissance | [`Alerts_defacement_keyword`](../tables/alerts-defacement-keyword.md) |
| [Cyble Vision Alerts Website Defacement URL](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_defacement_url_rule.yaml) | Low | Impact | [`Alerts_defacement_url`](../tables/alerts-defacement-url.md) |
| [CybleVision Alerts Cyber Crime Forum Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Cyber_Crime_Forum.yaml) | Low | Reconnaissance, ResourceDevelopment, Exfiltration | [`Alerts_cyber_crime_forums`](../tables/alerts-cyber-crime-forums.md) |
| [CybleVision Alerts Darkweb Marketplace Alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Darkweb_Marketplace.yaml) | Low | CredentialAccess, Collection, Exfiltration, Reconnaissance | [`Alerts_darkweb_marketplaces`](../tables/alerts-darkweb-marketplaces.md) |
| [CybleVision Alerts Mobile Apps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Mobile_Apps.yaml) | Low | Reconnaissance, ResourceDevelopment, InitialAccess | [`Alerts_mobile_apps`](../tables/alerts-mobile-apps.md) |
| [CybleVision Alerts Stealer Logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Stealer_Logs.yaml) | Low | CredentialAccess, Collection, Exfiltration, Reconnaissance, InitialAccess | [`Alerts_stealer_logs`](../tables/alerts-stealer-logs.md) |
| [CybleVision Alerts Telegram Mentions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Analytic%20Rules/Alerts_Telegram_Mentions.yaml) | Low | Reconnaissance, ResourceDevelopment, InitialAccess, CommandAndControl | [`Alerts_telegram_mentions`](../tables/alerts-telegram-mentions.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [CybleVisionAlertsWorkbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Workbooks/CybleVisionAlertsWorkbook.json) | [`CybleVisionAlerts_CL`](../tables/cyblevisionalerts-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Azure_Sentinel_automation_rules](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Playbooks/CybleVisionAlert_Status_Update/Azure_Sentinel_automation_rules.json) | - | - |
| [Cyble-IOC_Enrichment-Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Playbooks/IoC-Enrichment/azuredeploy.json) | This playbook leverages the Cyble API to enrich IP, Domain, Url & Hash indicators, found in Microsof... | - |
| [Cyble-ThreatIntelligence-Ingest-Playbook](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Playbooks/TI-Ingest/azuredeploy.json) | This playbook imports IoC lists from Cyble and stores them as Threat Intelligence Indicators in Micr... | - |
| [CybleVisionAlert_Status_Update](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Playbooks/CybleVisionAlert_Status_Update/azuredeploy.json) | This Logic App updates Cyble alert status and severity based on Sentinel incident changes. It suppor... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Alerts_advisory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_advisory.yaml) | - | - |
| [Alerts_assets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_assets.yaml) | - | - |
| [Alerts_bit_bucket](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_bit_bucket.yaml) | - | - |
| [Alerts_cloud_storage](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_cloud_storage.yaml) | - | - |
| [Alerts_compromised_endpoints_cookies](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_compromised_endpoints_cookies.yaml) | - | - |
| [Alerts_compromised_files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_compromised_files.yaml) | - | - |
| [Alerts_cyber_crime_forums](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_cyber_crime_forums.yaml) | - | - |
| [Alerts_darkweb_data_breaches](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_darkweb_data_breaches.yaml) | - | - |
| [Alerts_darkweb_marketplaces](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_darkweb_marketplaces.yaml) | - | - |
| [Alerts_darkweb_ransomware](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_darkweb_ransomware.yaml) | - | - |
| [Alerts_defacement_content](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_defacement_content.yaml) | - | - |
| [Alerts_defacement_keyword](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_defacement_keyword.yaml) | - | - |
| [Alerts_defacement_url](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_defacement_url.yaml) | - | - |
| [Alerts_discord](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_discord.yaml) | - | - |
| [Alerts_docker](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_docker.yaml) | - | - |
| [Alerts_domain_expiry](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_domain_expiry.yaml) | - | - |
| [Alerts_domain_watchlist](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_domain_watchlist.yaml) | - | - |
| [Alerts_flash_report](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_flash_report.yaml) | - | - |
| [Alerts_github](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_github.yaml) | - | - |
| [Alerts_hacktivism](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_hacktivism.yaml) | - | - |
| [Alerts_i2p](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_i2p.yaml) | - | - |
| [Alerts_iocs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_iocs.yaml) | - | - |
| [Alerts_ip_risk_score](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_ip_risk_score.yaml) | - | - |
| [Alerts_leaked_credentials](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_leaked_credentials.yaml) | - | - |
| [Alerts_malicious_ads](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_malicious_ads.yaml) | - | - |
| [Alerts_mobile_apps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_mobile_apps.yaml) | - | - |
| [Alerts_new_vulnerability](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_new_vulnerability.yaml) | - | - |
| [Alerts_news_feed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_news_feed.yaml) | - | - |
| [Alerts_osint](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_osint.yaml) | - | - |
| [Alerts_ot_ics](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_ot_ics.yaml) | - | - |
| [Alerts_pastebin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_pastebin.yaml) | - | - |
| [Alerts_phishing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_phishing.yaml) | - | - |
| [Alerts_physical_threats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_physical_threats.yaml) | - | - |
| [Alerts_postman](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_postman.yaml) | - | - |
| [Alerts_product_vulnerability](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_product_vulnerability.yaml) | - | - |
| [Alerts_ransomware_updates](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_ransomware_updates.yaml) | - | - |
| [Alerts_social_media_monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_social_media_monitoring.yaml) | - | - |
| [Alerts_ssl_expiry](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_ssl_expiry.yaml) | - | - |
| [Alerts_stealer_logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_stealer_logs.yaml) | - | - |
| [Alerts_subdomains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_subdomains.yaml) | - | - |
| [Alerts_suspicious_domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_suspicious_domains.yaml) | - | - |
| [Alerts_telegram_mentions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_telegram_mentions.yaml) | - | - |
| [Alerts_tor_links](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_tor_links.yaml) | - | - |
| [Alerts_vulnerability](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_vulnerability.yaml) | - | - |
| [Alerts_web_applications](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Cyble%20Vision/Parsers/Alerts_web_applications.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                     |
|-------------|--------------------------------|--------------------------------------------------------|
| 3.0.2       | 14-12-2025                     | Added new **CCF data connector**.<br/> Added new **Parsers** to Parse data message of each service.<br/> Added **Analytic Rules** to generate incidents based on Services.                      |
| 3.0.1       | 10-06-2025                     | *Cyble-ThreatIntelligence-Ingest* **Playbook**, including fixes for de-duplication of IoCs, optimized KQL query load, and pagination support. |
| 3.0.0       | 20-05-2025                     | Initial Solution Release.                              |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
