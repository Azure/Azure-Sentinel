# Corelight

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Corelight |
| **Support Tier** | Partner |
| **Support Link** | [https://support.corelight.com/](https://support.corelight.com/) |
| **Categories** | domains |
| **First Published** | 2022-06-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md)

**Publisher:** Corelight

The [Corelight](https://corelight.com/) data connector enables incident responders and threat hunters who use Microsoft Sentinel to work faster and more effectively. The data connector enables ingestion of events from [Zeek](https://zeek.org/) and [Suricata](https://suricata-ids.org/) via Corelight Sensors into Microsoft Sentinel.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required. [See the documentation to learn more about workspace keys](https://docs.microsoft.com/azure/azure-monitor/platform/agent-windows#obtain-workspace-id-and-key).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

>**NOTE:** This data connector depends on a parser based on a Kusto Function to work as expected [**Corelight**](https://aka.ms/sentinel-Corelight-parser) which is deployed with the Microsoft Sentinel Solution.

**1. Get the files**

Contact your TAM, SE, or info@corelight.com to get the files needed for the Microsoft Sentinel integration.

**2. Replay sample data.**

Replay sample data to create the needed tables in your Log Analytics workspace.
- **Send sample data (only needed once per Log Analytics workspace)**: `./send_samples.py --workspace-id {0} --workspace-key {1}`

**3. Install custom exporter.**

Install the custom exporter or the logstash container.

**4. Configure the Corelight Sensor to send logs to the Azure Log Analytics Agent.**

Using the following values, configure your Corelight Sensor to use the Microsoft Sentinel exporter. Alternatively, you can configure the logstash container with these values and configure your sensor to send JSON over TCP to that container on the appropriate port.
- **Workspace ID**: `WorkspaceId`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*
- **Primary Workspace Key**: `PrimaryKey`
  > *Note: The value above is dynamically provided when these instructions are presented within Microsoft Sentinel.*

| | |
|--------------------------|---|
| **Tables Ingested** | `Corelight_CL` |
| | `Corelight_v2_bacnet_CL` |
| | `Corelight_v2_capture_loss_CL` |
| | `Corelight_v2_cip_CL` |
| | `Corelight_v2_conn_CL` |
| | `Corelight_v2_conn_long_CL` |
| | `Corelight_v2_conn_red_CL` |
| | `Corelight_v2_corelight_burst_CL` |
| | `Corelight_v2_corelight_overall_capture_loss_CL` |
| | `Corelight_v2_corelight_profiling_CL` |
| | `Corelight_v2_datared_CL` |
| | `Corelight_v2_dce_rpc_CL` |
| | `Corelight_v2_dga_CL` |
| | `Corelight_v2_dhcp_CL` |
| | `Corelight_v2_dnp3_CL` |
| | `Corelight_v2_dns_CL` |
| | `Corelight_v2_dns_red_CL` |
| | `Corelight_v2_dpd_CL` |
| | `Corelight_v2_encrypted_dns_CL` |
| | `Corelight_v2_enip_CL` |
| | `Corelight_v2_enip_debug_CL` |
| | `Corelight_v2_enip_list_identity_CL` |
| | `Corelight_v2_etc_viz_CL` |
| | `Corelight_v2_files_CL` |
| | `Corelight_v2_files_red_CL` |
| | `Corelight_v2_ftp_CL` |
| | `Corelight_v2_generic_dns_tunnels_CL` |
| | `Corelight_v2_generic_icmp_tunnels_CL` |
| | `Corelight_v2_http2_CL` |
| | `Corelight_v2_http_CL` |
| | `Corelight_v2_http_red_CL` |
| | `Corelight_v2_icmp_specific_tunnels_CL` |
| | `Corelight_v2_intel_CL` |
| | `Corelight_v2_ipsec_CL` |
| | `Corelight_v2_irc_CL` |
| | `Corelight_v2_iso_cotp_CL` |
| | `Corelight_v2_kerberos_CL` |
| | `Corelight_v2_known_certs_CL` |
| | `Corelight_v2_known_devices_CL` |
| | `Corelight_v2_known_domains_CL` |
| | `Corelight_v2_known_hosts_CL` |
| | `Corelight_v2_known_names_CL` |
| | `Corelight_v2_known_remotes_CL` |
| | `Corelight_v2_known_services_CL` |
| | `Corelight_v2_known_users_CL` |
| | `Corelight_v2_local_subnets_CL` |
| | `Corelight_v2_local_subnets_dj_CL` |
| | `Corelight_v2_local_subnets_graphs_CL` |
| | `Corelight_v2_log4shell_CL` |
| | `Corelight_v2_modbus_CL` |
| | `Corelight_v2_mqtt_connect_CL` |
| | `Corelight_v2_mqtt_publish_CL` |
| | `Corelight_v2_mqtt_subscribe_CL` |
| | `Corelight_v2_mysql_CL` |
| | `Corelight_v2_notice_CL` |
| | `Corelight_v2_ntlm_CL` |
| | `Corelight_v2_ntp_CL` |
| | `Corelight_v2_ocsp_CL` |
| | `Corelight_v2_openflow_CL` |
| | `Corelight_v2_packet_filter_CL` |
| | `Corelight_v2_pe_CL` |
| | `Corelight_v2_profinet_CL` |
| | `Corelight_v2_profinet_dce_rpc_CL` |
| | `Corelight_v2_profinet_debug_CL` |
| | `Corelight_v2_radius_CL` |
| | `Corelight_v2_rdp_CL` |
| | `Corelight_v2_reporter_CL` |
| | `Corelight_v2_rfb_CL` |
| | `Corelight_v2_s7comm_CL` |
| | `Corelight_v2_signatures_CL` |
| | `Corelight_v2_sip_CL` |
| | `Corelight_v2_smartpcap_CL` |
| | `Corelight_v2_smartpcap_stats_CL` |
| | `Corelight_v2_smb_files_CL` |
| | `Corelight_v2_smb_mapping_CL` |
| | `Corelight_v2_smtp_CL` |
| | `Corelight_v2_smtp_links_CL` |
| | `Corelight_v2_snmp_CL` |
| | `Corelight_v2_socks_CL` |
| | `Corelight_v2_software_CL` |
| | `Corelight_v2_specific_dns_tunnels_CL` |
| | `Corelight_v2_ssh_CL` |
| | `Corelight_v2_ssl_CL` |
| | `Corelight_v2_ssl_red_CL` |
| | `Corelight_v2_stats_CL` |
| | `Corelight_v2_stepping_CL` |
| | `Corelight_v2_stun_CL` |
| | `Corelight_v2_stun_nat_CL` |
| | `Corelight_v2_suricata_corelight_CL` |
| | `Corelight_v2_suricata_eve_CL` |
| | `Corelight_v2_suricata_stats_CL` |
| | `Corelight_v2_suricata_zeek_stats_CL` |
| | `Corelight_v2_syslog_CL` |
| | `Corelight_v2_tds_CL` |
| | `Corelight_v2_tds_rpc_CL` |
| | `Corelight_v2_tds_sql_batch_CL` |
| | `Corelight_v2_traceroute_CL` |
| | `Corelight_v2_tunnel_CL` |
| | `Corelight_v2_unknown_smartpcap_CL` |
| | `Corelight_v2_util_stats_CL` |
| | `Corelight_v2_vpn_CL` |
| | `Corelight_v2_weird_CL` |
| | `Corelight_v2_weird_red_CL` |
| | `Corelight_v2_weird_stats_CL` |
| | `Corelight_v2_wireguard_CL` |
| | `Corelight_v2_x509_CL` |
| | `Corelight_v2_x509_red_CL` |
| | `Corelight_v2_zeek_doctor_CL` |
| **Connector Definition Files** | [CorelightConnectorExporter.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Corelight/Data%20Connectors/CorelightConnectorExporter.json) |

[→ View full connector details](../connectors/corelightconnectorexporter.md)

## Tables Reference

This solution ingests data into **108 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `Corelight_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_bacnet_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_capture_loss_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_cip_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_conn_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_conn_long_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_conn_red_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_corelight_burst_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_corelight_overall_capture_loss_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_corelight_profiling_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_datared_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_dce_rpc_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_dga_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_dhcp_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_dnp3_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_dns_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_dns_red_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_dpd_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_encrypted_dns_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_enip_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_enip_debug_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_enip_list_identity_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_etc_viz_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_files_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_files_red_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_ftp_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_generic_dns_tunnels_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_generic_icmp_tunnels_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_http2_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_http_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_http_red_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_icmp_specific_tunnels_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_intel_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_ipsec_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_irc_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_iso_cotp_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_kerberos_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_known_certs_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_known_devices_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_known_domains_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_known_hosts_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_known_names_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_known_remotes_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_known_services_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_known_users_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_local_subnets_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_local_subnets_dj_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_local_subnets_graphs_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_log4shell_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_modbus_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_mqtt_connect_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_mqtt_publish_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_mqtt_subscribe_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_mysql_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_notice_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_ntlm_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_ntp_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_ocsp_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_openflow_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_packet_filter_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_pe_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_profinet_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_profinet_dce_rpc_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_profinet_debug_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_radius_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_rdp_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_reporter_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_rfb_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_s7comm_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_signatures_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_sip_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_smartpcap_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_smartpcap_stats_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_smb_files_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_smb_mapping_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_smtp_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_smtp_links_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_snmp_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_socks_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_software_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_specific_dns_tunnels_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_ssh_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_ssl_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_ssl_red_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_stats_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_stepping_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_stun_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_stun_nat_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_suricata_corelight_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_suricata_eve_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_suricata_stats_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_suricata_zeek_stats_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_syslog_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_tds_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_tds_rpc_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_tds_sql_batch_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_traceroute_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_tunnel_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_unknown_smartpcap_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_util_stats_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_vpn_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_weird_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_weird_red_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_weird_stats_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_wireguard_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_x509_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_x509_red_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |
| `Corelight_v2_zeek_doctor_CL` | [Corelight Connector Exporter](../connectors/corelightconnectorexporter.md) |

[← Back to Solutions Index](../solutions-index.md)
