# DomainTools API Function App Connector

This Function App Connector is to connect DomainTools API.

### Authentication methods supported by this connector

* Custom Authentication (HMAC)

### Prerequisites For DomainTools Function App Connector

* DomainTools API Username
* DomainTools API Key 
* Visit https://www.domaintools.com/integrations to request a Api key.

## Actions supported by DomainTools Function App Connector

| **Component** | **Description** |
| --------- | -------------- |
| **InvestigateDomain** | Domain (e.g. name.tld) to be investigated or comma-separated list of domains; iris-investigate API. |
| **EnrichDomain** | Domain (e.g. name.tld) to be investigated or comma-separated list of domains; iris-enrich API. |
| **ClassicReverseIP** | List of domains that share the same IP address (Internet host). |
| **DomainProfile** |Basic registrant, server, and registration data for a domain name, plus preview data for other products. |
| **DomainRiskScore** | Provides risk scores and threat predictions based on DomainTools Proximity and Threat Profile algorithms. |
| **DomainSearch** | Searches active and deleted domain names that match a query string. |
| **Evidence** | Provides evidence reasons of the the risk score, such as 'blocklist', 'dns', 'realtime', 'registrant', or 'zerolist'. |
| **HostingHistory** | Provides the registrar, IP and name server history for a domain name. |
| **ParsedWhois** | Parsed results for Whois records for domain names and IP addresses. |
| **PivotByMXIP** | IP address of the mail server to be investigated. |
| **PivotByNameserverIPAddress** | IP address of the name server to be investigated. |
| **PivotByRegistrantName** | Substring search on the Whois registrant field to be investigated. |
| **PivotByRegistrantOrg** | Substring search on the Whois registrant org field to be investigated. |
| **PivotBySSLHash** | SSL certificate SHA-1 hash to be investigated. |
| **PivotMXHost** | Fully-qualified host name of the mail server (mx.domaintools.net) to be investigated. |
| **PivotNameServerHost** |Fully-qualified host name of the name server (ns1.domaintools.net) to be investigated. |
| **PivotSSLEmail** | Email address from the SSL certificate to be investigated. |
| **ReturnDomainsFromSearchHash** | Encoded search from the Iris UI. |
| **ReturnTaggedWithAll** | Comma-separated list of tags. Only returns domains tagged with the full list of tags. |
| **ReturnTaggedWithAny** | Comma-separated list of Iris Investigate tags. Returns domains tagged with any of the tags in a list. |
| **ReverseEmail** | Email address from the most recently available Whois record, DNS SOA record or SSL certificate. |
| **ReverseEmailDomain** | Only the domain portion of a Whois or DNS SOA email address. |
| **ReverseIP** | IPv4 address the registered domain was last known to point to during an active DNS check. |
| **ReverseIPHost-Domains** | List of domains that share the same network host. |
| **ReverseIPWhois** | Provides a list of IP network ranges with Whois records that match a specific query. |
| **ReverseNameServer** | List of domains that share the same primary name server. |
| **ReverseWhois** | Provides a list of domain names with Whois records that match a specific query. |
| **WhoisHistory** | Retrieve historical Whois records of a given domain name. |
| **WhoisLookup** | Whois records for domain names and IP addresses. |



### Deployment Instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - DomainTools Username 
    - DomainTools API Key

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDomainTools%2FPlaybooks%2FCustomConnector%2FDomainTools_FunctionAppConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FDomainTools%2FPlaybooks%2FCustomConnector%2FDomainTools_FunctionAppConnector%2Fazuredeploy.json)

### Function App Settings (DomainTools Username, DomainTools API Key) Update Instruction
1. Select the Function App.
2. Click on the Configuration blade under Settings.
3. Select the Application settings tab.
4. Click on the Edit for a setting.
5. Update the Values.
6. Click Ok to save.