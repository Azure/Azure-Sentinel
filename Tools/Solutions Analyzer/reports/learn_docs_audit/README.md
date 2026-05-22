# Microsoft Learn data-connectors-reference audit

Generated against `https://learn.microsoft.com/azure/sentinel/data-connectors-reference`

- Learn sections parsed: **342**
- Published, non-deprecated solutions: **469**
- Active connectors in those solutions: **415**

## 1. Active connectors missing from Learn

**92** active connectors in published solutions are not on Learn. See [`connectors_missing_from_learn.csv`](connectors_missing_from_learn.csv).

| Title | Solution | Collection method |
|---|---|---|
| Abnormal Security (Push) | AbnormalSecurity | CCF Push |
| Agent 365 | Agent 365 | Unknown |
| AI Vectra Stream via Legacy Agent | Vectra AI Stream | AMA |
| API Protection | 42Crunch API Protection | REST Pull API |
| Armis Activities | Armis | Azure Function |
| Armis Alerts | Armis | Azure Function |
| Armorblox | Armorblox | Azure Function |
| Atlassian Confluence | AtlassianConfluenceAudit | CCF |
| Auth0 Logs (via Codeless Connector Framework) | Auth0 | CCF |
| Azure Data Lake Storage Gen1 | Azure Data Lake Storage Gen1 | Azure Diagnostics |
| Bitsight data connector | BitSight | Azure Function |
| BloodHound Enterprise Data Connector (using Azure Functions) | BloodHound Enterprise | Azure Function |
| Cisco ASA via Legacy Agent | CiscoASA | AMA |
| CITRIX SECURITY ANALYTICS | Citrix Analytics for Security | REST Pull API |
| Common Event Format (CEF) | Common Event Format | AMA |
| Common Event Format (CEF) via AMA | Common Event Format | AMA |
| Cyber Blind Spot Integration | CTM360 | Azure Function |
| Zscaler Internet Access Cloud NSS Audit Log Push Connector | Zscaler Internet Access | CCF Push |
| Zscaler Internet Access Cloud NSS CASB Activity Log Push Connector | Zscaler Internet Access | CCF Push |
| Zscaler Internet Access Cloud NSS CASB CRM Log Push Connector | Zscaler Internet Access | CCF Push |

_…and 72 more. Full list in the CSV._

## 2. Learn entries with no analyzer match

**19** Learn sections have no matching connector in the analyzer. See [`connectors_missing_from_analyzer.csv`](connectors_missing_from_analyzer.csv).

