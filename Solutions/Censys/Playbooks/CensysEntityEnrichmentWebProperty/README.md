# Censys Entity Enrichment - Web Property

## Summary

This playbook is triggered automatically when a DNS entity (domain name) is detected in a Microsoft Sentinel incident, based on an automation rule. Upon triggering, it extracts the domain name from the entity and queries the Censys API (v3) to retrieve detailed web property information including geolocation (continent, country, city, coordinates), autonomous system details (ASN, BGP prefix), WHOIS data (network, organization, contacts), services, and DNS information. The playbook constructs the web property endpoint URL using the domain name with port 443 (e.g., domain:443). The playbook retrieves the Censys API token securely from Azure Key Vault, performs the API call with retry logic (up to 3 attempts) and comprehensive error handling for HTTP status codes (200, 401, 403, 404, 422). Upon successful data retrieval, the web property data is ingested into Azure Log Analytics (Censyswebproperty_CL table) for historical analysis and reporting. The playbook then retrieves the associated incident and invokes the CensysIncidentEnrichment sub-playbook to add the enrichment data as a comment to the incident. If no incident is associated, the playbook terminates successfully after data ingestion.

### Prerequisites

1. Deploy the CensysIncidentEnrichment playbook before deploying this playbook.
2. Create an Azure Key Vault and store your Censys API token as a secret named 'Censys-Access-Token'.
3. Obtain your Censys Organization ID from the Censys platform account settings.
4. Configure an automation rule in Microsoft Sentinel to trigger this playbook when DNS entities are detected.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: CensysEntityEnrichmentWebProperty).
   * Ports: Comma-separated list of ports to query for host enrichment (default: 80,443).
   * OrganizationID: Your Censys Organization ID from the Censys platform account settings.
   * IncidentEnrichmentPlaybookName: Name of the deployed CensysAddIncidentComment playbook.
   * KeyVaultName: Name of the Azure Key Vault where the Censys API token is stored.
   * TenantId: Azure AD Tenant ID where the Key Vault is located.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysEntityEnrichmentWebProperty%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysEntityEnrichmentWebProperty%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for Microsoft Sentinel and Log Analytics Data Collector connections.

#### b. Add Access policy in Key Vault

Grant the playbook's managed identity 'Key Vault Secrets User' role on the Azure Key Vault.
1. Go to Logic App → *your Logic App* → Identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to Key Vaults → *your Key Vault* → Access policies → Create.
3. Select Get and List permissions for Secrets. Click Next.
4. In the principal section, search by copied Object ID. Click Next.
5. Click Review + Create.

#### c. Create automation rule in Microsoft Sentinel

Create an automation rule in Microsoft Sentinel to trigger this playbook for DNS entities.
1. Go to Microsoft Sentinel → *your workspace* → Automation.
2. Click Create → Automation rule.
3. Configure the rule to trigger when DNS entities are detected.
4. Add action to run this playbook.
5. Click Apply.

#### d. Ensure CensysIncidentEnrichment playbook is deployed

Ensure the CensysIncidentEnrichment (or CensysAddIncidentComment) playbook is deployed and accessible.
