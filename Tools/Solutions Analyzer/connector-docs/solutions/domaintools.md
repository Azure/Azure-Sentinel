# DomainTools

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | DomainTools |
| **Support Tier** | Partner |
| **Support Link** | [https://www.domaintools.com/support/](https://www.domaintools.com/support/) |
| **Categories** | domains |
| **First Published** | 2022-10-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools) |

## Data Connectors

**This solution does not include data connectors.**

This solution may contain other components such as analytics rules, workbooks, hunting queries, or playbooks.

## Content Items

This solution includes **40 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 39 |
| Parsers | 1 |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Domain ASIM Enrichment - DomainTools Iris Enrich](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/DomainTools-ASIM-DNS-Playbook/azuredeploy.json) | Given a domain or set of domains associated with an alert return all Iris Enrich data for those doma... | - |
| [Domain Enrichment - DomainTools Iris Enrich](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/DomainTools-Iris-Enrich-Playbook/azuredeploy.json) | Given a domain or set of domains associated with an incident return all Iris Enrich data for those d... | - |
| [Domain Enrichment - DomainTools Iris Investigate](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/DomainTools-Iris-Investigate-Playbook/azuredeploy.json) | Given a domain or set of domains associated with an incident return all Iris Investigate data for th... | - |
| [DomainTools DNSDB Co-Located Hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/DomainTools-DNSDB-Co-Located-Hosts/azuredeploy.json) | This playbook uses the Farsight DNSDB connector to automatically enrich Domain's found in the Micros... | - |
| [DomainTools DNSDB Co-Located IP Addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/DomainTools-DNSDB-Co-Located-Addresses/azuredeploy.json) | This playbook uses the Farsight DNSDB connector to automatically enrich IP Addresses found in the Mi... | - |
| [DomainTools DNSDB Historical Hosts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/DomainTools-DNSDB-Historical-Hosts/azuredeploy.json) | This playbook uses the Farsight DNSDB connector to automatically enrich Domain's found in the Micros... | - |
| [DomainTools DNSDB Historical IP Addresses](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/DomainTools-DNSDB-Historical-Addresses/azuredeploy.json) | This playbook uses the Farsight DNSDB connector to automatically enrich IP Addresses found in the Mi... | - |
| [DomainTools_FunctionAppConnector](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/azuredeploy.json) | - | - |
| [IP Enrichment - DomainTools Parsed Whois](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/DomainTools-IP-Address-Playbook/azuredeploy.json) | This playbook uses the DomainTools Parsed Whois API. Given a ip address or set of ip addresses assoc... | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ClassicReverseIP/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/DomainProfile/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/DomainRiskScore/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/DomainSearch/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/EnrichDomain/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/Evidence/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/HostingHistory/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/InvestigateDomain/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ParsedWhois/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/PivotByMXIP/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/PivotByNameserverIPAddress/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/PivotByRegistrantName/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/PivotByRegistrantOrg/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/PivotBySSLHash/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/PivotMXHost/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/PivotNameServerHost/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/PivotSSLEmail/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReturnDomainsFromSearchHash/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReturnTaggedWithAll/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReturnTaggedWithAny/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReverseEmail/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReverseEmailDomain/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReverseIP/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReverseIPHost-Domains/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReverseIPWhois/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReverseNameServer/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/ReverseWhois/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/WhoisHistory/function.json) | - | - |
| [function](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/WhoisLookup/function.json) | - | - |
| [host](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Playbooks/CustomConnector/DomainTools_FunctionAppConnector/host.json) | - | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [DomainToolsDNS](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/DomainTools/Parsers/DomainToolsDNS.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                        |
|-------------|--------------------------------|---------------------------------------------------------------------------|
| 3.0.0       | 29-01-2024                     | App insights to LA change in data connector and repackage                 |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
