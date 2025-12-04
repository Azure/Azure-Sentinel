# Vectra AI Stream

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Vectra AI |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vectra.ai/support](https://www.vectra.ai/support) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Last Updated** | 2024-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream) |\n\n## Data Connectors

This solution provides **2 data connector(s)**.

### AI Vectra Stream via Legacy Agent

**Publisher:** Vectra AI

The AI Vectra Stream connector allows to send Network Metadata collected by Vectra Sensors accross the Network and Cloud to Microsoft Sentinel

**Tables Ingested:**

- `VectraStream`
- `VectraStream_CL`

**Connector Definition Files:**

- [Connector_VectraAI_Stream.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Data%20Connectors/Connector_VectraAI_Stream.json)

### [Recommended] Vectra AI Stream via AMA

**Publisher:** Vectra AI

The Vectra AI Stream connector allows to send Network Metadata collected by Vectra Sensors accross the Network and Cloud to Microsoft Sentinel

**Tables Ingested:**

- `vectra_beacon_CL`
- `vectra_dcerpc_CL`
- `vectra_dhcp_CL`
- `vectra_dns_CL`
- `vectra_http_CL`
- `vectra_isession_CL`
- `vectra_kerberos_CL`
- `vectra_ldap_CL`
- `vectra_ntlm_CL`
- `vectra_radius_CL`
- `vectra_rdp_CL`
- `vectra_smbfiles_CL`
- `vectra_smbmapping_CL`
- `vectra_smtp_CL`
- `vectra_ssh_CL`
- `vectra_ssl_CL`
- `vectra_x509_CL`

**Connector Definition Files:**

- [template_VectraStreamAma.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Data%20Connectors/template_VectraStreamAma.json)

## Tables Reference

This solution ingests data into **19 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `VectraStream` | AI Vectra Stream via Legacy Agent |
| `VectraStream_CL` | AI Vectra Stream via Legacy Agent |
| `vectra_beacon_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_dcerpc_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_dhcp_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_dns_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_http_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_isession_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_kerberos_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_ldap_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_ntlm_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_radius_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_rdp_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_smbfiles_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_smbmapping_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_smtp_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_ssh_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_ssl_CL` | [Recommended] Vectra AI Stream via AMA |
| `vectra_x509_CL` | [Recommended] Vectra AI Stream via AMA |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n