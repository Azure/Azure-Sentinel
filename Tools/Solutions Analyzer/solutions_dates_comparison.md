# Solutions Date Comparison: Local vs Marketplace

This table compares publication dates from `SolutionMetadata.json` (local) with dates from the Azure Marketplace API.

**Key observations:**
- Local `first_publish_date` and marketplace `creation_date` rarely match — marketplace listings were typically created later than the solution's initial publication.
- Local `last_publish_date` and marketplace `last_modified_date` never match exactly.
- Solutions with empty marketplace dates are not published on the marketplace.

| Solution | Local First Publish | MP Creation Date | Local Last Publish | MP Last Modified | Published |
|----------|:-------------------:|:----------------:|:------------------:|:----------------:|:---------:|
| 1Password | 2023-12-01 | 2024-06-27 | — | 2025-12-13 | ✅ |
| 42Crunch API Protection | 2022-09-21 | — | — | — | ✅ |
| AbnormalSecurity | 2021-10-20 | 2023-04-03 | — | 2025-12-13 | ✅ |
| AbuseIPDB | 2022-05-23 | 2023-11-22 | — | 2025-12-13 | ✅ |
| Acronis Cyber Protect Cloud | 2025-10-28 | 2025-11-04 | 2025-10-28 | 2026-03-02 | ✅ |
| Agari | 2022-05-02 | — | — | — | ❌ |
| AgileSec Analytics Connector | — | 2023-06-30 | — | 2025-12-13 | ✅ |
| AI Analyst Darktrace | 2022-05-02 | — | — | — | ✅ |
| AIShield AI Security Monitoring | 2022-01-11 | 2023-08-18 | 2025-03-06 | 2025-12-13 | ✅ |
| Akamai Security Events | 2022-03-23 | 2023-03-21 | — | 2025-12-13 | ✅ |
| ALC-WebCTRL | 2021-11-18 | 2024-11-08 | — | 2025-12-13 | ✅ |
| Alibaba Cloud | 2022-06-27 | 2023-04-10 | — | 2025-12-13 | ✅ |
| Alibaba Cloud ActionTrail | 2025-07-03 | 2025-07-08 | — | 2025-12-13 | ✅ |
| Alsid For AD | 2022-05-06 | — | — | — | ❌ |
| Amazon Web Services | 2022-05-26 | 2023-02-24 | — | 2026-01-14 | ✅ |
| Amazon Web Services NetworkFirewall | 2025-03-20 | 2025-07-04 | — | 2025-12-13 | ✅ |
| Amazon Web Services Route 53 | 2025-03-21 | 2025-05-28 | — | 2025-12-13 | ✅ |
| Anvilogic | 2025-06-20 | 2025-09-26 | — | 2025-12-13 | ✅ |
| Apache Log4j Vulnerability Detection | 2021-12-15 | 2023-04-26 | — | 2025-12-13 | ✅ |
| ApacheHTTPServer | 2021-10-27 | 2023-04-06 | — | 2025-12-13 | ✅ |
| archTIS | — | — | — | — | ❌ |
| ARGOSCloudSecurity | 2022-08-16 | 2024-11-08 | — | 2025-12-13 | ✅ |
| AristaAwakeSecurity | 2021-10-18 | 2024-05-13 | — | 2025-12-13 | ✅ |
| Armis | 2022-08-02 | 2023-08-28 | 2024-08-23 | 2025-12-13 | ✅ |
| Armorblox | 2021-10-18 | — | — | — | ✅ |
| Aruba ClearPass | 2022-05-23 | 2023-04-06 | — | 2025-12-13 | ✅ |
| AtlassianConfluenceAudit | 2022-01-24 | 2023-05-26 | — | 2025-12-13 | ✅ |
| AtlassianJiraAudit | 2022-01-10 | 2023-03-03 | — | 2025-12-13 | ✅ |
| Attacker Tools Threat Protection Essentials | 2022-11-16 | 2023-04-25 | — | 2026-01-29 | ✅ |
| Australian Cyber Security Centre | 2022-11-23 | 2023-11-20 | — | 2025-12-13 | ✅ |
| Auth0 | 2022-08-18 | 2023-03-29 | — | 2025-12-13 | ✅ |
| Authomize | 2023-06-15 | — | — | — | ❌ |
| AWS CloudFront | 2025-03-20 | 2025-08-08 | — | 2025-12-13 | ✅ |
| AWS Security Hub | 2025-03-12 | 2025-05-23 | 2025-03-12 | 2025-12-14 | ✅ |
| AWS Systems Manager | — | 2023-10-19 | — | 2026-01-15 | ✅ |
| AWS VPC Flow Logs | 2025-07-30 | — | — | — | ❌ |
| AWS_AccessLogs | 2025-02-06 | 2025-08-12 | — | 2025-12-13 | ✅ |
| AWS_IAM | 2022-09-28 | 2023-05-30 | — | 2025-12-13 | ✅ |
| AWSAthena | 2022-11-18 | 2024-02-27 | — | 2026-01-15 | ✅ |
| Azure Activity | 2022-04-18 | 2023-02-21 | — | 2026-02-27 | ✅ |
| Azure Batch Account | 2022-06-30 | 2023-02-20 | — | 2025-12-13 | ✅ |
| Azure Cloud NGFW By Palo Alto Networks | 2023-11-03 | 2024-07-23 | 2023-11-03 | 2025-12-13 | ✅ |
| Azure Cognitive Search | 2022-06-28 | 2023-04-10 | — | 2025-12-13 | ✅ |
| Azure Data Lake Storage Gen1 | 2022-06-24 | 2023-02-22 | — | 2025-12-13 | ✅ |
| Azure DDoS Protection | 2022-05-13 | 2023-02-28 | — | 2025-12-13 | ✅ |
| Azure Event Hubs | 2022-06-01 | 2023-04-11 | — | 2025-12-13 | ✅ |
| Azure Firewall | 2022-05-23 | 2023-02-27 | — | 2026-02-16 | ✅ |
| Azure Key Vault | 2022-05-02 | 2023-02-17 | — | 2025-12-13 | ✅ |
| Azure kubernetes Service | 2022-06-01 | 2023-02-17 | — | 2025-12-13 | ✅ |
| Azure Logic Apps | 2022-06-24 | 2024-11-08 | — | 2025-12-13 | ✅ |
| Azure Network Security Groups | 2022-05-23 | 2023-02-20 | — | 2025-12-14 | ✅ |
| Azure Resource Graph | 2025-06-20 | 2025-07-14 | — | 2025-12-12 | ✅ |
| Azure Service Bus | 2022-06-29 | 2023-04-10 | — | 2025-12-13 | ✅ |
| Azure SQL Database solution for sentinel | 2022-08-19 | 2023-03-31 | — | 2025-12-13 | ✅ |
| Azure Storage | 2022-05-12 | 2024-01-18 | — | 2025-12-13 | ✅ |
| Azure Stream Analytics | 2022-06-24 | 2023-04-11 | — | 2025-12-13 | ✅ |
| Azure Web Application Firewall (WAF) | 2022-05-18 | 2023-02-16 | — | 2025-12-13 | ✅ |
| AzureDevOpsAuditing | 2022-09-20 | 2023-03-01 | — | 2026-02-17 | ✅ |
| AzureSecurityBenchmark | 2022-06-17 | 2023-04-20 | — | 2025-12-13 | ✅ |
| Barracuda CloudGen Firewall | 2021-05-02 | 2023-10-31 | — | 2025-12-13 | ✅ |
| Barracuda WAF | 2022-05-13 | — | — | — | ✅ |
| BETTER Mobile Threat Defense (MTD) | 2022-05-02 | 2024-11-08 | — | 2025-12-12 | ✅ |
| Beyond Security beSECURE | 2022-05-02 | — | — | — | ❌ |
| BeyondTrustPMCloud | 2025-10-31 | 2026-02-27 | — | 2026-02-27 | ✅ |
| BigID | 2025-10-07 | 2026-02-20 | — | 2026-03-02 | ✅ |
| Bitglass | 2021-10-23 | 2023-05-24 | — | 2025-12-13 | ✅ |
| BitSight | 2023-02-20 | 2023-10-12 | 2024-02-20 | 2026-02-26 | ✅ |
| Bitwarden | 2024-05-12 | 2024-09-30 | 2024-10-02 | 2025-12-13 | ✅ |
| Blackberry CylancePROTECT | 2022-05-20 | 2023-03-14 | — | 2025-12-13 | ✅ |
| BlinkOps | 2025-05-05 | 2025-06-18 | — | 2025-12-13 | ✅ |
| BloodHound Enterprise | 2023-05-04 | — | 2021-05-04 | — | ✅ |
| Box | 2022-05-20 | 2023-08-04 | — | 2025-12-13 | ✅ |
| Broadcom SymantecDLP | 2022-05-02 | 2023-03-16 | — | 2025-12-13 | ✅ |
| Business Email Compromise - Financial Fraud | 2023-08-04 | 2023-08-09 | — | 2025-12-13 | ✅ |
| Check Point | 2021-08-13 | 2023-04-03 | — | 2025-12-13 | ✅ |
| Check Point CloudGuard CNAPP | 2024-11-12 | 2025-01-16 | — | 2025-12-13 | ✅ |
| Check Point Cyberint Alerts | 2025-03-18 | 2025-08-14 | — | 2026-01-21 | ✅ |
| Check Point Cyberint IOC | 2025-04-29 | 2025-08-14 | — | 2025-12-13 | ✅ |
| CheckPhish by Bolster | 2022-10-12 | 2024-11-08 | — | 2025-12-13 | ✅ |
| Cisco ACI | 2021-07-03 | 2024-07-29 | — | 2025-12-13 | ✅ |
| Cisco ETD | 2024-03-04 | 2024-03-28 | — | 2025-12-13 | ✅ |
| Cisco Firepower EStreamer | 2022-05-25 | 2023-05-23 | — | 2025-12-13 | ✅ |
| Cisco ISE | 2021-07-03 | 2023-05-08 | — | 2025-12-12 | ✅ |
| Cisco Meraki Events via REST API | 2023-07-12 | 2024-04-24 | — | 2025-12-14 | ✅ |
| Cisco SD-WAN | 2023-06-01 | 2023-07-18 | 2024-06-01 | 2025-12-13 | ✅ |
| Cisco Secure Cloud Analytics | 2021-10-20 | 2024-05-16 | — | 2025-12-13 | ✅ |
| Cisco Secure Endpoint | 2021-10-28 | 2023-05-23 | 2022-02-02 | 2025-12-13 | ✅ |
| Cisco UCS | 2022-05-02 | 2023-03-17 | — | 2025-12-13 | ✅ |
| CiscoASA | 2022-05-23 | 2023-06-15 | — | 2025-12-12 | ✅ |
| CiscoDuoSecurity | 2022-01-07 | — | — | — | ✅ |
| CiscoMeraki | 2021-09-08 | 2023-03-17 | — | 2026-01-23 | ✅ |
| CiscoSEG | 2021-06-23 | 2023-10-06 | — | 2025-12-12 | ✅ |
| CiscoUmbrella | 2022-04-01 | 2023-03-23 | — | 2026-02-19 | ✅ |
| CiscoWSA | 2021-06-29 | 2024-07-30 | — | 2025-12-13 | ✅ |
| Citrix ADC | 2022-06-02 | 2023-04-06 | — | 2025-12-12 | ✅ |
| Citrix Analytics for Security | 2022-05-06 | — | — | — | ✅ |
| Citrix Web App Firewall | 2022-05-06 | 2023-02-22 | — | 2026-02-09 | ✅ |
| Claroty | 2021-10-23 | 2023-08-17 | — | 2025-12-13 | ✅ |
| Claroty xDome | 2024-02-01 | 2024-05-21 | — | 2025-12-13 | ✅ |
| Cloud Identity Threat Protection Essentials | 2022-11-16 | 2023-04-17 | — | 2025-12-13 | ✅ |
| Cloud Service Threat Protection Essentials | 2022-11-16 | 2023-04-17 | — | 2025-12-13 | ✅ |
| Cloudflare | 2021-10-20 | 2023-05-12 | — | 2025-12-13 | ✅ |
| Cloudflare CCF | 2025-09-30 | 2025-10-23 | — | 2026-02-11 | ✅ |
| CofenseIntelligence | 2023-05-26 | — | 2024-05-26 | — | ❌ |
| CofenseTriage | 2023-03-24 | — | 2023-03-24 | — | ❌ |
| Cognni | 2022-05-06 | 2024-11-08 | — | 2025-12-13 | ✅ |
| CognyteLuminar | 2023-09-15 | 2024-03-28 | — | 2025-12-13 | ✅ |
| CohesitySecurity | 2022-10-10 | 2023-02-27 | — | 2025-12-13 | ✅ |
| Common Event Format | 2022-05-30 | 2023-02-21 | — | 2025-12-13 | ✅ |
| Commvault Security IQ | 2023-08-17 | 2023-09-18 | — | 2026-02-20 | ✅ |
| ContinuousDiagnostics&Mitigation | 2022-08-24 | 2023-11-16 | — | 2025-12-13 | ✅ |
| Contrast Protect | 2021-10-20 | — | — | — | ✅ |
| ContrastADR | 2025-01-18 | 2025-10-20 | 2025-01-18 | 2026-01-22 | ✅ |
| Corelight | 2022-06-01 | 2023-11-01 | — | 2026-02-02 | ✅ |
| Cortex XDR | 2023-07-12 | 2023-08-04 | — | 2025-12-13 | ✅ |
| Cribl | 2024-08-01 | 2024-09-12 | 2024-09-05 | 2025-12-13 | ✅ |
| CrowdStrike Falcon Endpoint Protection | 2022-06-01 | 2023-03-24 | — | 2026-03-09 | ✅ |
| CTERA | 2024-07-28 | 2025-02-25 | — | 2025-12-14 | ✅ |
| CTM360 | 2023-10-23 | 2024-01-28 | — | 2026-03-09 | ✅ |
| CustomLogsAma | 2024-07-21 | 2024-08-12 | — | 2025-12-13 | ✅ |
| CyberArk Privilege Access Manager (PAM) Events | 2022-05-02 | 2024-03-12 | — | 2025-12-13 | ✅ |
| CyberArkAudit | 2024-03-01 | 2024-04-04 | — | 2026-03-05 | ✅ |
| CyberArkEPM | 2022-04-10 | — | — | — | ✅ |
| CybersecurityMaturityModelCertification(CMMC)2.0 | 2022-01-06 | 2023-04-19 | — | 2026-01-14 | ✅ |
| Cybersixgill-Actionable-Alerts | 2023-02-27 | 2023-03-14 | 2024-09-24 | 2025-12-13 | ✅ |
| Cyble Vision | 2025-05-05 | 2025-05-26 | — | 2026-01-16 | ✅ |
| Cyborg Security HUNTER | 2023-07-03 | 2023-11-27 | 2023-09-22 | 2025-12-13 | ✅ |
| CyeraDSPM | 2025-10-15 | — | 2025-10-29 | — | ❌ |
| Cyfirma Attack Surface | 2025-03-27 | 2025-05-12 | — | 2025-12-13 | ✅ |
| Cyfirma Brand Intelligence | 2025-03-27 | 2025-05-13 | — | 2025-12-13 | ✅ |
| Cyfirma Compromised Accounts | 2025-05-15 | 2025-06-18 | — | 2025-12-13 | ✅ |
| Cyfirma Cyber Intelligence | 2025-05-15 | 2025-06-18 | — | 2025-12-13 | ✅ |
| Cyfirma Digital Risk | 2025-03-27 | 2025-05-13 | — | 2025-12-13 | ✅ |
| Cyfirma Vulnerabilities Intel | 2025-05-15 | 2025-06-18 | — | 2025-12-13 | ✅ |
| Cynerio | 2023-03-29 | 2023-04-24 | 2023-03-29 | 2025-12-13 | ✅ |
| CyrenThreatIntelligence | 2025-11-16 | 2026-02-09 | — | 2026-03-02 | ✅ |
| Cyware | 2024-03-18 | 2024-07-11 | 2024-03-18 | 2025-12-13 | ✅ |
| Darktrace | 2022-05-02 | 2023-05-08 | — | 2025-12-13 | ✅ |
| Datalake2Sentinel | 2024-01-15 | 2024-02-05 | 2024-01-15 | 2025-12-13 | ✅ |
| Dataminr Pulse | 2023-04-12 | 2023-10-20 | 2023-04-12 | 2025-12-13 | ✅ |
| Datawiza | 2025-11-10 | 2026-01-15 | — | 2026-01-15 | ✅ |
| Delinea Secret Server | 2022-05-06 | 2023-09-02 | — | 2025-12-13 | ✅ |
| Dev 0270 Detection and Hunting | 2022-11-29 | 2023-02-28 | — | 2025-12-14 | ✅ |
| DEV-0537DetectionandHunting | 2022-04-07 | — | — | — | ✅ |
| Digital Guardian Data Loss Prevention | 2021-07-23 | 2023-10-17 | — | 2025-12-13 | ✅ |
| Digital Shadows | — | 2023-05-31 | — | 2025-12-14 | ✅ |
| DNS Essentials | 2023-01-14 | 2023-04-18 | — | 2025-12-13 | ✅ |
| DomainTools | 2022-10-20 | 2023-03-21 | — | 2025-12-14 | ✅ |
| Doppel | 2024-11-20 | 2025-01-28 | — | 2026-02-26 | ✅ |
| DORA Compliance | 2025-10-08 | 2026-02-27 | — | 2026-02-27 | ✅ |
| DPDP Compliance | 2026-01-26 | 2026-02-05 | — | 2026-02-06 | ✅ |
| Dragos | 2025-01-23 | 2025-02-05 | 2025-01-23 | 2025-12-12 | ✅ |
| DruvaDataSecurityCloud | 2024-12-24 | 2025-01-27 | — | 2025-12-13 | ✅ |
| Dynamics 365 | 2023-01-17 | 2023-02-28 | — | 2026-03-03 | ✅ |
| Dynatrace | 2022-10-18 | 2023-02-22 | 2023-10-16 | 2025-12-12 | ✅ |
| EatonForeseer | 2022-06-28 | 2023-04-10 | — | 2025-12-13 | ✅ |
| EclecticIQ | 2022-09-30 | 2023-04-28 | — | 2025-12-13 | ✅ |
| Egress Defend | 2023-07-27 | — | — | — | ❌ |
| Egress Iris | 2024-03-11 | — | — | — | ✅ |
| Elastic Search | 2022-09-30 | — | — | — | ❌ |
| ElasticAgent | 2021-11-12 | 2023-04-10 | — | 2025-12-13 | ✅ |
| Endace | 2025-03-24 | 2025-12-16 | — | 2026-01-27 | ✅ |
| Endpoint Threat Protection Essentials | 2022-11-16 | 2023-03-17 | — | 2026-02-19 | ✅ |
| Entrust identity as Service | 2023-05-22 | 2023-07-13 | — | 2025-12-13 | ✅ |
| Ermes Browser Security | 2023-09-29 | 2023-12-04 | — | 2025-12-17 | ✅ |
| ESET Inspect | 2022-06-01 | — | — | — | ✅ |
| ESET Protect Platform | 2024-10-29 | — | 2025-06-17 | — | ❌ |
| Eset Security Management Center | 2022-05-11 | — | — | — | ❌ |
| ESETPROTECT | 2021-10-20 | — | — | — | ✅ |
| Exabeam Advanced Analytics | 2022-05-20 | 2023-03-20 | — | 2025-12-13 | ✅ |
| ExtraHop | 2025-02-11 | 2025-07-10 | 2025-06-04 | 2025-12-13 | ✅ |
| ExtraHop Reveal(x) | 2022-05-19 | 2024-09-03 | — | 2025-12-13 | ✅ |
| F5 Big-IP | 2022-05-25 | 2023-04-08 | — | 2025-12-13 | ✅ |
| F5 Networks | 2022-05-12 | 2023-04-08 | — | 2025-12-13 | ✅ |
| FalconFriday | 2021-10-18 | 2024-11-08 | — | 2026-03-09 | ✅ |
| Farsight DNSDB | — | — | — | — | ✅ |
| Feedly | 2023-08-01 | 2023-09-29 | — | 2026-03-02 | ✅ |
| FireEye Network Security | 2022-06-01 | 2023-09-04 | — | 2025-12-13 | ✅ |
| Flare | 2021-10-20 | 2023-03-08 | — | 2026-02-10 | ✅ |
| Forcepoint CASB | 2022-05-19 | 2023-07-11 | — | 2025-12-12 | ✅ |
| Forcepoint CSG | 2022-05-10 | 2023-07-11 | — | 2025-12-13 | ✅ |
| Forcepoint DLP | 2022-05-09 | 2024-11-08 | — | 2025-12-13 | ✅ |
| Forcepoint NGFW | 2022-05-25 | 2023-07-11 | — | 2025-12-13 | ✅ |
| Forescout (Legacy) | 2022-06-01 | 2023-06-21 | — | 2025-12-13 | ✅ |
| Forescout eyeInspect for OT Security | 2025-07-10 | — | — | — | ❌ |
| ForescoutHostPropertyMonitor | 2022-06-28 | 2024-02-08 | — | 2025-12-13 | ✅ |
| ForgeRock Common Audit for CEF | 2022-05-04 | — | — | — | ❌ |
| Fortinet FortiGate Next-Generation Firewall connector for Microsoft Sentinel | 2021-08-13 | 2023-04-20 | — | 2025-12-12 | ✅ |
| Fortinet FortiNDR Cloud | 2024-01-15 | 2024-03-11 | — | 2025-12-13 | ✅ |
| Fortinet FortiWeb Cloud WAF-as-a-Service connector for Microsoft Sentinel | 2022-05-23 | 2023-04-27 | — | 2025-12-13 | ✅ |
| Garrison ULTRA | 2024-10-04 | 2025-01-23 | — | 2025-12-13 | ✅ |
| GDPR Compliance & Data Security | 2025-10-08 | 2025-11-13 | — | 2025-12-18 | ✅ |
| Gigamon Connector | — | 2023-11-21 | — | 2026-03-06 | ✅ |
| GitHub | 2021-10-18 | 2023-05-16 | — | 2026-02-04 | ✅ |
| GitLab | 2022-04-27 | 2023-11-22 | 2022-06-27 | 2025-12-13 | ✅ |
| Global Secure Access | 2024-04-08 | 2024-09-30 | — | 2026-03-02 | ✅ |
| Google Apigee | 2021-10-28 | 2023-03-06 | — | 2025-12-12 | ✅ |
| Google Cloud Platform Audit Logs | 2023-03-29 | 2023-03-29 | — | 2026-01-29 | ✅ |
| Google Cloud Platform BigQuery | 2023-03-02 | 2023-07-12 | — | 2025-12-13 | ✅ |
| Google Cloud Platform Cloud Monitoring | 2022-07-01 | 2023-03-06 | — | 2026-02-17 | ✅ |
| Google Cloud Platform Cloud Run | 2021-07-30 | 2025-07-22 | — | 2025-12-13 | ✅ |
| Google Cloud Platform Compute Engine | 2022-07-07 | 2025-07-18 | — | 2025-12-13 | ✅ |
| Google Cloud Platform Firewall Logs | 2024-11-03 | 2024-11-26 | — | 2025-12-12 | ✅ |
| Google Cloud Platform Load Balancer Logs | 2025-02-12 | 2025-02-25 | — | 2025-12-12 | ✅ |
| Google Cloud Platform Security Command Center | 2023-09-11 | 2024-02-08 | — | 2025-12-13 | ✅ |
| Google Cloud Platform VPC Flow Logs | 2025-02-12 | 2025-05-21 | — | 2025-12-13 | ✅ |
| Google Kubernetes Engine | 2025-04-04 | 2025-08-06 | — | 2026-03-06 | ✅ |
| Google Threat Intelligence | 2024-10-26 | 2024-12-13 | 2024-10-26 | 2025-12-12 | ✅ |
| GoogleCloudPlatformCDN | 2025-03-07 | 2025-06-19 | — | 2025-12-13 | ✅ |
| GoogleCloudPlatformDNS | 2022-07-07 | 2023-03-06 | — | 2025-12-13 | ✅ |
| GoogleCloudPlatformIAM | 2021-07-30 | 2023-05-23 | — | 2025-12-18 | ✅ |
| GoogleCloudPlatformIDS | 2022-07-07 | 2025-06-19 | — | 2025-12-13 | ✅ |
| GoogleCloudPlatformNAT | 2025-05-29 | 2025-07-23 | — | 2025-12-13 | ✅ |
| GoogleCloudPlatformResourceManager | 2025-03-07 | 2025-07-18 | — | 2025-12-13 | ✅ |
| GoogleCloudPlatformSQL | 2021-07-30 | 2025-07-22 | — | 2025-12-13 | ✅ |
| GoogleDirectory | — | — | — | — | ❌ |
| GoogleWorkspaceReports | 2022-01-24 | 2023-03-06 | — | 2026-02-17 | ✅ |
| GreyNoiseThreatIntelligence | 2023-09-05 | 2023-10-17 | 2025-07-28 | 2025-12-13 | ✅ |
| Group-IB | — | — | — | — | ❌ |
| Halcyon | 2025-12-22 | 2026-01-22 | 2025-12-22 | 2026-01-22 | ✅ |
| HIPAA Compliance | 2025-10-08 | 2025-11-13 | — | 2025-12-13 | ✅ |
| HolmSecurity | 2022-07-18 | 2023-09-29 | — | 2025-12-13 | ✅ |
| HoneyTokens | — | — | — | — | ❌ |
| HYAS | 2021-10-20 | 2024-02-28 | — | 2025-12-13 | ✅ |
| HYAS Protect | 2023-09-26 | — | — | — | ✅ |
| iboss | 2022-02-15 | 2023-08-20 | — | 2026-02-09 | ✅ |
| Illumio Core | 2022-05-26 | — | — | — | ✅ |
| Illumio Insight | 2025-08-10 | 2025-09-17 | — | 2025-12-14 | ✅ |
| IllumioSaaS | 2024-05-13 | 2024-07-08 | — | 2025-12-13 | ✅ |
| Illusive Active Defense | — | — | — | — | ❌ |
| Illusive Platform | 2022-05-25 | 2024-11-08 | — | 2025-12-13 | ✅ |
| Imperva WAF Gateway | 2022-05-02 | — | — | — | ❌ |
| ImpervaCloudWAF | 2021-09-28 | 2023-05-30 | — | 2025-12-13 | ✅ |
| Infoblox | 2024-07-15 | 2024-09-25 | 2024-07-15 | 2025-12-13 | ✅ |
| Infoblox Cloud Data Connector | 2021-10-20 | — | — | — | ✅ |
| Infoblox NIOS | 2022-04-01 | 2023-03-14 | — | 2025-12-13 | ✅ |
| Infoblox SOC Insights | 2024-03-06 | — | — | — | ❌ |
| InsightVM | — | — | — | — | ❌ |
| Integration for Atlassian Beacon | 2023-09-22 | 2023-10-26 | — | 2025-12-14 | ✅ |
| Intel471 | 2023-06-21 | — | — | — | ✅ |
| IONIX | 2022-05-02 | 2024-11-08 | — | 2025-12-13 | ✅ |
| IoTOTThreatMonitoringwithDefenderforIoT | 2021-10-26 | 2023-02-17 | — | 2025-12-13 | ✅ |
| IPinfo | 2024-05-02 | — | — | — | ❌ |
| IPQualityScore | 2021-10-20 | 2023-05-18 | — | 2025-12-13 | ✅ |
| IronNet IronDefense | 2021-10-18 | — | — | — | ❌ |
| ISC Bind | 2022-09-20 | 2023-03-16 | — | 2025-12-13 | ✅ |
| Island | 2023-05-02 | 2023-05-17 | 2023-07-20 | 2025-12-13 | ✅ |
| Ivanti Unified Endpoint Management | 2022-07-05 | 2024-07-31 | — | 2025-12-13 | ✅ |
| Jamf Protect | 2022-10-10 | 2023-02-21 | 2025-09-02 | 2025-12-13 | ✅ |
| JBoss | 2021-10-20 | 2024-08-21 | — | 2025-12-13 | ✅ |
| JoeSandbox | 2025-09-12 | 2026-02-10 | — | 2026-02-18 | ✅ |
| Joshua-Cyberiskvision | 2022-01-10 | 2024-11-08 | 2022-01-10 | 2025-12-13 | ✅ |
| Juniper SRX | 2022-05-02 | 2023-03-14 | — | 2025-12-13 | ✅ |
| JuniperIDP | 2021-03-31 | 2024-08-20 | — | 2025-12-13 | ✅ |
| Keeper Security | 2025-06-03 | 2025-06-30 | 2025-06-03 | 2025-12-13 | ✅ |
| KQL Training | 2022-11-30 | 2023-09-12 | — | 2025-12-13 | ✅ |
| Lastpass Enterprise Activity Monitoring | 2021-10-20 | 2024-11-08 | 2022-01-12 | 2025-12-12 | ✅ |
| Legacy IOC based Threat Protection | 2022-12-19 | 2023-02-23 | — | 2025-12-13 | ✅ |
| Lookout | 2021-10-18 | 2024-11-08 | 2025-12-18 | 2026-01-13 | ✅ |
| Lookout Cloud Security Platform for Microsoft Sentinel | 2023-02-17 | — | — | — | ✅ |
| Lumen Defender Threat Feed | 2025-09-12 | — | 2025-09-12 | — | ✅ |
| MailGuard 365 | 2023-05-09 | 2023-09-18 | 2023-06-08 | 2025-12-13 | ✅ |
| MailRisk | 2023-03-16 | 2023-07-06 | 2025-10-27 | 2026-02-17 | ✅ |
| Malware Protection Essentials | 2023-09-25 | 2024-05-17 | 2023-09-25 | 2025-12-13 | ✅ |
| MarkLogicAudit | 2022-08-01 | 2023-03-06 | — | 2025-12-13 | ✅ |
| MaturityModelForEventLogManagementM2131 | 2021-12-05 | 2023-03-30 | — | 2025-12-13 | ✅ |
| McAfee ePolicy Orchestrator | 2021-03-25 | — | — | — | ✅ |
| McAfee Network Security Platform | 2021-06-29 | — | — | — | ✅ |
| meshStack | 2025-12-15 | — | — | — | ❌ |
| Microsoft 365 | 2022-05-23 | 2023-02-20 | — | 2025-12-13 | ✅ |
| Microsoft 365 Assets | 2025-06-20 | — | — | — | ✅ |
| Microsoft Business Applications | 2023-04-19 | 2024-01-03 | — | 2026-02-25 | ✅ |
| Microsoft Copilot | 2025-10-01 | 2025-09-15 | — | 2026-01-30 | ✅ |
| Microsoft Defender for Cloud | 2022-05-17 | 2023-05-16 | — | 2025-12-13 | ✅ |
| Microsoft Defender for Cloud Apps | 2022-05-02 | 2023-04-25 | — | 2025-12-13 | ✅ |
| Microsoft Defender for Identity | 2022-04-20 | 2023-03-02 | — | 2025-12-13 | ✅ |
| Microsoft Defender for Office 365 | 2022-05-17 | 2023-09-06 | — | 2025-12-13 | ✅ |
| Microsoft Defender Threat Intelligence | 2023-03-23 | 2023-03-27 | — | 2025-12-13 | ✅ |
| Microsoft Defender XDR | 2022-05-02 | 2023-02-21 | — | 2026-01-23 | ✅ |
| Microsoft Entra ID | 2022-05-16 | 2023-02-20 | — | 2026-02-24 | ✅ |
| Microsoft Entra ID Assets | 2025-06-20 | 2025-09-26 | — | 2025-12-13 | ✅ |
| Microsoft Entra ID Protection | 2022-05-18 | 2023-02-24 | — | 2025-12-13 | ✅ |
| Microsoft Exchange Security - Exchange On-Premises | 2022-12-21 | 2023-07-04 | — | 2025-12-13 | ✅ |
| Microsoft Exchange Security - Exchange Online | 2022-12-21 | 2023-07-04 | — | 2025-12-13 | ✅ |
| Microsoft PowerBI | 2022-05-23 | 2023-03-23 | — | 2025-12-14 | ✅ |
| Microsoft Project | 2022-05-23 | 2023-07-11 | — | 2025-12-14 | ✅ |
| Microsoft Purview | 2021-11-23 | 2023-02-16 | — | 2025-12-13 | ✅ |
| Microsoft Purview Information Protection | 2023-01-06 | 2023-03-02 | — | 2025-12-13 | ✅ |
| Microsoft Sysmon For Linux | 2021-10-27 | 2023-04-20 | — | 2025-12-12 | ✅ |
| Microsoft Windows SQL Server Database Audit | 2022-11-29 | 2023-07-14 | — | 2025-12-13 | ✅ |
| MicrosoftDefenderForEndpoint | 2022-01-31 | 2023-03-03 | — | 2025-12-14 | ✅ |
| MicrosoftPurviewInsiderRiskManagement | 2021-10-20 | 2023-03-02 | — | 2025-12-13 | ✅ |
| Mimecast | 2024-09-10 | 2024-11-21 | 2024-09-10 | 2025-12-13 | ✅ |
| MimecastAudit | 2022-02-24 | 2023-10-18 | 2022-02-24 | 2025-12-13 | ✅ |
| MimecastSEG | 2022-02-24 | 2023-10-18 | 2022-02-24 | 2025-12-13 | ✅ |
| MimecastTIRegional | 2023-08-23 | 2023-10-23 | 2023-09-11 | 2025-12-13 | ✅ |
| MimecastTTP | 2022-02-24 | 2023-10-18 | 2022-02-24 | 2025-12-13 | ✅ |
| Minemeld | 2022-10-11 | 2024-04-04 | — | 2025-12-13 | ✅ |
| Miro | — | 2025-12-24 | — | 2026-01-08 | ✅ |
| MISP2Sentinel | 2023-07-29 | 2023-08-22 | 2023-07-29 | 2025-12-13 | ✅ |
| MongoDBAtlas | 2025-08-22 | 2025-11-03 | — | 2025-12-13 | ✅ |
| MongoDBAudit | 2022-06-01 | 2023-03-06 | — | 2025-12-12 | ✅ |
| Morphisec | 2022-05-05 | 2024-11-08 | — | 2025-12-13 | ✅ |
| Mulesoft | 2022-07-12 | 2023-05-26 | — | 2025-12-13 | ✅ |
| Multi Cloud Attack Coverage Essentials - Resource Abuse | 2023-11-22 | 2023-11-29 | — | 2025-12-13 | ✅ |
| Nasuni | 2023-07-07 | 2023-07-19 | 2023-07-07 | 2025-12-13 | ✅ |
| NC Protect Data Connector | 2021-10-20 | 2023-06-01 | — | 2025-12-13 | ✅ |
| NCSC-NL NDN Cyber Threat Intelligence Sharing | 2025-05-19 | 2025-07-10 | — | 2025-12-13 | ✅ |
| NetClean ProActive | 2022-06-30 | — | — | — | ✅ |
| Netskope | 2022-05-05 | 2023-07-21 | — | 2025-12-13 | ✅ |
| Netskopev2 | 2024-03-18 | 2023-07-21 | 2024-03-18 | 2025-12-13 | ✅ |
| Network Session Essentials | 2022-11-11 | 2023-03-21 | 2022-11-11 | 2026-02-09 | ✅ |
| Network Threat Protection Essentials | 2022-11-16 | 2023-04-13 | — | 2026-01-30 | ✅ |
| Netwrix Auditor | 2022-06-17 | 2023-04-11 | — | 2025-12-13 | ✅ |
| Neustar IP GeoPoint | 2022-09-30 | 2024-11-08 | 2022-09-30 | 2025-12-13 | ✅ |
| NGINX HTTP Server | 2021-12-16 | 2023-04-06 | — | 2025-12-13 | ✅ |
| NISTSP80053 | 2022-02-24 | 2023-04-19 | — | 2026-01-22 | ✅ |
| Noname API Security Solution for Microsoft Sentinel | 2022-12-01 | — | — | — | ✅ |
| NordPass | 2025-04-22 | 2025-06-27 | — | 2026-02-23 | ✅ |
| NozomiNetworks | 2022-07-12 | 2023-09-14 | — | 2025-12-13 | ✅ |
| NXLog BSM macOS | 2022-05-02 | — | — | — | ✅ |
| NXLog FIM | 2022-08-15 | — | — | — | ✅ |
| NXLog LinuxAudit | 2022-05-05 | — | — | — | ✅ |
| NXLogAixAudit | 2022-05-05 | — | — | — | ✅ |
| NXLogDNSLogs | 2022-05-24 | — | — | — | ✅ |
| Obsidian Datasharing | 2024-01-01 | 2025-09-30 | — | 2025-12-17 | ✅ |
| Okta Single Sign-On | 2022-03-24 | 2023-07-11 | — | 2026-01-14 | ✅ |
| Onapsis Defend | 2025-07-17 | 2025-08-25 | 2025-07-17 | 2025-12-13 | ✅ |
| Onapsis Platform | 2022-05-11 | — | — | — | ❌ |
| OneIdentity | 2022-05-02 | — | — | — | ✅ |
| OneLoginIAM | 2022-08-18 | 2023-05-26 | — | 2025-12-13 | ✅ |
| OneTrust | 2025-10-24 | 2025-11-13 | 2025-10-24 | 2025-12-13 | ✅ |
| Open Systems | 2025-05-12 | 2025-11-28 | — | 2025-12-13 | ✅ |
| OpenCTI | 2022-09-22 | 2024-11-08 | 2022-09-22 | 2025-12-13 | ✅ |
| OpenVPN | 2022-08-18 | 2023-04-05 | — | 2025-12-13 | ✅ |
| Oracle Cloud Infrastructure | 2022-06-01 | 2023-05-31 | — | 2026-02-11 | ✅ |
| OracleDatabaseAudit | 2021-11-05 | 2023-03-21 | — | 2025-12-13 | ✅ |
| OracleWebLogicServer | 2022-01-06 | 2023-04-06 | — | 2025-12-13 | ✅ |
| Orca Security Alerts | 2022-05-10 | 2024-11-08 | — | 2025-12-13 | ✅ |
| OSSEC | 2022-05-19 | 2023-03-20 | — | 2025-12-13 | ✅ |
| Palo Alto - XDR (Cortex) | — | — | — | — | ❌ |
| Palo Alto Cortex XDR CCP | 2024-12-07 | 2024-12-19 | — | 2025-12-13 | ✅ |
| Palo Alto Cortex Xpanse CCF | 2024-12-07 | 2025-08-07 | — | 2025-12-13 | ✅ |
| Palo Alto Prisma Cloud CWPP | 2022-06-24 | 2023-11-07 | — | 2025-12-13 | ✅ |
| PaloAlto-PAN-OS | 2021-08-09 | 2023-03-07 | 2021-09-20 | 2026-01-14 | ✅ |
| PaloAltoCDL | 2021-10-23 | 2023-03-08 | — | 2025-12-13 | ✅ |
| PaloAltoPrismaCloud | 2021-04-16 | 2023-03-08 | — | 2025-12-13 | ✅ |
| Pathlock_TDnR | 2022-02-17 | 2025-11-12 | — | 2025-12-13 | ✅ |
| PCI DSS Compliance | 2022-06-29 | 2024-10-17 | — | 2025-12-13 | ✅ |
| PDNS Block Data Connector | 2023-03-31 | — | — | — | ❌ |
| Perimeter 81 | 2022-05-06 | 2023-03-21 | — | 2025-12-14 | ✅ |
| Phosphorus | 2024-08-13 | 2024-08-31 | 2024-08-13 | 2025-12-14 | ✅ |
| PingFederate | 2022-06-01 | 2023-09-08 | — | 2025-12-13 | ✅ |
| PingOne | 2025-04-20 | 2025-06-24 | 2025-04-20 | 2025-12-13 | ✅ |
| PostgreSQL | 2022-06-27 | 2024-08-16 | — | 2025-12-13 | ✅ |
| Power Platform | — | — | — | — | ❌ |
| Prancer PenSuiteAI Integration | 2023-08-02 | 2023-11-01 | — | 2025-12-12 | ✅ |
| Proofpoint On demand(POD) Email Security | 2021-03-31 | 2025-09-10 | — | 2025-12-23 | ✅ |
| ProofPointTap | 2022-05-23 | 2025-09-10 | — | 2025-12-13 | ✅ |
| Pulse Connect Secure | 2022-05-02 | 2023-03-28 | — | 2025-12-13 | ✅ |
| Pure Storage | 2024-02-05 | 2024-03-04 | — | 2025-12-13 | ✅ |
| Qualys VM Knowledgebase | 2022-05-17 | 2023-03-28 | — | 2025-12-13 | ✅ |
| QualysVM | 2020-12-14 | 2023-06-12 | 2025-11-18 | 2025-12-13 | ✅ |
| Quokka | 2025-10-30 | 2025-11-25 | — | 2026-02-02 | ✅ |
| Radiflow | 2024-06-26 | 2024-07-26 | — | 2025-12-12 | ✅ |
| Rapid7InsightVM | 2021-07-07 | 2023-05-26 | — | 2025-12-13 | ✅ |
| Recorded Future | 2021-11-01 | 2023-02-20 | 2023-09-19 | 2025-12-13 | ✅ |
| Recorded Future Identity | 2022-09-06 | 2024-07-09 | 2025-04-02 | 2025-12-13 | ✅ |
| Red Canary | 2022-03-04 | — | 2022-03-04 | — | ✅ |
| ReversingLabs | 2022-08-08 | 2023-02-27 | 2024-07-17 | 2025-12-13 | ✅ |
| RidgeSecurity | 2023-10-23 | 2023-12-13 | 2023-10-23 | 2025-12-13 | ✅ |
| RiskIQ | 2021-10-20 | 2024-11-08 | — | 2026-01-21 | ✅ |
| RSA SecurID | 2021-09-07 | 2023-04-11 | — | 2025-12-13 | ✅ |
| RSAIDPlus_AdminLogs_Connector | 2025-10-14 | 2025-10-27 | — | 2025-12-13 | ✅ |
| RubrikSecurityCloud | 2022-07-19 | 2023-04-17 | 2025-07-25 | 2025-12-14 | ✅ |
| SailPointIdentityNow | 2021-10-26 | 2024-03-25 | — | 2025-12-13 | ✅ |
| SalemCyber | 2023-07-21 | — | 2023-07-21 | — | ❌ |
| Salesforce Service Cloud | 2022-05-16 | 2023-04-25 | — | 2026-01-27 | ✅ |
| Samsung Knox Asset Intelligence | 2025-01-15 | 2025-04-24 | — | 2025-12-13 | ✅ |
| SAP | — | — | — | — | ❌ |
| SAP BTP | 2023-04-04 | 2023-05-04 | — | 2026-02-02 | ✅ |
| SAP ETD Cloud | 2025-02-17 | 2025-03-04 | 2025-09-11 | 2025-12-13 | ✅ |
| SAP LogServ | 2025-02-17 | 2025-03-07 | 2025-07-18 | 2025-12-13 | ✅ |
| SAP S4 Cloud Public Edition | 2025-09-12 | 2025-10-13 | — | 2025-12-13 | ✅ |
| SecurityBridge App | 2022-02-17 | 2024-03-13 | — | 2025-12-13 | ✅ |
| SecurityScorecard Cybersecurity Ratings | 2022-10-01 | — | 2022-10-01 | — | ✅ |
| SecurityThreatEssentialSolution | 2022-03-30 | 2023-03-17 | — | 2025-12-12 | ✅ |
| Semperis Directory Services Protector | 2021-10-18 | — | — | — | ✅ |
| SenservaPro | 2022-06-01 | — | — | — | ✅ |
| SentinelOne | 2024-11-26 | 2023-03-13 | — | 2026-01-12 | ✅ |
| SentinelSOARessentials | 2022-06-27 | 2023-07-04 | — | 2026-01-15 | ✅ |
| SeraphicSecurity | 2023-07-31 | 2023-12-18 | 2023-07-31 | 2025-12-13 | ✅ |
| Servicenow | 2022-09-19 | 2023-04-19 | — | 2025-12-13 | ✅ |
| ServiceNow TISC | 2025-01-15 | 2025-02-06 | 2025-01-15 | 2025-12-13 | ✅ |
| SevcoSecurity | 2023-05-01 | — | — | — | ❌ |
| ShadowByte Aria | 2021-12-24 | 2024-11-08 | — | 2025-12-13 | ✅ |
| Shodan | 2023-02-20 | 2023-07-12 | — | 2025-12-13 | ✅ |
| SIGNL4 | 2021-12-10 | 2023-05-04 | 2021-12-10 | 2025-12-13 | ✅ |
| Silverfort | 2024-09-01 | 2024-09-26 | — | 2025-12-13 | ✅ |
| SINEC Security Guard | 2024-07-15 | — | — | — | ✅ |
| SlackAudit | 2021-03-24 | 2023-08-25 | — | 2025-12-17 | ✅ |
| SlashNext | 2022-08-12 | — | 2022-08-12 | — | ✅ |
| SlashNext SIEM | 2023-05-26 | — | 2023-06-16 | — | ✅ |
| Snowflake | 2021-10-23 | 2023-09-12 | — | 2026-02-04 | ✅ |
| SOC Handbook | 2022-11-30 | 2023-06-08 | — | 2026-01-15 | ✅ |
| SOC Prime CCF | 2025-09-25 | 2025-12-26 | — | 2026-01-07 | ✅ |
| SOC-Process-Framework | 2022-04-08 | 2023-03-02 | — | 2025-12-13 | ✅ |
| SonicWall Firewall | 2022-05-06 | 2023-02-14 | — | 2025-12-13 | ✅ |
| SonraiSecurity | 2021-10-18 | 2023-08-16 | — | 2025-12-13 | ✅ |
| Sophos Cloud Optix | 2022-05-02 | 2024-07-03 | — | 2025-12-13 | ✅ |
| Sophos Endpoint Protection | 2021-07-07 | 2023-08-22 | — | 2025-12-12 | ✅ |
| Sophos XG Firewall | 2021-10-20 | 2023-03-21 | — | 2025-12-12 | ✅ |
| SOX IT Compliance | 2025-12-11 | 2025-12-18 | — | 2025-12-19 | ✅ |
| SpyCloud Enterprise Protection | 2023-09-09 | 2023-10-06 | — | 2025-12-13 | ✅ |
| Squadra Technologies SecRmm | 2022-05-09 | — | — | — | ✅ |
| SquidProxy | 2022-05-16 | 2023-03-24 | — | 2025-12-13 | ✅ |
| Styx Intelligence | 2025-02-07 | — | — | — | ❌ |
| Symantec Endpoint Protection | 2022-07-01 | 2023-03-24 | — | 2025-12-13 | ✅ |
| Symantec Integrated Cyber Defense | 2022-06-02 | 2023-07-11 | — | 2025-12-13 | ✅ |
| Symantec VIP | 2022-05-16 | 2023-03-24 | — | 2025-12-13 | ✅ |
| SymantecProxySG | 2021-05-25 | 2023-03-21 | — | 2025-12-13 | ✅ |
| Synack | — | — | — | — | ✅ |
| Syslog | 2022-05-23 | 2023-02-21 | — | 2025-12-13 | ✅ |
| TacitRed-Defender-ThreatIntelligence | 2025-11-10 | 2026-02-06 | — | 2026-02-13 | ✅ |
| TacitRed-IOC-CrowdStrike | 2025-11-25 | 2026-02-10 | — | 2026-02-10 | ✅ |
| TacitRed-SentinelOne | 2025-12-01 | 2026-02-10 | 2025-12-10 | 2026-03-09 | ✅ |
| TacitRedThreatIntelligence | 2025-01-01 | 2026-02-09 | — | 2026-02-09 | ✅ |
| Talon | 2023-01-25 | 2023-03-01 | — | 2025-12-12 | ✅ |
| Tanium | 2022-05-16 | 2023-05-26 | 2025-07-03 | 2025-12-13 | ✅ |
| Team Cymru Scout | 2024-07-16 | 2025-03-20 | 2025-05-16 | 2025-12-14 | ✅ |
| Teams | 2022-02-01 | 2023-06-20 | — | 2025-12-13 | ✅ |
| Tenable App | 2024-06-06 | 2024-07-08 | 2025-06-19 | 2025-12-13 | ✅ |
| TenableAD | — | — | — | — | ❌ |
| TenableIO | 2022-06-01 | 2024-07-08 | — | 2025-12-13 | ✅ |
| TestSolution | — | — | — | — | ❌ |
| TheHive | 2021-10-23 | 2023-09-19 | — | 2025-12-13 | ✅ |
| Theom | 2022-11-04 | 2023-03-07 | — | 2025-12-13 | ✅ |
| Threat Intelligence | 2022-05-18 | 2023-03-21 | — | 2026-01-27 | ✅ |
| Threat Intelligence (NEW) | 2025-04-02 | 2025-04-04 | — | 2026-02-20 | ✅ |
| Threat Intelligence Solution for Azure Government | 2023-03-06 | — | — | — | ❌ |
| ThreatAnalysis&Response | 2021-10-20 | 2023-11-21 | — | 2025-12-12 | ✅ |
| ThreatConnect | 2023-09-11 | 2023-10-18 | 2023-09-11 | 2025-12-13 | ✅ |
| ThreatXCloud | 2022-09-23 | 2024-11-08 | 2022-09-23 | 2025-12-13 | ✅ |
| Tomcat | 2022-01-31 | 2023-04-06 | — | 2025-12-14 | ✅ |
| Torq | 2024-12-24 | 2024-12-27 | — | 2025-12-13 | ✅ |
| TransmitSecurity | 2024-06-10 | 2024-07-16 | 2024-11-20 | 2025-12-13 | ✅ |
| Trend Micro Apex One | 2021-07-06 | 2023-10-04 | 2022-03-24 | 2025-12-13 | ✅ |
| Trend Micro Cloud App Security | 2021-09-28 | — | — | — | ✅ |
| Trend Micro Deep Security | 2022-05-10 | 2024-08-27 | — | 2025-12-13 | ✅ |
| Trend Micro TippingPoint | 2022-05-02 | 2024-08-27 | — | 2025-12-13 | ✅ |
| Trend Micro Vision One | 2022-05-11 | 2023-03-01 | 2024-07-16 | 2025-12-13 | ✅ |
| Tropico | 2025-12-02 | 2025-12-22 | — | 2025-12-22 | ✅ |
| Ubiquiti UniFi | 2022-06-01 | 2024-01-23 | — | 2026-01-12 | ✅ |
| UEBA Essentials | 2022-06-27 | 2023-05-16 | — | 2026-02-11 | ✅ |
| URLhaus | 2022-09-29 | 2024-01-12 | — | 2025-12-13 | ✅ |
| Valence Security | 2023-11-20 | 2023-12-12 | — | 2025-12-13 | ✅ |
| vArmour Application Controller | 2022-06-01 | 2023-02-22 | — | 2025-12-13 | ✅ |
| Varonis Purview | 2025-10-27 | 2025-11-25 | 2025-10-01 | 2025-12-13 | ✅ |
| VaronisSaaS | 2023-11-10 | 2024-10-16 | 2023-11-10 | 2025-12-19 | ✅ |
| Vectra AI Detect | 2022-05-24 | 2023-03-31 | 2023-04-17 | 2025-12-13 | ✅ |
| Vectra AI Stream | 2021-10-18 | 2023-02-28 | 2024-05-02 | 2025-12-13 | ✅ |
| Vectra XDR | 2023-07-04 | 2023-08-07 | 2024-08-01 | 2025-12-13 | ✅ |
| Veeam | 2025-08-26 | 2025-10-23 | — | 2025-12-13 | ✅ |
| Veritas NetBackup | 2023-09-25 | 2024-11-19 | — | 2025-12-13 | ✅ |
| VersasecCMS | — | 2026-02-03 | — | 2026-02-12 | ✅ |
| VirtualMetric DataStream | 2025-09-15 | 2025-10-08 | — | 2025-12-13 | ✅ |
| VirusTotal | 2022-07-31 | 2023-03-03 | — | 2025-12-13 | ✅ |
| VMRay | 2025-07-23 | 2025-09-25 | — | 2025-12-13 | ✅ |
| VMware Carbon Black Cloud | 2022-06-01 | 2023-06-30 | — | 2026-01-30 | ✅ |
| VMware SASE | 2023-12-31 | — | — | — | ❌ |
| VMware vCenter | 2022-06-29 | 2023-03-24 | — | 2025-12-13 | ✅ |
| VMWareESXi | 2022-01-12 | 2023-03-21 | — | 2026-01-07 | ✅ |
| Votiro | — | — | — | — | ❌ |
| Watchguard Firebox | 2022-05-06 | 2024-06-06 | — | 2025-12-13 | ✅ |
| Watchlists Utilities | 2022-05-23 | 2024-11-08 | — | 2025-12-13 | ✅ |
| Web Session Essentials | 2023-06-29 | 2023-09-26 | — | 2025-12-13 | ✅ |
| Web Shells Threat Protection | 2022-05-22 | 2023-07-13 | — | 2025-12-13 | ✅ |
| Windows Firewall | 2022-05-02 | 2023-07-24 | — | 2025-12-13 | ✅ |
| Windows Forwarded Events | 2022-05-02 | 2023-02-22 | — | 2025-12-14 | ✅ |
| Windows Security Events | 2022-05-23 | 2023-03-01 | — | 2026-02-25 | ✅ |
| Windows Server DNS | 2022-05-11 | 2023-02-23 | — | 2025-12-13 | ✅ |
| WireX Network Forensics Platform | 2022-05-06 | 2023-05-24 | — | 2025-12-13 | ✅ |
| WithSecureElementsViaConnector | 2022-11-03 | — | 2022-11-03 | — | ❌ |
| WithSecureElementsViaFunction | 2024-02-22 | 2024-03-04 | 2025-04-25 | 2026-03-06 | ✅ |
| Wiz | 2023-06-20 | 2023-08-28 | — | 2025-12-13 | ✅ |
| Workday | 2024-02-15 | 2024-03-21 | — | 2026-02-17 | ✅ |
| Workplace from Facebook | 2022-05-18 | 2023-04-18 | — | 2025-12-13 | ✅ |
| ZeroFox | 2023-07-28 | 2024-04-26 | — | 2025-12-13 | ✅ |
| ZeroNetworks | 2022-06-06 | 2023-02-21 | 2025-09-17 | 2025-12-13 | ✅ |
| ZeroTrust(TIC3.0) | 2021-10-20 | 2023-04-20 | — | 2026-01-22 | ✅ |
| Zimperium Mobile Threat Defense | 2022-05-02 | 2024-11-08 | — | 2025-12-13 | ✅ |
| Zinc Open Source | 2022-10-03 | 2023-05-12 | — | 2025-12-13 | ✅ |
| ZoomReports | 2022-05-23 | 2023-07-17 | — | 2025-12-13 | ✅ |
| Zscaler Internet Access | 2022-05-25 | 2024-08-05 | — | 2025-12-13 | ✅ |
| Zscaler Private Access (ZPA) | 2022-01-31 | 2023-03-29 | — | 2026-01-15 | ✅ |
