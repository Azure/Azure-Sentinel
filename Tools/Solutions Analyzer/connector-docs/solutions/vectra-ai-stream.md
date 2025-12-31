# Vectra AI Stream

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Vectra AI |
| **Support Tier** | Partner |
| **Support Link** | [https://www.vectra.ai/support](https://www.vectra.ai/support) |
| **Categories** | domains |
| **First Published** | 2021-10-18 |
| **Last Updated** | 2024-05-02 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream) |

## Data Connectors

This solution provides **2 data connector(s)**:

- [AI Vectra Stream via Legacy Agent](../connectors/aivectrastream.md)
- [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md)

## Tables Reference

This solution uses **19 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`VectraStream`](../tables/vectrastream.md) | [AI Vectra Stream via Legacy Agent](../connectors/aivectrastream.md) | - |
| [`VectraStream_CL`](../tables/vectrastream-cl.md) | [AI Vectra Stream via Legacy Agent](../connectors/aivectrastream.md) | - |
| [`vectra_beacon_CL`](../tables/vectra-beacon-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_dcerpc_CL`](../tables/vectra-dcerpc-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_dhcp_CL`](../tables/vectra-dhcp-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_dns_CL`](../tables/vectra-dns-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_http_CL`](../tables/vectra-http-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_isession_CL`](../tables/vectra-isession-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_kerberos_CL`](../tables/vectra-kerberos-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_ldap_CL`](../tables/vectra-ldap-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_ntlm_CL`](../tables/vectra-ntlm-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_radius_CL`](../tables/vectra-radius-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_rdp_CL`](../tables/vectra-rdp-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_smbfiles_CL`](../tables/vectra-smbfiles-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_smbmapping_CL`](../tables/vectra-smbmapping-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_smtp_CL`](../tables/vectra-smtp-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_ssh_CL`](../tables/vectra-ssh-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_ssl_CL`](../tables/vectra-ssl-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |
| [`vectra_x509_CL`](../tables/vectra-x509-cl.md) | [[Recommended] Vectra AI Stream via AMA](../connectors/vectrastreamama.md) | - |

## Content Items

This solution includes **20 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Parsers | 20 |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [VectraStream_function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/VectraStream_function.yaml) | - | - |
| [vectra_beacon](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_beacon.yaml) | - | - |
| [vectra_dcerpc](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_dcerpc.yaml) | - | - |
| [vectra_dhcp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_dhcp.yaml) | - | - |
| [vectra_dns](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_dns.yaml) | - | - |
| [vectra_http](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_http.yaml) | - | - |
| [vectra_isession](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_isession.yaml) | - | - |
| [vectra_kerberos](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_kerberos.yaml) | - | - |
| [vectra_ldap](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_ldap.yaml) | - | - |
| [vectra_match](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_match.yaml) | - | - |
| [vectra_ntlm](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_ntlm.yaml) | - | - |
| [vectra_radius](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_radius.yaml) | - | - |
| [vectra_rdp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_rdp.yaml) | - | - |
| [vectra_smbfiles](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_smbfiles.yaml) | - | - |
| [vectra_smbmapping](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_smbmapping.yaml) | - | - |
| [vectra_smtp](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_smtp.yaml) | - | - |
| [vectra_ssh](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_ssh.yaml) | - | - |
| [vectra_ssl](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_ssl.yaml) | - | - |
| [vectra_stream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_stream.yaml) | - | - |
| [vectra_x509](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Vectra%20AI%20Stream/Parsers/vectra_x509.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                             |
|-------------|--------------------------------|--------------------------------------------------------------------------------|
| 3.0.1       | 19-11-2024                     |Added new **Parser** vectra_match to the Solution </br>Update the solution to support a new metadata type: match (suricata)| 
| 3.0.0       | 10-07-2024                     | Added new **AMA Data Connector**</br> Removed deprecated content **Hunting Queries** And **Workbooks**</br> Added new **Parsers** to the Solution   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