| Learn title | Tables | URL |
|---|---|---|
| A365 Observability | 0 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#a365-observability) |
| Auth0 Access Management (using Azure Functions) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#auth0-access-management-using-azure-functions) |
| Auth0 Logs(via Codeless Connector Framework) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#auth0-logsvia-codeless-connector-framework) |
| Box (using Azure Functions) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#box-using-azure-functions) |
| Cloudflare (Preview) (using Azure Functions) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#cloudflare-preview-using-azure-functions) |
| CrowdStrike Falcon Adversary Intelligence  (using Azure Functions) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#crowdstrike-falcon-adversary-intelligence--using-azure-functions) |
| Dynamics365 | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#dynamics365) |
| Dynatrace Attacks | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#dynatrace-attacks) |
| Dynatrace Audit Logs | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#dynatrace-audit-logs) |
| Dynatrace Problems | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#dynatrace-problems) |
| Dynatrace Runtime Vulnerabilities | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#dynatrace-runtime-vulnerabilities) |
| Elastic Agent (Standalone) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#elastic-agent-standalone) |
| Island Enterprise Browser Admin Audit (Polling CCF) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#island-enterprise-browser-admin-audit-polling-ccp) |
| Island Enterprise Browser User Activity (Polling CCF) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#island-enterprise-browser-user-activity-polling-ccp) |
| Mimecast Audit & Authentication (using Azure Functions) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#mimecast-audit--authentication-using-azure-functions) |
| Mimecast Intelligence for Microsoft - Microsoft Sentinel (using Azure Functions) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#mimecast-intelligence-for-microsoft---microsoft-sentinel-using-azure-functions) |
| Onapsis Defend: Integrate Unmatched SAP Threat Detection & Intel with Microsoft Sentinel | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#onapsis-defend-integrate-unmatched-sap-threat-detection--intel-with-microsoft-sentinel) |
| Sophos Endpoint Protection (using Azure Functions) | 1 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#sophos-endpoint-protection-using-azure-functions) |
| VMware Carbon Black Cloud (using Azure Functions) | 3 | [link](https://learn.microsoft.com/azure/sentinel/data-connectors-reference#vmware-carbon-black-cloud-using-azure-functions) |

## 3. Table-list mismatches

**70** connectors match by title but have a different set of Log Analytics tables. See [`connector_table_mismatches.csv`](connector_table_mismatches.csv).

| Title | Only in analyzer | Only on Learn |
|---|---|---|
| Alibaba Cloud Networking Data Connector (via Codeless Connector Framework) | — | AlibabaCloudVPCFlowLogs |
| Amazon Web Services Elastic Load Balancing (via Codeless Connector Framework) | AWSALBAccessLogs, AWSALBAccessLogs_CL, AWSELBFlowLogs, AWSELBFlowLogs_CL, AWSNLBAccessLogs, AWSNLBAccessLogs_CL | AWSALBAccessLogsData |
| Amazon Web Services NetworkFirewall (via Codeless Connector Framework) | AWSNetworkFirewallAlert, AWSNetworkFirewallTls | — |
| Azure Kubernetes Service (AKS) | ContainerInventory, KubeEvents | — |
| BigID DSPM connector | BigIDDSPMAssetStore_CL | — |
| Bitwarden Event Logs | BitwardenEventLogs_CL, BitwardenGroups_CL, BitwardenMembers_CL | BitwardenEventLogs |
| Box Events (via Codeless Connector Framework) | BoxEvents_CL | — |
| Cisco ASA/FTD via AMA | Heartbeat | — |
| Cisco Meraki (using REST API) | CiscoMerakiNativePoller_CL, Syslog, meraki_CL | ASimNetworkSessionLogs |
| Cisco Meraki (using REST API) | ASimAuditEventLogs, ASimWebSessionLogs | — |
| Cisco Meraki (using REST API) | CiscoMerakiNativePoller_CL, Syslog, meraki_CL | ASimNetworkSessionLogs |
| Corelight Connector Exporter | Corelight_CL, Corelight_v2_bacnet_CL, Corelight_v2_capture_loss_CL, Corelight_v2_cip_CL, Corelight_v2_conn_CL, Corelight_v2_conn_long_CL, Corelight_v2_conn_red_CL, Corelight_v2_corelight_burst_CL, Corelight_v2_corelight_overall_capture_loss_CL, Corelight_v2_corelight_profiling_CL, Corelight_v2_datared_CL, Corelight_v2_dce_rpc_CL, Corelight_v2_dga_CL, Corelight_v2_dhcp_CL, Corelight_v2_dnp3_CL, Corelight_v2_dns_CL, Corelight_v2_dns_red_CL, Corelight_v2_dpd_CL, Corelight_v2_encrypted_dns_CL, Corelight_v2_enip_CL, Corelight_v2_enip_debug_CL, Corelight_v2_enip_list_identity_CL, Corelight_v2_etc_viz_CL, Corelight_v2_files_CL, Corelight_v2_files_red_CL, Corelight_v2_ftp_CL, Corelight_v2_generic_dns_tunnels_CL, Corelight_v2_generic_icmp_tunnels_CL, Corelight_v2_http2_CL, Corelight_v2_http_CL, Corelight_v2_http_red_CL, Corelight_v2_icmp_specific_tunnels_CL, Corelight_v2_intel_CL, Corelight_v2_ipsec_CL, Corelight_v2_irc_CL, Corelight_v2_iso_cotp_CL, Corelight_v2_kerberos_CL, Corelight_v2_known_certs_CL, Corelight_v2_known_devices_CL, Corelight_v2_known_domains_CL, Corelight_v2_known_hosts_CL, Corelight_v2_known_names_CL, Corelight_v2_known_remotes_CL, Corelight_v2_known_services_CL, Corelight_v2_known_users_CL, Corelight_v2_local_subnets_CL, Corelight_v2_local_subnets_dj_CL, Corelight_v2_local_subnets_graphs_CL, Corelight_v2_log4shell_CL, Corelight_v2_modbus_CL, Corelight_v2_mqtt_connect_CL, Corelight_v2_mqtt_publish_CL, Corelight_v2_mqtt_subscribe_CL, Corelight_v2_mysql_CL, Corelight_v2_notice_CL, Corelight_v2_ntlm_CL, Corelight_v2_ntp_CL, Corelight_v2_ocsp_CL, Corelight_v2_openflow_CL, Corelight_v2_packet_filter_CL, Corelight_v2_pe_CL, Corelight_v2_profinet_CL, Corelight_v2_profinet_dce_rpc_CL, Corelight_v2_profinet_debug_CL, Corelight_v2_radius_CL, Corelight_v2_rdp_CL, Corelight_v2_reporter_CL, Corelight_v2_rfb_CL, Corelight_v2_s7comm_CL, Corelight_v2_signatures_CL, Corelight_v2_sip_CL, Corelight_v2_smartpcap_CL, Corelight_v2_smartpcap_stats_CL, Corelight_v2_smb_files_CL, Corelight_v2_smb_mapping_CL, Corelight_v2_smtp_CL, Corelight_v2_smtp_links_CL, Corelight_v2_snmp_CL, Corelight_v2_socks_CL, Corelight_v2_software_CL, Corelight_v2_specific_dns_tunnels_CL, Corelight_v2_ssh_CL, Corelight_v2_ssl_CL, Corelight_v2_ssl_red_CL, Corelight_v2_stats_CL, Corelight_v2_stepping_CL, Corelight_v2_stun_CL, Corelight_v2_stun_nat_CL, Corelight_v2_suricata_corelight_CL, Corelight_v2_suricata_eve_CL, Corelight_v2_suricata_stats_CL, Corelight_v2_suricata_zeek_stats_CL, Corelight_v2_syslog_CL, Corelight_v2_tds_CL, Corelight_v2_tds_rpc_CL, Corelight_v2_tds_sql_batch_CL, Corelight_v2_traceroute_CL, Corelight_v2_tunnel_CL, Corelight_v2_unknown_smartpcap_CL, Corelight_v2_util_stats_CL, Corelight_v2_vpn_CL, Corelight_v2_weird_CL, Corelight_v2_weird_red_CL, Corelight_v2_weird_stats_CL, Corelight_v2_wireguard_CL, Corelight_v2_x509_CL, Corelight_v2_x509_red_CL, Corelight_v2_zeek_doctor_CL | Corelight |
| Cortex XDR - Incidents | PaloAltoCortexXDR_Incidents_CL | CortexXDR_Incidents_CL |
| Cribl | CriblAccess_CL, CriblAudit_CL, CriblUIAccess_CL | — |
| CrowdStrike API Data Connector (via Codeless Connector Framework) | CrowdStrikeCases, CrowdStrikeDetections, CrowdStrikeHosts, CrowdStrikeVulnerabilities | — |
| CrowdStrike Falcon Data Replicator (AWS S3) (via Codeless Connector Framework) | CrowdStrike_Audit_Events_CL, CrowdStrike_Auth_Events_CL, CrowdStrike_DNS_Events_CL, CrowdStrike_File_Events_CL, CrowdStrike_Network_Events_CL, CrowdStrike_Process_Events_CL, CrowdStrike_Registry_Events_CL, CrowdStrike_Secondary_Data_CL, CrowdStrike_User_Events_CL | — |
| CrowdStrike Falcon Data Replicator (CrowdStrike Managed AWS-S3) (using Azure Function) | ASimAuditEventLogs, ASimAuthenticationEventLogs, ASimAuthenticationEventLogs_CL, ASimDnsActivityLogs, ASimFileEventLogs, ASimFileEventLogs_CL, ASimNetworkSessionLogs, ASimProcessEventLogs, ASimProcessEventLogs_CL, ASimRegistryEventLogs, ASimRegistryEventLogs_CL, ASimUserManagementActivityLogs, ASimUserManagementLogs_CL, CrowdStrike_Additional_Events_CL, CrowdStrike_Secondary_Data_CL | CrowdStrikeReplicatorV2 |
| CTM360 CyberBlindSpot (Serverless) | CBS_BreachedCredentials_AzureV2_CL, CBS_CompromisedCards_AzureV2_CL, CBS_DomainInfringement_AzureV2_CL, CBS_MalwareLogs_AzureV2_CL, CBS_SubdomainInfringement_AzureV2_CL | — |
| Datalake2Sentinel | ThreatIntelIndicators, ThreatIntelObjects | ThreatIntelligenceIndicator |
| Derdack SIGNL4 | SIGNL4_CL | — |

_…and 50 more. Full list in the CSV._
