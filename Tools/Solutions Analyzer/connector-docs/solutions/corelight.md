# Corelight

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Corelight |
| **Support Tier** | Partner |
| **Support Link** | [https://support.corelight.com/](https://support.corelight.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md)

## Tables Reference

This solution uses **129 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`AggregationRecords`](../tables/aggregationrecords.md) | - | Workbooks |
| [`Corelight_CL`](../tables/corelight-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_bacnet_CL`](../tables/corelight-v2-bacnet-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_capture_loss_CL`](../tables/corelight-v2-capture-loss-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_cip_CL`](../tables/corelight-v2-cip-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_conn_CL`](../tables/corelight-v2-conn-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Hunting, Workbooks |
| [`Corelight_v2_conn_long_CL`](../tables/corelight-v2-conn-long-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Hunting, Workbooks |
| [`Corelight_v2_conn_red_CL`](../tables/corelight-v2-conn-red-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Hunting, Workbooks |
| [`Corelight_v2_corelight_burst_CL`](../tables/corelight-v2-corelight-burst-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_corelight_metrics_disk_CL`](../tables/corelight-v2-corelight-metrics-disk-cl.md) | - | Workbooks |
| [`Corelight_v2_corelight_metrics_iface_CL`](../tables/corelight-v2-corelight-metrics-iface-cl.md) | - | Workbooks |
| [`Corelight_v2_corelight_metrics_memory_CL`](../tables/corelight-v2-corelight-metrics-memory-cl.md) | - | Workbooks |
| [`Corelight_v2_corelight_metrics_system_CL`](../tables/corelight-v2-corelight-metrics-system-cl.md) | - | Workbooks |
| [`Corelight_v2_corelight_metrics_zeek_doctor_CL`](../tables/corelight-v2-corelight-metrics-zeek-doctor-cl.md) | - | Workbooks |
| [`Corelight_v2_corelight_overall_capture_loss_CL`](../tables/corelight-v2-corelight-overall-capture-loss-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_corelight_profiling_CL`](../tables/corelight-v2-corelight-profiling-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_datared_CL`](../tables/corelight-v2-datared-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_dce_rpc_CL`](../tables/corelight-v2-dce-rpc-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_dga_CL`](../tables/corelight-v2-dga-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_dhcp_CL`](../tables/corelight-v2-dhcp-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_dnp3_CL`](../tables/corelight-v2-dnp3-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_dns_CL`](../tables/corelight-v2-dns-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Hunting, Workbooks |
| [`Corelight_v2_dns_red_CL`](../tables/corelight-v2-dns-red-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Hunting, Workbooks |
| [`Corelight_v2_dpd_CL`](../tables/corelight-v2-dpd-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_encrypted_dns_CL`](../tables/corelight-v2-encrypted-dns-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_enip_CL`](../tables/corelight-v2-enip-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_enip_debug_CL`](../tables/corelight-v2-enip-debug-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_enip_list_identity_CL`](../tables/corelight-v2-enip-list-identity-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_etc_viz_CL`](../tables/corelight-v2-etc-viz-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_files_CL`](../tables/corelight-v2-files-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Hunting, Workbooks |
| [`Corelight_v2_files_red_CL`](../tables/corelight-v2-files-red-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Hunting, Workbooks |
| [`Corelight_v2_ftp_CL`](../tables/corelight-v2-ftp-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_generic_dns_tunnels_CL`](../tables/corelight-v2-generic-dns-tunnels-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_generic_icmp_tunnels_CL`](../tables/corelight-v2-generic-icmp-tunnels-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Analytics, Hunting, Workbooks |
| [`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Analytics, Hunting, Workbooks |
| [`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Analytics, Hunting, Workbooks |
| [`Corelight_v2_icmp_specific_tunnels_CL`](../tables/corelight-v2-icmp-specific-tunnels-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_intel_CL`](../tables/corelight-v2-intel-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_ipsec_CL`](../tables/corelight-v2-ipsec-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_irc_CL`](../tables/corelight-v2-irc-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_iso_cotp_CL`](../tables/corelight-v2-iso-cotp-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_kerberos_CL`](../tables/corelight-v2-kerberos-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_known_certs_CL`](../tables/corelight-v2-known-certs-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_known_devices_CL`](../tables/corelight-v2-known-devices-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_known_domains_CL`](../tables/corelight-v2-known-domains-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_known_hosts_CL`](../tables/corelight-v2-known-hosts-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_known_names_CL`](../tables/corelight-v2-known-names-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_known_remotes_CL`](../tables/corelight-v2-known-remotes-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_known_services_CL`](../tables/corelight-v2-known-services-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_known_users_CL`](../tables/corelight-v2-known-users-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_local_subnets_CL`](../tables/corelight-v2-local-subnets-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_local_subnets_dj_CL`](../tables/corelight-v2-local-subnets-dj-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_local_subnets_graphs_CL`](../tables/corelight-v2-local-subnets-graphs-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_log4shell_CL`](../tables/corelight-v2-log4shell-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_modbus_CL`](../tables/corelight-v2-modbus-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_mqtt_connect_CL`](../tables/corelight-v2-mqtt-connect-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_mqtt_publish_CL`](../tables/corelight-v2-mqtt-publish-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_mqtt_subscribe_CL`](../tables/corelight-v2-mqtt-subscribe-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_mysql_CL`](../tables/corelight-v2-mysql-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_notice_CL`](../tables/corelight-v2-notice-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_ntlm_CL`](../tables/corelight-v2-ntlm-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_ntp_CL`](../tables/corelight-v2-ntp-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_ocsp_CL`](../tables/corelight-v2-ocsp-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_openflow_CL`](../tables/corelight-v2-openflow-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_packet_filter_CL`](../tables/corelight-v2-packet-filter-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_pe_CL`](../tables/corelight-v2-pe-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_profinet_CL`](../tables/corelight-v2-profinet-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_profinet_dce_rpc_CL`](../tables/corelight-v2-profinet-dce-rpc-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_profinet_debug_CL`](../tables/corelight-v2-profinet-debug-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_radius_CL`](../tables/corelight-v2-radius-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_rdp_CL`](../tables/corelight-v2-rdp-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_reporter_CL`](../tables/corelight-v2-reporter-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_rfb_CL`](../tables/corelight-v2-rfb-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_s7comm_CL`](../tables/corelight-v2-s7comm-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_signatures_CL`](../tables/corelight-v2-signatures-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_sip_CL`](../tables/corelight-v2-sip-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_smartpcap_CL`](../tables/corelight-v2-smartpcap-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_smartpcap_stats_CL`](../tables/corelight-v2-smartpcap-stats-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_smb_files_CL`](../tables/corelight-v2-smb-files-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_smb_mapping_CL`](../tables/corelight-v2-smb-mapping-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Hunting |
| [`Corelight_v2_smtp_CL`](../tables/corelight-v2-smtp-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Analytics, Hunting, Workbooks |
| [`Corelight_v2_smtp_links_CL`](../tables/corelight-v2-smtp-links-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_snmp_CL`](../tables/corelight-v2-snmp-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_socks_CL`](../tables/corelight-v2-socks-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_software_CL`](../tables/corelight-v2-software-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_specific_dns_tunnels_CL`](../tables/corelight-v2-specific-dns-tunnels-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_ssh_CL`](../tables/corelight-v2-ssh-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_ssl_CL`](../tables/corelight-v2-ssl-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_ssl_red_CL`](../tables/corelight-v2-ssl-red-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_stats_CL`](../tables/corelight-v2-stats-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_stepping_CL`](../tables/corelight-v2-stepping-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_stun_CL`](../tables/corelight-v2-stun-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_stun_nat_CL`](../tables/corelight-v2-stun-nat-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_suricata_corelight_CL`](../tables/corelight-v2-suricata-corelight-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_suricata_eve_CL`](../tables/corelight-v2-suricata-eve-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_suricata_stats_CL`](../tables/corelight-v2-suricata-stats-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_suricata_zeek_stats_CL`](../tables/corelight-v2-suricata-zeek-stats-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_syslog_CL`](../tables/corelight-v2-syslog-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_tds_CL`](../tables/corelight-v2-tds-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_tds_rpc_CL`](../tables/corelight-v2-tds-rpc-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_tds_sql_batch_CL`](../tables/corelight-v2-tds-sql-batch-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_traceroute_CL`](../tables/corelight-v2-traceroute-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_tunnel_CL`](../tables/corelight-v2-tunnel-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_unknown_smartpcap_CL`](../tables/corelight-v2-unknown-smartpcap-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_util_stats_CL`](../tables/corelight-v2-util-stats-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_vpn_CL`](../tables/corelight-v2-vpn-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_weird_CL`](../tables/corelight-v2-weird-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_weird_red_CL`](../tables/corelight-v2-weird-red-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_weird_stats_CL`](../tables/corelight-v2-weird-stats-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_wireguard_CL`](../tables/corelight-v2-wireguard-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`Corelight_v2_x509_CL`](../tables/corelight-v2-x509-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_x509_red_CL`](../tables/corelight-v2-x509-red-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | Workbooks |
| [`Corelight_v2_zeek_doctor_CL`](../tables/corelight-v2-zeek-doctor-cl.md) | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) | - |
| [`FilteredDNS`](../tables/filtereddns.md) | - | Workbooks |
| [`FilteredRDP`](../tables/filteredrdp.md) | - | Workbooks |
| [`FilteredVPN`](../tables/filteredvpn.md) | - | Workbooks |
| [`NxdomainResponses`](../tables/nxdomainresponses.md) | - | Workbooks |
| [`QueryResult`](../tables/queryresult.md) | - | Workbooks |
| [`QueryResults`](../tables/queryresults.md) | - | Workbooks |
| [`Records`](../tables/records.md) | - | Workbooks |
| [`SSL`](../tables/ssl.md) | - | Workbooks |
| [`TopSubjects`](../tables/topsubjects.md) | - | Workbooks |
| [`TotalRecords`](../tables/totalrecords.md) | - | Workbooks |
| [`UnencryptedConnection`](../tables/unencryptedconnection.md) | - | Workbooks |
| [`UnusualQtypes`](../tables/unusualqtypes.md) | - | Workbooks |
| [`VPNCount`](../tables/vpncount.md) | - | Workbooks |
| [`X509`](../tables/x509.md) | - | Workbooks |
| [`filter_record`](../tables/filter-record.md) | - | Workbooks |

## Content Items

This solution includes **151 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 122 |
| Analytic Rules | 10 |
| Hunting Queries | 10 |
| Workbooks | 5 |
| Watchlists | 4 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Corelight - C2 DGA Detected Via Repetitive Failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightC2RepetitiveFailures.yaml) | Medium | CommandAndControl | - |
| [Corelight - External Proxy Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightExternalProxyDetected.yaml) | Low | DefenseEvasion, CommandAndControl | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - Forced External Outbound SMB](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightForcedExternalOutboundSMB.yaml) | Medium | CredentialAccess | - |
| [Corelight - Multiple Compressed Files Transferred over HTTP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightMultipleCompressedFilesTransferredOverHTTP.yaml) | Medium | Exfiltration | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - Multiple files sent over HTTP with abnormal requests](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightMultipleFilesSentOverHTTPAbnormalRequests.yaml) | Medium | Exfiltration | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - Network Service Scanning Multiple IP Addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightNetworkServiceScanning.yaml) | Medium | InitialAccess | - |
| [Corelight - Possible Typo Squatting or Punycode Phishing HTTP Request](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightTypoSquattingOrPunycodePhishingHTTPRequest.yaml) | Medium | InitialAccess | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - Possible Webshell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightPossibleWebshell.yaml) | Medium | Persistence | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - Possible Webshell (Rare PUT or POST)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightPossibleWebshellRarePOST.yaml) | Medium | Persistence | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - SMTP Email containing NON Ascii Characters within the Subject](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Analytic%20Rules/CorelightSMTPEmailSubjectNonAsciiCharacters.yaml) | Low | InitialAccess | [`Corelight_v2_smtp_CL`](../tables/corelight-v2-smtp-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Corelight - Abnormal Email Subject](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightAbnormalEmailSubject.yaml) | InitialAccess | [`Corelight_v2_smtp_CL`](../tables/corelight-v2-smtp-cl.md) |
| [Corelight - Compressed Files Transferred over HTTP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightCompressedFilesTransferredOverHTTP.yaml) | Exfiltration | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - External Facing Services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightExternalServices.yaml) | InitialAccess | [`Corelight_v2_conn_CL`](../tables/corelight-v2-conn-cl.md)<br>[`Corelight_v2_conn_long_CL`](../tables/corelight-v2-conn-long-cl.md)<br>[`Corelight_v2_conn_red_CL`](../tables/corelight-v2-conn-red-cl.md) |
| [Corelight - File uploads by source](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightFilesTransferedByIp.yaml) | Exfiltration | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - Files in logs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightFilesSeen.yaml) | InitialAccess, Exfiltration | [`Corelight_v2_files_CL`](../tables/corelight-v2-files-cl.md)<br>[`Corelight_v2_files_red_CL`](../tables/corelight-v2-files-red-cl.md) |
| [Corelight - Multiple Remote SMB Connections from single client](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightMultipleRemoteSMBConnectionsFromSingleIP.yaml) | Discovery | [`Corelight_v2_smb_mapping_CL`](../tables/corelight-v2-smb-mapping-cl.md) |
| [Corelight - Obfuscated binary filenames](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightObfuscatedBinary.yaml) | InitialAccess | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - Rare PUT or POST](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightRarePOST.yaml) | Persistence | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |
| [Corelight - Repetitive DNS Failures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightRepetitiveDnsFailures.yaml) | CommandAndControl | [`Corelight_v2_dns_CL`](../tables/corelight-v2-dns-cl.md)<br>[`Corelight_v2_dns_red_CL`](../tables/corelight-v2-dns-red-cl.md) |
| [Corelight - Top sources of data transferred](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Hunting%20Queries/CorelightDataTransferedByIp.yaml) | Exfiltration | [`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [Corelight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Workbooks/Corelight.json) | [`Corelight_v2_conn_CL`](../tables/corelight-v2-conn-cl.md)<br>[`Corelight_v2_conn_long_CL`](../tables/corelight-v2-conn-long-cl.md)<br>[`Corelight_v2_conn_red_CL`](../tables/corelight-v2-conn-red-cl.md)<br>[`Corelight_v2_dns_CL`](../tables/corelight-v2-dns-cl.md)<br>[`Corelight_v2_dns_red_CL`](../tables/corelight-v2-dns-red-cl.md)<br>[`Corelight_v2_etc_viz_CL`](../tables/corelight-v2-etc-viz-cl.md)<br>[`Corelight_v2_files_CL`](../tables/corelight-v2-files-cl.md)<br>[`Corelight_v2_files_red_CL`](../tables/corelight-v2-files-red-cl.md)<br>[`Corelight_v2_ftp_CL`](../tables/corelight-v2-ftp-cl.md)<br>[`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md)<br>[`Corelight_v2_notice_CL`](../tables/corelight-v2-notice-cl.md)<br>[`Corelight_v2_rdp_CL`](../tables/corelight-v2-rdp-cl.md)<br>[`Corelight_v2_software_CL`](../tables/corelight-v2-software-cl.md)<br>[`Corelight_v2_ssl_CL`](../tables/corelight-v2-ssl-cl.md)<br>[`Corelight_v2_ssl_red_CL`](../tables/corelight-v2-ssl-red-cl.md)<br>[`Corelight_v2_vpn_CL`](../tables/corelight-v2-vpn-cl.md)<br>[`Corelight_v2_x509_CL`](../tables/corelight-v2-x509-cl.md)<br>[`Corelight_v2_x509_red_CL`](../tables/corelight-v2-x509-red-cl.md)<br>[`FilteredDNS`](../tables/filtereddns.md)<br>[`FilteredRDP`](../tables/filteredrdp.md)<br>[`FilteredVPN`](../tables/filteredvpn.md)<br>[`NxdomainResponses`](../tables/nxdomainresponses.md)<br>[`QueryResult`](../tables/queryresult.md)<br>[`QueryResults`](../tables/queryresults.md)<br>[`SSL`](../tables/ssl.md)<br>[`UnencryptedConnection`](../tables/unencryptedconnection.md)<br>[`UnusualQtypes`](../tables/unusualqtypes.md)<br>[`VPNCount`](../tables/vpncount.md)<br>[`X509`](../tables/x509.md) |
| [Corelight_Alert_Aggregations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Workbooks/Corelight_Alert_Aggregations.json) | [`Corelight_v2_conn_CL`](../tables/corelight-v2-conn-cl.md)<br>[`Corelight_v2_conn_long_CL`](../tables/corelight-v2-conn-long-cl.md)<br>[`Corelight_v2_conn_red_CL`](../tables/corelight-v2-conn-red-cl.md)<br>[`Corelight_v2_suricata_corelight_CL`](../tables/corelight-v2-suricata-corelight-cl.md) |
| [Corelight_Data_Explorer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Workbooks/Corelight_Data_Explorer.json) | [`Corelight_v2_conn_CL`](../tables/corelight-v2-conn-cl.md)<br>[`Corelight_v2_conn_long_CL`](../tables/corelight-v2-conn-long-cl.md)<br>[`Corelight_v2_conn_red_CL`](../tables/corelight-v2-conn-red-cl.md)<br>[`Corelight_v2_dns_CL`](../tables/corelight-v2-dns-cl.md)<br>[`Corelight_v2_dns_red_CL`](../tables/corelight-v2-dns-red-cl.md)<br>[`Corelight_v2_files_CL`](../tables/corelight-v2-files-cl.md)<br>[`Corelight_v2_files_red_CL`](../tables/corelight-v2-files-red-cl.md)<br>[`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md)<br>[`Corelight_v2_software_CL`](../tables/corelight-v2-software-cl.md)<br>[`Corelight_v2_ssl_CL`](../tables/corelight-v2-ssl-cl.md)<br>[`Corelight_v2_ssl_red_CL`](../tables/corelight-v2-ssl-red-cl.md)<br>[`QueryResults`](../tables/queryresults.md)<br>[`TopSubjects`](../tables/topsubjects.md)<br>[`TotalRecords`](../tables/totalrecords.md)<br>[`filter_record`](../tables/filter-record.md) |
| [Corelight_Security_Workflow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Workbooks/Corelight_Security_Workflow.json) | [`AggregationRecords`](../tables/aggregationrecords.md)<br>[`Corelight_v2_conn_CL`](../tables/corelight-v2-conn-cl.md)<br>[`Corelight_v2_conn_long_CL`](../tables/corelight-v2-conn-long-cl.md)<br>[`Corelight_v2_conn_red_CL`](../tables/corelight-v2-conn-red-cl.md)<br>[`Corelight_v2_dns_CL`](../tables/corelight-v2-dns-cl.md)<br>[`Corelight_v2_dns_red_CL`](../tables/corelight-v2-dns-red-cl.md)<br>[`Corelight_v2_etc_viz_CL`](../tables/corelight-v2-etc-viz-cl.md)<br>[`Corelight_v2_files_CL`](../tables/corelight-v2-files-cl.md)<br>[`Corelight_v2_files_red_CL`](../tables/corelight-v2-files-red-cl.md)<br>[`Corelight_v2_ftp_CL`](../tables/corelight-v2-ftp-cl.md)<br>[`Corelight_v2_http2_CL`](../tables/corelight-v2-http2-cl.md)<br>[`Corelight_v2_http_CL`](../tables/corelight-v2-http-cl.md)<br>[`Corelight_v2_http_red_CL`](../tables/corelight-v2-http-red-cl.md)<br>[`Corelight_v2_intel_CL`](../tables/corelight-v2-intel-cl.md)<br>[`Corelight_v2_notice_CL`](../tables/corelight-v2-notice-cl.md)<br>[`Corelight_v2_rdp_CL`](../tables/corelight-v2-rdp-cl.md)<br>[`Corelight_v2_smb_files_CL`](../tables/corelight-v2-smb-files-cl.md)<br>[`Corelight_v2_smtp_CL`](../tables/corelight-v2-smtp-cl.md)<br>[`Corelight_v2_ssh_CL`](../tables/corelight-v2-ssh-cl.md)<br>[`Corelight_v2_ssl_CL`](../tables/corelight-v2-ssl-cl.md)<br>[`Corelight_v2_ssl_red_CL`](../tables/corelight-v2-ssl-red-cl.md)<br>[`Corelight_v2_suricata_corelight_CL`](../tables/corelight-v2-suricata-corelight-cl.md)<br>[`Corelight_v2_vpn_CL`](../tables/corelight-v2-vpn-cl.md)<br>[`Corelight_v2_x509_CL`](../tables/corelight-v2-x509-cl.md)<br>[`Corelight_v2_x509_red_CL`](../tables/corelight-v2-x509-red-cl.md)<br>[`FilteredDNS`](../tables/filtereddns.md)<br>[`FilteredRDP`](../tables/filteredrdp.md)<br>[`FilteredVPN`](../tables/filteredvpn.md)<br>[`NxdomainResponses`](../tables/nxdomainresponses.md)<br>[`QueryResult`](../tables/queryresult.md)<br>[`QueryResults`](../tables/queryresults.md)<br>[`Records`](../tables/records.md)<br>[`SSL`](../tables/ssl.md)<br>[`UnencryptedConnection`](../tables/unencryptedconnection.md)<br>[`UnusualQtypes`](../tables/unusualqtypes.md)<br>[`VPNCount`](../tables/vpncount.md)<br>[`X509`](../tables/x509.md) |
| [Corelight_Sensor_Overview](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Workbooks/Corelight_Sensor_Overview.json) | [`Corelight_v2_corelight_metrics_disk_CL`](../tables/corelight-v2-corelight-metrics-disk-cl.md)<br>[`Corelight_v2_corelight_metrics_iface_CL`](../tables/corelight-v2-corelight-metrics-iface-cl.md)<br>[`Corelight_v2_corelight_metrics_memory_CL`](../tables/corelight-v2-corelight-metrics-memory-cl.md)<br>[`Corelight_v2_corelight_metrics_system_CL`](../tables/corelight-v2-corelight-metrics-system-cl.md)<br>[`Corelight_v2_corelight_metrics_zeek_doctor_CL`](../tables/corelight-v2-corelight-metrics-zeek-doctor-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Corelight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/Corelight.yaml) | - | - |
| [corelight_anomaly](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_anomaly.yaml) | - | - |
| [corelight_bacnet](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_bacnet.yaml) | - | - |
| [corelight_capture_loss](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_capture_loss.yaml) | - | - |
| [corelight_cip](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_cip.yaml) | - | - |
| [corelight_conn](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_conn.yaml) | - | - |
| [corelight_conn_agg](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_conn_agg.yaml) | - | - |
| [corelight_conn_long](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_conn_long.yaml) | - | - |
| [corelight_conn_red](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_conn_red.yaml) | - | - |
| [corelight_corelight_burst](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_corelight_burst.yaml) | - | - |
| [corelight_corelight_metrics_disk](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_corelight_metrics_disk.yaml) | - | - |
| [corelight_corelight_metrics_iface](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_corelight_metrics_iface.yaml) | - | - |
| [corelight_corelight_metrics_memory](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_corelight_metrics_memory.yaml) | - | - |
| [corelight_corelight_metrics_system](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_corelight_metrics_system.yaml) | - | - |
| [corelight_corelight_metrics_zeek_doctor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_corelight_metrics_zeek_doctor.yaml) | - | - |
| [corelight_corelight_overall_capture_loss](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_corelight_overall_capture_loss.yaml) | - | - |
| [corelight_corelight_profiling](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_corelight_profiling.yaml) | - | - |
| [corelight_datared](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_datared.yaml) | - | - |
| [corelight_dce_rpc](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_dce_rpc.yaml) | - | - |
| [corelight_dga](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_dga.yaml) | - | - |
| [corelight_dhcp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_dhcp.yaml) | - | - |
| [corelight_dnp3](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_dnp3.yaml) | - | - |
| [corelight_dns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_dns.yaml) | - | - |
| [corelight_dns_agg](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_dns_agg.yaml) | - | - |
| [corelight_dns_red](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_dns_red.yaml) | - | - |
| [corelight_dpd](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_dpd.yaml) | - | - |
| [corelight_encrypted_dns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_encrypted_dns.yaml) | - | - |
| [corelight_enip](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_enip.yaml) | - | - |
| [corelight_enip_debug](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_enip_debug.yaml) | - | - |
| [corelight_enip_list_identity](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_enip_list_identity.yaml) | - | - |
| [corelight_etc_viz](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_etc_viz.yaml) | - | - |
| [corelight_files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_files.yaml) | - | - |
| [corelight_files_agg](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_files_agg.yaml) | - | - |
| [corelight_files_red](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_files_red.yaml) | - | - |
| [corelight_first_seen](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_first_seen.yaml) | - | - |
| [corelight_ftp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_ftp.yaml) | - | - |
| [corelight_generic_dns_tunnels](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_generic_dns_tunnels.yaml) | - | - |
| [corelight_generic_icmp_tunnels](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_generic_icmp_tunnels.yaml) | - | - |
| [corelight_http](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_http.yaml) | - | - |
| [corelight_http2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_http2.yaml) | - | - |
| [corelight_http_agg](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_http_agg.yaml) | - | - |
| [corelight_http_red](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_http_red.yaml) | - | - |
| [corelight_icmp_specific_tunnels](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_icmp_specific_tunnels.yaml) | - | - |
| [corelight_intel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_intel.yaml) | - | - |
| [corelight_ipsec](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_ipsec.yaml) | - | - |
| [corelight_irc](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_irc.yaml) | - | - |
| [corelight_iso_cotp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_iso_cotp.yaml) | - | - |
| [corelight_kerberos](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_kerberos.yaml) | - | - |
| [corelight_known_certs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_known_certs.yaml) | - | - |
| [corelight_known_devices](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_known_devices.yaml) | - | - |
| [corelight_known_domains](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_known_domains.yaml) | - | - |
| [corelight_known_hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_known_hosts.yaml) | - | - |
| [corelight_known_names](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_known_names.yaml) | - | - |
| [corelight_known_remotes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_known_remotes.yaml) | - | - |
| [corelight_known_services](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_known_services.yaml) | - | - |
| [corelight_known_users](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_known_users.yaml) | - | - |
| [corelight_local_subnets](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_local_subnets.yaml) | - | - |
| [corelight_local_subnets_dj](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_local_subnets_dj.yaml) | - | - |
| [corelight_local_subnets_graphs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_local_subnets_graphs.yaml) | - | - |
| [corelight_log4shell](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_log4shell.yaml) | - | - |
| [corelight_modbus](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_modbus.yaml) | - | - |
| [corelight_mqtt_connect](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_mqtt_connect.yaml) | - | - |
| [corelight_mqtt_publish](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_mqtt_publish.yaml) | - | - |
| [corelight_mqtt_subscribe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_mqtt_subscribe.yaml) | - | - |
| [corelight_mysql](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_mysql.yaml) | - | - |
| [corelight_notice](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_notice.yaml) | - | - |
| [corelight_ntlm](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_ntlm.yaml) | - | - |
| [corelight_ntp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_ntp.yaml) | - | - |
| [corelight_ocsp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_ocsp.yaml) | - | - |
| [corelight_openflow](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_openflow.yaml) | - | - |
| [corelight_packet_filter](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_packet_filter.yaml) | - | - |
| [corelight_pe](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_pe.yaml) | - | - |
| [corelight_profinet](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_profinet.yaml) | - | - |
| [corelight_profinet_dce_rpc](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_profinet_dce_rpc.yaml) | - | - |
| [corelight_profinet_debug](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_profinet_debug.yaml) | - | - |
| [corelight_radius](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_radius.yaml) | - | - |
| [corelight_rdp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_rdp.yaml) | - | - |
| [corelight_reporter](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_reporter.yaml) | - | - |
| [corelight_rfb](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_rfb.yaml) | - | - |
| [corelight_s7comm](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_s7comm.yaml) | - | - |
| [corelight_signatures](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_signatures.yaml) | - | - |
| [corelight_sip](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_sip.yaml) | - | - |
| [corelight_smartpcap](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_smartpcap.yaml) | - | - |
| [corelight_smartpcap_stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_smartpcap_stats.yaml) | - | - |
| [corelight_smb_files](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_smb_files.yaml) | - | - |
| [corelight_smb_mapping](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_smb_mapping.yaml) | - | - |
| [corelight_smtp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_smtp.yaml) | - | - |
| [corelight_smtp_links](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_smtp_links.yaml) | - | - |
| [corelight_snmp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_snmp.yaml) | - | - |
| [corelight_socks](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_socks.yaml) | - | - |
| [corelight_software](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_software.yaml) | - | - |
| [corelight_specific_dns_tunnels](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_specific_dns_tunnels.yaml) | - | - |
| [corelight_ssh](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_ssh.yaml) | - | - |
| [corelight_ssl](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_ssl.yaml) | - | - |
| [corelight_ssl_agg](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_ssl_agg.yaml) | - | - |
| [corelight_ssl_red](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_ssl_red.yaml) | - | - |
| [corelight_stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_stats.yaml) | - | - |
| [corelight_stepping](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_stepping.yaml) | - | - |
| [corelight_stun](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_stun.yaml) | - | - |
| [corelight_stun_nat](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_stun_nat.yaml) | - | - |
| [corelight_suri_aggregations](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_suri_aggregations.yaml) | - | - |
| [corelight_suricata_corelight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_suricata_corelight.yaml) | - | - |
| [corelight_suricata_eve](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_suricata_eve.yaml) | - | - |
| [corelight_suricata_stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_suricata_stats.yaml) | - | - |
| [corelight_suricata_zeek_stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_suricata_zeek_stats.yaml) | - | - |
| [corelight_syslog](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_syslog.yaml) | - | - |
| [corelight_tds](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_tds.yaml) | - | - |
| [corelight_tds_rpc](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_tds_rpc.yaml) | - | - |
| [corelight_tds_sql_batch](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_tds_sql_batch.yaml) | - | - |
| [corelight_traceroute](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_traceroute.yaml) | - | - |
| [corelight_tunnel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_tunnel.yaml) | - | - |
| [corelight_unknown_smartpcap](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_unknown_smartpcap.yaml) | - | - |
| [corelight_util_stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_util_stats.yaml) | - | - |
| [corelight_vpn](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_vpn.yaml) | - | - |
| [corelight_weird](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_weird.yaml) | - | - |
| [corelight_weird_agg](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_weird_agg.yaml) | - | - |
| [corelight_weird_red](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_weird_red.yaml) | - | - |
| [corelight_weird_stats](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_weird_stats.yaml) | - | - |
| [corelight_wireguard](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_wireguard.yaml) | - | - |
| [corelight_x509](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_x509.yaml) | - | - |
| [corelight_x509_red](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_x509_red.yaml) | - | - |
| [corelight_zeek_doctor](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Parsers/corelight_zeek_doctor.yaml) | - | - |

### Watchlists

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [CorelightAggregationsEnrichment1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Watchlists/CorelightAggregationsEnrichment1.json) | - | - |
| [CorelightAggregationsEnrichment2](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Watchlists/CorelightAggregationsEnrichment2.json) | - | - |
| [CorelightDNSPortDesc](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Watchlists/CorelightDNSPortDesc.json) | - | - |
| [CorelightInferencesDesc](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Watchlists/CorelightInferencesDesc.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.2.2       | 01-12-2025                     | Added Corelight Aggregation Parsers.
| 3.2.1       | 30-10-2025                     | Added corelight_first_seen and corelight_anomaly Parsers.
| 3.2.0       | 05-03-2025                     | Added new Parsers, Workbooks and Watchlists.
| 3.1.0       | 27-09-2024                     | Updated Parsers and added new tabs in Workbook.
| 3.0.2       | 31-01-2024                     | Updated **Parser** Corelight <br/> Updated tactics of **Hunting Query** Corelight - Repetitive DNS Failures                             |
| 3.0.1       | 16-11-2023                     | Updated package mainTemplate variables                             |
| 3.0.0       | 20-09-2023                     | Changed backend format to use separate tables with parsed values   |
| 2.0.0       | 10-06-2022                     | Updated **Workbooks**                                               | 
| 1.1.0       | 22-10-2021                     | Packaging updates                                                  |
| 1.0.2       | 22-04-2021                     | Updated instructions, rules, LA config                              |
| 1.0.1       | 09-04-2021                     | Updated **Analytic Rule**                                           |
| 1.0.0       | 01-04-2021                     | Initial Solution Release                                           |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
