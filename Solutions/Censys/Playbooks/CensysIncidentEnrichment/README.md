# Censys Incident Enrichment

## Summary

This playbook will be triggered when any automation rule is attached or manually invoked. This will fetch associated IPs, Host(Domains) and SHAs from incident and make associated API calls to retrieve Censys data and enrich incident with additional information as Incident comment.

By default this playbook first queries the Censys Host Enrichment API (`v3/global/asset/enrichment/host`) for the incident IPs, which returns the standard host record plus GreyNoise, IPinfo (network and privacy) and Mallory third-party data. The enrichment API is a separately entitled feature, so a single probe call decides whether it is available: on 403 (not entitled) or 409 every IP falls back to the standard bulk host API, and any individual IP the enrichment API cannot return falls back on its own. Transient statuses (429, 5xx) and 404 keep the enrichment path enabled without losing any IP. A 401 response terminates the run with an authentication error pointing at the Key Vault secret and Organization ID. Set the `UseHostEnrichment` parameter to `false` to always use the standard host API.

### Prerequisites

1. Deploy the CensysAddIncidentComment playbook before deploying this playbook.
2. Obtain a Censys API token and store it in Azure Key Vault as a secret named 'Censys-Access-Token'.
3. Obtain the Censys Organization ID from your Censys platform account.
4. Create or identify an Azure Key Vault and note its name and Tenant ID.
5. Ensure you have a Log Analytics Workspace configured for Microsoft Sentinel.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: CensysIncidentEnrichment).
   * Ports: Comma-separated list of ports used to build web property identifiers (default: 80,443).
   * UseHostEnrichment: Set to true (default) to use the Censys Host Enrichment API for additional GreyNoise, IPinfo and Mallory data, or false to always use the standard host API.
   * OrganizationID: Your Censys Organization ID from the Censys platform account settings.
   * IncidentEnrichmentPlaybookName: Name of the deployed CensysAddIncidentComment playbook.
   * KeyVaultName: Name of the Azure Key Vault where the Censys API token is stored.
   * TenantId: Azure AD Tenant ID where the Key Vault is located.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysIncidentEnrichment%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysIncidentEnrichment%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select Microsoft Sentinel connection resource.
2. Go to General → edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for Key Vault and Log Analytics Data Collector connections.

#### b. Add Access policy in Keyvault

Add access policy for the playbook's managed identity to read secrets from Key Vault.
1. Go to logic app → *your logic app* → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to keyvaults → *your keyvault* → Access policies → create.
3. Select Get and List permissions for Secrets. Click next.
4. In the principal section, search by copied object ID. Click next.
5. Click review + create.

#### c. Assign Microsoft Sentinel Responder role

Assign Microsoft Sentinel Responder role to the playbook's managed identity.
1. Go to Log Analytics workspace → Access control (IAM) → Add role assignment.
2. Select Microsoft Sentinel Responder role.
3. Select Managed identity and choose the playbook's identity.
4. Click Save.
