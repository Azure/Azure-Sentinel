# Microsoft Learn data-connectors-reference audit

Generated **2026-05-22 06:59 UTC** against `https://learn.microsoft.com/azure/sentinel/data-connectors-reference`

- Learn sections parsed: **342**
- Published, non-deprecated solutions: **469**
- Active connectors in those solutions: **415**

## 1. Connector coverage gaps

**76** total gaps — **74** active connectors not on Learn, **2** Learn entries not covered by any active connector (an additional **8** Learn entries are covered only by a deprecated connector and are suppressed). See [`connector_coverage_gaps.csv`](connector_coverage_gaps.csv).

### 1a. Active connectors missing from Learn

| Title | Solution | Published | Collection method | Docs |
|---|---|---|---|---|
| [Recommended] Vectra AI Stream via AMA | Vectra AI Stream | 2024-05-02 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/vectrastreamama.html) |
| Abnormal Security (Push) | AbnormalSecurity | 2026-02-17 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/abnormalsecuritypush.html) |
| AI Vectra Stream via Legacy Agent | Vectra AI Stream | 2024-05-02 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/aivectrastream.html) |
| API Protection | 42Crunch API Protection | 2022-09-21 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/42crunchapiprotection.html) |
| Armis Activities | Armis | 2024-08-23 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/armisactivities.html) |
| Armis Alerts | Armis | 2024-08-23 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/armisalerts.html) |
| Armorblox | Armorblox | 2021-10-18 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/armorblox.html) |
| Atlassian Confluence | AtlassianConfluenceAudit | 2025-12-13 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/atlassianconfluence.html) |
| Azure Data Lake Storage Gen1 | Azure Data Lake Storage Gen1 | 2025-12-13 | Azure Diagnostics | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/azuredatalakestoragegen1_ccp.html) |
| Bitsight data connector | BitSight | 2024-02-20 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/bitsight.html) |
| blacklens.io | Blacklens | 2026-04-13 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/blacklens_io.html) |
| BloodHound Enterprise Data Connector (using Azure Functions) | BloodHound Enterprise | 2021-05-04 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/bloodhoundenterprise.html) |
| Cisco ASA via Legacy Agent | CiscoASA | 2025-12-12 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/ciscoasa.html) |
| CITRIX SECURITY ANALYTICS | Citrix Analytics for Security | 2022-05-06 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/citrix.html) |
| Common Event Format (CEF) | Common Event Format | 2025-12-13 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cef.html) |
| Common Event Format (CEF) via AMA | Common Event Format | 2025-12-13 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cefama.html) |
| Contrast ADR Push Connector | ContrastADR | 2025-01-18 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/contrastadrccf.html) |
| Cyber Blind Spot Integration | CTM360 | 2026-03-09 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cbspollingidazurefunctions.html) |
| CyberArkEPM | CyberArkEPM | 2022-04-10 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cyberarkepm.html) |
| Egress Iris Connector | Egress Iris | 2024-03-11 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/egresssiempolling.html) |
| ESET Inspect | ESET Inspect | 2022-06-01 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/esetinspect.html) |
| Fortinet FortiWeb Web Application Firewall via AMA | Fortinet FortiWeb Cloud WAF-as-a-Service connector for Microsoft Sentinel | 2025-12-13 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/fortinetfortiwebama.html) |
| GCP Pub/Sub Firewall Logs | Google Cloud Platform Firewall Logs | 2025-12-12 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/gcpfirewalllogsccpdefinition.html) |
| HackerView Intergration | CTM360 | 2026-03-09 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/hvpollingidazurefunctions.html) |
| HYAS Protect | HYAS Protect | 2023-09-26 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/hyasprotect.html) |
| iboss via AMA | iboss | 2026-02-09 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/ibossama.html) |
| Illumio Insights Graph | Illumio Insight | 2025-12-14 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/sentinelillumioinsightsgraphccp.html) |
| Island Enterprise Browser V2 | Island | 2026-04-05 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/islandv2.html) |
| Lookout Cloud Security for Microsoft Sentinel | Lookout Cloud Security Platform for Microsoft Sentinel | 2023-02-17 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/lookoutcloudsecuritydataconnector.html) |
| Lumen Defender Threat Feed Data Connector V2 | Lumen Defender Threat Feed | 2026-02-04 | Azure Function (TI Upload API) | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/lumenthreatfeedconnectorv2.html) |
| Lumen Defender Threat Feed Data Connector V2 (using Azure Functions Flex Consumption Plan with Private Networking) | Lumen Defender Threat Feed | 2026-02-04 | Azure Function (TI Upload API) | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/lumenthreatfeedconnectorv2privatenetworking.html) |
| meshStack Event Logs | meshStack | 2026-04-16 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/meshstackeventlogsdefinition.html) |
| Microsoft 365 Assets (formerly, Office 365) | Microsoft 365 Assets | 2025-06-20 | Native | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/m365assets.html) |
| Miro Audit Logs (Enterprise Plan) | Miro | 2026-01-08 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/miroauditlogsdataconnector.html) |
| Miro Content Logs (Enterprise Plan + Enterprise Guard) | Miro | 2026-01-08 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/mirocontentlogsdataconnector.html) |
| Morphisec API Data Connector (via Codeless Connector Framework) | Morphisec | 2025-12-13 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/morphisecccf.html) |
| Netclean ProActive Incidents | NetClean ProActive | 2022-06-30 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/netclean_proactive_incidents.html) |
| Netskope | Netskope | 2025-12-13 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/netskope.html) |
| Noname Security for Microsoft Sentinel | Noname API Security Solution for Microsoft Sentinel | 2022-12-01 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/nonamesecuritymicrosoftsentinel.html) |
| One Identity Safeguard | OneIdentity | 2022-05-02 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/oneidentity.html) |
| Oracle Cloud Infrastructure (via CCP) – Preview | Oracle Cloud Infrastructure | 2026-02-11 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/oci-connector-ccp-definition.html) |
| Red Canary Threat Detection | Red Canary | 2022-03-04 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/redcanarydataconnector.html) |
| Rubrik Security Cloud Protection Status (using Codeless Connector Framework) | RubrikSecurityCloud | 2026-02-19 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/rubrikprotectionstatus.html) |
| Salesforce Audit Logs (via Codeless Connector Framework) | Salesforce Service Cloud | 2026-01-27 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/salesforceauditlogsconnector.html) |
| SecurityBridge Threat Detection for SAP | SecurityBridge App | 2025-12-13 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/securitybridgesap.html) |
| SecurityScorecard Cybersecurity Ratings | SecurityScorecard Cybersecurity Ratings | 2022-10-01 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/securityscorecardratingsazurefunctions.html) |
| SecurityScorecard Factor | SecurityScorecard Cybersecurity Ratings | 2022-10-01 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/securityscorecardfactorazurefunctions.html) |
| SecurityScorecard Issue | SecurityScorecard Cybersecurity Ratings | 2022-10-01 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/securityscorecardissueazurefunctions.html) |
| Semperis Directory Services Protector | Semperis Directory Services Protector | 2021-10-18 | AMA | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/semperisdsp.html) |
| SenservaPro (Preview) | SenservaPro | 2022-06-01 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/senservapro.html) |
| SINEC Security Guard | SINEC Security Guard | 2024-07-15 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/ssg.html) |
| Slack | SlackAudit | 2025-12-17 | CCF | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/slackaudit.html) |
| Sophos Cloud Optix | Sophos Cloud Optix | 2022-05-02 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/sophoscloudoptix.html) |
| Squadra Technologies secRMM | Squadra Technologies SecRmm | 2022-05-09 | REST Pull API | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/squadratechnologiessecrmm.html) |
| Tanium's CCF Push Connector | Tanium | 2026-03-27 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/taniumconnector.html) |
| Tenable.io Vulnerability Management | TenableIO | 2026-04-16 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/tenableioapi.html) |
| TheHive Project - TheHive | TheHive | 2026-03-13 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/thehiveprojectthehive.html) |
| Threat intelligence - TAXII Export | Threat Intelligence (NEW) | 2026-04-15 | Native | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/threatintelligencetaxiiexport.html) |
| Trend Micro Cloud App Security | Trend Micro Cloud App Security | 2021-09-28 | Azure Function | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/trendmicrocas.html) |
| Zscaler Internet Access Cloud NSS Audit Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnssauditlogs_ccp.html) |
| Zscaler Internet Access Cloud NSS CASB Activity Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnsscasbactivitylogs_ccp.html) |
| Zscaler Internet Access Cloud NSS CASB Cloud Storage Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnsscasbcloudstoragelogs_ccp.html) |
| Zscaler Internet Access Cloud NSS CASB Collaboration Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnsscasbcollablogs_ccp.html) |
| Zscaler Internet Access Cloud NSS CASB CRM Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnsscasbcrmlogs_ccp.html) |
| Zscaler Internet Access Cloud NSS CASB Email Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnsscasbemaillogs_ccp.html) |
| Zscaler Internet Access Cloud NSS CASB File Sharing Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnsscasbfilesharinglogs_ccp.html) |
| Zscaler Internet Access Cloud NSS CASB ITSM Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnsscasbitsmlogs_ccp.html) |
| Zscaler Internet Access Cloud NSS CASB Repo Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnsscasbrepologs_ccp.html) |
| Zscaler Internet Access Cloud NSS DNS Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnssdnslogs_ccp.html) |
| Zscaler Internet Access Cloud NSS Email DLP Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnssemaildlplogs_ccp.html) |
| Zscaler Internet Access Cloud NSS Endpoint DLP Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnssendpointdlplogs_ccp.html) |
| Zscaler Internet Access Cloud NSS Firewall Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnssfwlogs_ccp.html) |
| Zscaler Internet Access Cloud NSS Tunnel Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnsstunnellogs_ccp.html) |
| Zscaler Internet Access Cloud NSS Web Log Push Connector | Zscaler Internet Access | 2025-09-02 | CCF Push | [link](https://oshezaf.github.io/sentinelninja/Solutions%20Docs/connectors/cloudnssweblogs_ccp.html) |

### 1b. Learn entries with no active analyzer connector

| Learn title | Tables | URL |
|---|---|---|
| ESET Protect Platform (using Azure Functions) | 2 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#eset-protect-platform-using-azure-functions) |
| Mimecast Audit & Authentication (using Azure Functions) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#mimecast-audit--authentication-using-azure-functions) |

## 2. Table-list mismatches

**83** connectors match by title but have a different set of Log Analytics tables. See [`connector_table_mismatches.csv`](connector_table_mismatches.csv).

| Title | Solution | Only in analyzer | Only on Learn |
|---|---|---|---|
| Alibaba Cloud Networking Data Connector (via Codeless Connector Framework) | Alibaba Cloud Networking | — | AlibabaCloudVPCFlowLogs |
| Amazon Web Services Elastic Load Balancing (via Codeless Connector Framework) | AWS ELB | AWSALBAccessLogs, AWSALBAccessLogs_CL, AWSELBFlowLogs, AWSELBFlowLogs_CL, AWSNLBAccessLogs, AWSNLBAccessLogs_CL | AWSALBAccessLogsData |
| Amazon Web Services NetworkFirewall (via Codeless Connector Framework) | Amazon Web Services NetworkFirewall | AWSNetworkFirewallAlert, AWSNetworkFirewallTls | — |
| Azure Kubernetes Service (AKS) | Azure kubernetes Service | ContainerInventory, KubeEvents | — |
| BigID DSPM connector | BigID | BigIDDSPMAssetStore_CL | — |
| Bitwarden Event Logs | Bitwarden | BitwardenEventLogs_CL, BitwardenGroups_CL, BitwardenMembers_CL | BitwardenEventLogs |
| Box Events (via Codeless Connector Framework) | Box | BoxEvents_CL | — |
| Cisco ASA/FTD via AMA | CiscoASA | Heartbeat | — |
| Cisco Meraki (using REST API) | CiscoMeraki | CiscoMerakiNativePoller_CL, Syslog, meraki_CL | ASimNetworkSessionLogs |
| Cisco Meraki (using REST API) | Cisco Meraki Events via REST API | ASimAuditEventLogs, ASimWebSessionLogs | — |
| Cisco Meraki (using REST API) | CiscoMeraki | CiscoMerakiNativePoller_CL, Syslog, meraki_CL | ASimNetworkSessionLogs |
| Corelight Connector Exporter | Corelight | Corelight_CL, Corelight_v2_bacnet_CL, Corelight_v2_capture_loss_CL, Corelight_v2_cip_CL, Corelight_v2_conn_CL, Corelight_v2_conn_long_CL, Corelight_v2_conn_red_CL, Corelight_v2_corelight_burst_CL, Corelight_v2_corelight_overall_capture_loss_CL, Corelight_v2_corelight_profiling_CL, Corelight_v2_datared_CL, Corelight_v2_dce_rpc_CL, Corelight_v2_dga_CL, Corelight_v2_dhcp_CL, Corelight_v2_dnp3_CL, Corelight_v2_dns_CL, Corelight_v2_dns_red_CL, Corelight_v2_dpd_CL, Corelight_v2_encrypted_dns_CL, Corelight_v2_enip_CL, Corelight_v2_enip_debug_CL, Corelight_v2_enip_list_identity_CL, Corelight_v2_etc_viz_CL, Corelight_v2_files_CL, Corelight_v2_files_red_CL, Corelight_v2_ftp_CL, Corelight_v2_generic_dns_tunnels_CL, Corelight_v2_generic_icmp_tunnels_CL, Corelight_v2_http2_CL, Corelight_v2_http_CL, Corelight_v2_http_red_CL, Corelight_v2_icmp_specific_tunnels_CL, Corelight_v2_intel_CL, Corelight_v2_ipsec_CL, Corelight_v2_irc_CL, Corelight_v2_iso_cotp_CL, Corelight_v2_kerberos_CL, Corelight_v2_known_certs_CL, Corelight_v2_known_devices_CL, Corelight_v2_known_domains_CL, Corelight_v2_known_hosts_CL, Corelight_v2_known_names_CL, Corelight_v2_known_remotes_CL, Corelight_v2_known_services_CL, Corelight_v2_known_users_CL, Corelight_v2_local_subnets_CL, Corelight_v2_local_subnets_dj_CL, Corelight_v2_local_subnets_graphs_CL, Corelight_v2_log4shell_CL, Corelight_v2_modbus_CL, Corelight_v2_mqtt_connect_CL, Corelight_v2_mqtt_publish_CL, Corelight_v2_mqtt_subscribe_CL, Corelight_v2_mysql_CL, Corelight_v2_notice_CL, Corelight_v2_ntlm_CL, Corelight_v2_ntp_CL, Corelight_v2_ocsp_CL, Corelight_v2_openflow_CL, Corelight_v2_packet_filter_CL, Corelight_v2_pe_CL, Corelight_v2_profinet_CL, Corelight_v2_profinet_dce_rpc_CL, Corelight_v2_profinet_debug_CL, Corelight_v2_radius_CL, Corelight_v2_rdp_CL, Corelight_v2_reporter_CL, Corelight_v2_rfb_CL, Corelight_v2_s7comm_CL, Corelight_v2_signatures_CL, Corelight_v2_sip_CL, Corelight_v2_smartpcap_CL, Corelight_v2_smartpcap_stats_CL, Corelight_v2_smb_files_CL, Corelight_v2_smb_mapping_CL, Corelight_v2_smtp_CL, Corelight_v2_smtp_links_CL, Corelight_v2_snmp_CL, Corelight_v2_socks_CL, Corelight_v2_software_CL, Corelight_v2_specific_dns_tunnels_CL, Corelight_v2_ssh_CL, Corelight_v2_ssl_CL, Corelight_v2_ssl_red_CL, Corelight_v2_stats_CL, Corelight_v2_stepping_CL, Corelight_v2_stun_CL, Corelight_v2_stun_nat_CL, Corelight_v2_suricata_corelight_CL, Corelight_v2_suricata_eve_CL, Corelight_v2_suricata_stats_CL, Corelight_v2_suricata_zeek_stats_CL, Corelight_v2_syslog_CL, Corelight_v2_tds_CL, Corelight_v2_tds_rpc_CL, Corelight_v2_tds_sql_batch_CL, Corelight_v2_traceroute_CL, Corelight_v2_tunnel_CL, Corelight_v2_unknown_smartpcap_CL, Corelight_v2_util_stats_CL, Corelight_v2_vpn_CL, Corelight_v2_weird_CL, Corelight_v2_weird_red_CL, Corelight_v2_weird_stats_CL, Corelight_v2_wireguard_CL, Corelight_v2_x509_CL, Corelight_v2_x509_red_CL, Corelight_v2_zeek_doctor_CL | Corelight |
| Cortex XDR - Incidents | Cortex XDR | PaloAltoCortexXDR_Incidents_CL | CortexXDR_Incidents_CL |
| Cribl | Cribl | CriblAccess_CL, CriblAudit_CL, CriblUIAccess_CL | — |
| CrowdStrike API Data Connector (via Codeless Connector Framework) | CrowdStrike Falcon Endpoint Protection | CrowdStrikeCases, CrowdStrikeDetections, CrowdStrikeHosts, CrowdStrikeVulnerabilities | — |
| CrowdStrike Falcon Adversary Intelligence  | CrowdStrike Falcon Endpoint Protection | ThreatIntelObjects | — |
| CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework) | CrowdStrike Falcon Endpoint Protection | CrowdStrike_Audit_Events_CL, CrowdStrike_Auth_Events_CL, CrowdStrike_DNS_Events_CL, CrowdStrike_File_Events_CL, CrowdStrike_Network_Events_CL, CrowdStrike_Process_Events_CL, CrowdStrike_Registry_Events_CL, CrowdStrike_Secondary_Data_CL, CrowdStrike_User_Events_CL | — |
| CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3) (using Azure Function) | CrowdStrike Falcon Endpoint Protection | ASimAuditEventLogs, ASimAuthenticationEventLogs, ASimAuthenticationEventLogs_CL, ASimDnsActivityLogs, ASimFileEventLogs, ASimFileEventLogs_CL, ASimNetworkSessionLogs, ASimProcessEventLogs, ASimProcessEventLogs_CL, ASimRegistryEventLogs, ASimRegistryEventLogs_CL, ASimUserManagementActivityLogs, ASimUserManagementLogs_CL, CrowdStrike_Additional_Events_CL, CrowdStrike_Secondary_Data_CL | CrowdStrikeReplicatorV2 |
| CTM360 CyberBlindSpot (Serverless) | CTM360 | CBS_BreachedCredentials_AzureV2_CL, CBS_CompromisedCards_AzureV2_CL, CBS_DomainInfringement_AzureV2_CL, CBS_MalwareLogs_AzureV2_CL, CBS_SubdomainInfringement_AzureV2_CL | — |
| Datalake2Sentinel | Datalake2Sentinel | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| Derdack SIGNL4 | SIGNL4 | SIGNL4_CL | — |
| Druva Events Connector | DruvaDataSecurityCloud | DruvaInsyncEvents_CL, DruvaPlatformEvents_CL | — |
| Dynatrace Attacks V1 | Dynatrace | DynatraceAttacksV2_CL | — |
| Dynatrace Attacks V2 | Dynatrace | DynatraceAttacksV2_CL | — |
| Dynatrace Audit Logs V1 | Dynatrace | DynatraceAuditLogsV2_CL | — |
| Dynatrace Audit Logs V2 | Dynatrace | DynatraceAuditLogsV2_CL | — |
| Dynatrace Problems V1 | Dynatrace | DynatraceProblemsV2_CL | — |
| Dynatrace Problems V2 | Dynatrace | DynatraceProblemsV2_CL | — |
| Dynatrace Runtime Vulnerabilities V1 | Dynatrace | DynatraceSecurityProblemsV2_CL | — |
| Dynatrace Runtime Vulnerabilities V2 | Dynatrace | DynatraceSecurityProblemsV2_CL | — |
| Elastic Agent | ElasticAgent | ElasticAgentLogs_CL | ElasticAgentEvent |
| Elastic Agent (via Codeless Connector Framework) | ElasticAgent | ElasticAgentLogsV2_CL | ElasticAgentEvent |
| Forescout | Forescout (Legacy) | Syslog | ForescoutEvent |
| Forescout Host Property Monitor | ForescoutHostPropertyMonitor | ForescoutComplianceStatus_CL, ForescoutPolicyStatus_CL | — |
| GitHub (using Webhooks) V2 | GitHub | GitHubAdvancedSecurityAlerts_CL | — |
| Google Kubernetes Engine (via Codeless Connector Framework) | Google Kubernetes Engine | GKEAPIServer, GKEApplication, GKEControllerManager, GKEHPADecision, GKEScheduler | — |
| GreyNoise Threat Intelligence | GreyNoiseThreatIntelligence | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| Halcyon Connector | Halcyon | HalcyonEvents_CL | HalcyonAuthenticationEvents_CL, HalcyonDnsActivity_CL, HalcyonFileActivity_CL, HalcyonNetworkSession_CL, HalcyonProcessEvent_CL |
| Illumio Insights | Illumio Insight | IllumioInsights_CL | IlumioInsights |
| Illumio Saas | IllumioSaaS | IllumioFlowEventsV2_CL | Illumio_Auditable_Events_CL, Illumio_Flow_Events_CL |
| Imperva Cloud WAF | ImpervaCloudWAF | ImpervaWAFCloudV2_CL, SentinelImpervaWAFCloudV2Logs | — |
| Imperva Cloud WAF (via Codeless Connector Framework) | ImpervaCloudWAF | ImpervaWAFCloudV2_CL, ImpervaWAFCloud_CL, SentinelImpervaWAFCloudV2Logs | ImpervaWAFCloud |
| Infoblox Data Connector via REST API | Infoblox | ThreatIntelIndicators, ThreatIntelObjects | Failed_Range_To_Ingest_CL, Infoblox_Failed_Indicators_CL, dossier_atp_CL, dossier_atp_threat_CL, dossier_dns_CL, dossier_geo_CL, dossier_infoblox_web_cat_CL, dossier_inforank_CL, dossier_malware_analysis_v3_CL, dossier_nameserver_CL, dossier_nameserver_matches_CL, dossier_ptr_CL, dossier_rpz_feeds_CL, dossier_rpz_feeds_records_CL, dossier_threat_actor_CL, dossier_tld_risk_CL, dossier_whitelist_CL, dossier_whois_CL |
| JoeSandboxThreatIntelligence | JoeSandbox | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| MailRisk by Secure Practice | MailRisk | MailRiskEventEmails_CL | MailRiskEmails_CL |
| Microsoft Defender for Cloud Apps | Microsoft Defender for Cloud Apps | McasShadowItReporting, SecurityAlert | McasShadowItReporting​, SecurityAlert​ |
| Microsoft Defender Threat Intelligence | Threat Intelligence (NEW) | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| Microsoft Defender XDR | Microsoft Defender XDR | DeviceFileCertificateInfo, DeviceFileEvents, DeviceImageLoadEvents, DeviceInfo, DeviceLogonEvents, DeviceNetworkEvents, DeviceNetworkInfo, DeviceProcessEvents, DeviceRegistryEvents, EmailAttachmentInfo, EmailPostDeliveryEvents, EmailUrlInfo, IdentityDirectoryEvents, IdentityQueryEvents, UrlClickEvents | — |
| MISP2Sentinel | MISP2Sentinel | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| Netskope Alerts and Events (via Codeless Connector Framework) | Netskopev2 | NetskopeEventsApplication_CL, NetskopeEventsAudit_CL, NetskopeEventsConnection_CL, NetskopeEventsDLP_CL, NetskopeEventsEndpoint_CL, NetskopeEventsInfrastructure_CL, NetskopeEventsNetwork_CL, NetskopeEventsPage_CL | — |
| Okta Single Sign-On (Polling CCP) | Okta Single Sign-On | OktaNativePoller_CL | OktaV2_CL, Okta_CL |
| Onapsis Defend Integration | Onapsis Defend | ABAPAuditLog | — |
| Palo Alto Prisma Cloud CSPM (via Codeless Connector Framework) | PaloAltoPrismaCloud | PaloAltoPrismaCloudAuditV2_CL | — |
| Pathlock Inc.: Threat Detection and Response for SAP | Pathlock_TDnR | Pathlock_TDnR_CL | — |
| Premium Microsoft Defender Threat Intelligence | Threat Intelligence (NEW) | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| Qualys Knowledge Base (via Codeless Connector Framework) | Qualys VM Knowledgebase | QualysKB_CL | — |
| Qualys VM KnowledgeBase | Qualys VM Knowledgebase | QualysKnowledgeBase | — |
| Radiflow iSID via AMA | Radiflow | CommonSecurityLog | RadiflowEvent |
| Rapid7 Insight Platform Vulnerability Management Reports (via Codeless Connector Framework) | Rapid7InsightVM | Rapid7InsightVMCloudAssets, Rapid7InsightVMCloudVulnerabilities | NexposeInsightVMCloud_assets_CL, NexposeInsightVMCloud_vulnerabilities_CL |
| SailPoint IdentityNow (via Codeless Connector Framework) | SailPointIdentityNow | SailPointIDN_EventsV2_CL | SailPointIDN_Events_CL, SailPointIDN_Triggers_CL |
| Salesforce Service Cloud (via Codeless Connector Framework) | Salesforce Service Cloud | SalesforceServiceCloudV3_CL | — |
| Samsung Knox Asset Intelligence | Samsung Knox Asset Intelligence | Samsung_Knox_Application_CL, Samsung_Knox_Network_CL, Samsung_Knox_Process_CL, Samsung_Knox_System_CL, Samsung_Knox_User_CL | — |
| SecurityBridge Solution for SAP | SecurityBridge App | SecurityBridge_CL | — |
| Semperis Lightning Logs | SemperisLightning | LightningAttackPathLinks_CL, LightningIOEsMetadata_CL, LightningIndicatorExecutions_CL, LightningTier0Attackers_CL | — |
| SentinelOne (via Codeless Connector Framework) | SentinelOne | SentinelOneActivities_CL, SentinelOneAgents_CL, SentinelOneAlerts_CL, SentinelOneGroups_CL, SentinelOneThreats_CL | SentinelOne_CL |
| Sophos Endpoint Protection (via Codeless Connector Platform) | Sophos Endpoint Protection | SophosEPAlerts_CL | — |
| Synqly Integration Connector | SynqlyIntegrationConnector | ASimAuditEventLogs, ASimAuthenticationEventLogs, ASimDhcpEventLogs, ASimDnsActivityLogs, ASimFileEventLogs, ASimNetworkSessionLogs, ASimProcessEventLogs, ASimRegistryEventLogs, ASimUserManagementActivityLogs, ASimWebSessionLogs | union ASimAuditEventLogs, ASimAuthenticationEventLogs, ASimDhcpEventLogs, ASimDnsActivityLogs, ASimFileEventLogs, ASimNetworkSessionLogs, ASimProcessEventLogs, ASimRegistryEventLogs, ASimUserManagementActivityLogs, ASimWebSessionLogs |
| Tenable Identity Exposure | Tenable App | AlsidForADLog_CL, Tenable_IE_CL | — |
| TheHive (via Codeless Connector Framework) | TheHive | — | TheHiveData |
| Threat intelligence - TAXII | Threat Intelligence (NEW) | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| Threat Intelligence Platforms | Threat Intelligence (NEW) | CommonSecurityLog, ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| Threat Intelligence Upload API (Preview) | Threat Intelligence (NEW) | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| Trellix Endpoint Security (via Codeless Connector Framework) | Trellix | TrellixEvents_CL | TrellixEvents |
| Tropico Security - Alerts | Tropico | Tropico_Alerts_CL | {{graphQueriesTableName}} |
| Tropico Security - Events | Tropico | Tropico_Events_CL | {{graphQueriesTableName}} |
| Tropico Security - Incidents | Tropico | Tropico_Incidents_CL | {{graphQueriesTableName}} |
| VMRayThreatIntelligence | VMRay | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| VMware Carbon Black Cloud via AWS S3 | VMware Carbon Black Cloud | ASimAuthenticationEventLogs, ASimFileEventLogs, ASimNetworkSessionLogs, ASimProcessEventLogs, ASimRegistryEventLogs, CarbonBlack_Watchlist_CL | — |
| Windows Firewall | Windows Firewall | WindowsFirewall | — |
| Windows Firewall Events via AMA | Windows Firewall | ASimNetworkSessionLogs | — |
| Wiz | Wiz | WizAuditLogsV2_CL, WizAuditLogs_CL, WizIssuesV2_CL, WizIssues_CL, WizVulnerabilitiesV2_CL, WizVulnerabilities_CL | union isfuzzy=true (WizAuditLogs_CL),(WizAuditLogsV2_CL), union isfuzzy=true (WizIssues_CL),(WizIssuesV2_CL), union isfuzzy=true (WizVulnerabilities_CL),(WizVulnerabilitiesV2_CL) |
| Zimperium Mobile Threat Defense | Zimperium Mobile Threat Defense | ZimperiumMitigationLog_CL | — |
| Zimperium Mobile Threat Defense CCF | Zimperium Mobile Threat Defense | ZimperiumMitigationLogV2_CL, ZimperiumThreatLogV2_CL | ZimperiumThreatLog_CL |

## 3. Potential matches (for manual review)

**0** pair(s) of gap rows share ≥ 50% of their content tokens after stripping stopwords. These are likely V1/V2 splits, minor word differences (`Audit` vs `Events`), or renames — surfaced here so they can be confirmed or dismissed without auto-matching. See [`connector_potential_matches.csv`](connector_potential_matches.csv).

