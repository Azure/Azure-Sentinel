# FullHunt Custom Connector

## Summary

A Logic Apps custom connector for the [FullHunt API](https://docs.fullhunt.io). The FullHunt playbooks in this solution use it, and you can use its actions in your own playbooks. It authenticates with the `X-API-KEY` header.

Only read-only lookups are included. Active scanning, organization management and OEM endpoints are not exposed. Lookups consume FullHunt credits (1 per call); `AuthStatus` is free and returns your remaining credits.

| Action | Endpoint | Description |
|---|---|---|
| AuthStatus | `GET /auth/status` | Returns the API key's account status and remaining credits. Does not consume credits. |
| GetHost | `GET /host/{host}` | Returns FullHunt's attack surface record for a host name (not an IP address). 1 credit. |
| GetDomainDetails | `GET /domain/{domain}/details` | Returns metadata, WHOIS data and full host records for an apex domain. 1 credit. Responses can be large for big domains. |
| GetDomainSubdomains | `GET /domain/{domain}/subdomains` | Returns metadata, WHOIS data and subdomain names for an apex domain. 1 credit. |
| IntelIpToHosts | `GET /intel/ip-to-hosts` | Hosts that resolve to an IPv4 address. Requires the Data Intelligence module. 1 credit. |
| IntelIpRangeToHosts | `GET /intel/ip-range-to-hosts` | Hosts in an IPv4 range. Requires the Data Intelligence module. 1 credit. |
| IntelAsnToHosts | `GET /intel/asn-to-hosts` | Hosts announced by an autonomous system. Requires the Data Intelligence module. 1 credit. |
| IntelAsnToVirtualHosts | `GET /intel/asn-to-virtual-hosts` | Virtual hosts in an autonomous system. Requires the Data Intelligence module. 1 credit. |
| IntelDomain | `GET /intel/domain` | Hosts under an apex domain. Requires the Data Intelligence module. 1 credit. |
| IntelHost | `GET /intel/host` | Intel record for a host name. Requires the Data Intelligence module. 1 credit. |
| IntelProduct | `GET /intel/product` | Hosts running a product. Requires the Data Intelligence module. 1 credit. |
| IntelTag | `GET /intel/tag` | Hosts with a FullHunt tag. Requires the Data Intelligence module. 1 credit. |
| IntelWebTech | `GET /intel/web-tech` | Hosts using a web technology. Requires the Data Intelligence module. 1 credit. |
| IntelDnsMxToHosts | `GET /intel/dns-mx-to-hosts` | Hosts using an MX server. Requires the Data Intelligence module. 1 credit. |
| IntelDnsNsToHosts | `GET /intel/dns-ns-to-hosts` | Hosts using a name server. Requires the Data Intelligence module. 1 credit. |
| NexusIpLookup | `GET /nexus/ip-lookup` | Network, geolocation, cloud and CDN context for an IPv4 address or host name. 1 credit. |
| NexusTorCheckIp | `GET /nexus/tor/check-ip` | Checks whether an IP is a known Tor exit node. Always returns HTTP 200; check the body status (200 found, 404 not found). 1 credit. |
| NexusCloudCertsDnsSearch | `GET /nexus/cloud-certs/dns-search` | Certificates observed on cloud infrastructure whose DNS names start with the query. 1 credit. |
| NexusPassiveDnsLookup | `GET /nexus/passive-dns/lookup` | Host names observed for an apex domain in passive DNS. 1 credit. |
| NexusDomainCollectionLookup | `GET /nexus/domain-collection/lookup` | Organization and asset-collection context for an apex domain. 1 credit. |
| NexusDomainCollectionCompanyLookup | `GET /nexus/domain-collection/company-lookup` | Domain collections that match a company name. 1 credit. |
| NexusWhoisLookup | `GET /nexus/whois/lookup` | WHOIS record for an apex domain. 1 credit. |
| NexusWhoisSearch | `GET /nexus/whois/search` | Domains that match WHOIS filters. Provide at least one filter. 1 credit. |
| VulnerabilitySearch | `GET /vulnerability-intelligence/vulnerability-search` | CVE intelligence: CVSS, EPSS, KEV, exploit availability and advisories. Query by upper-case CVE ID, CPE or keyword. 1 credit. |
| ExploitsSearch | `GET /vulnerability-intelligence/exploits-search` | Exploit and known-exploited records for a CVE ID or keyword. 1 credit. |
| AdvisoriesSearch | `GET /vulnerability-intelligence/advisories-search` | Security advisories (GHSA, OSV and others) for a CVE ID, advisory ID, keyword, ecosystem or package. 1 credit. |

### Prerequisites

1. A FullHunt API key.

### Deployment Instructions

1. Click the Deploy to Azure button. This launches the ARM template deployment wizard.
2. Fill in the parameters:
   * FullHuntConnectorName: Name of the custom connector (default: FullHuntCustomConnector). Use the same value in the playbooks' `FullHuntConnectorName` parameter.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHuntCustomConnector%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FFullHunt%2FPlaybooks%2FFullHuntCustomConnector%2Fazuredeploy.json)

### Post-Deployment Instructions

1. Deploy the FullHunt playbooks to the same resource group.
2. In each playbook, authorize the FullHunt API connection with your API key.
