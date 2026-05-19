# Censys Host History

## Summary

This playbook is triggered manually via HTTP request, typically invoked from a Microsoft Sentinel workbook. It retrieves historical timeline data for a specified host (IP address) from the Censys API (v3) within a given time range. The playbook accepts start_time, end_time, and host parameters in RFC3339 format. NOTE: Start time must be the timestamp closest to the current time (more recent) and End time must be the timestamp furthest from the current time (older). The playbook validates input parameters to ensure times are not in the future and start_time is not greater than end_time. It retrieves the Censys API token securely from Azure Key Vault, then queries the Censys host timeline endpoint with pagination support (up to 10 pages). The playbook processes various event types including service_scanned, endpoint_scanned, location_updated, route_updated, and whois_updated events. Each event is enriched with UI links to the Censys platform for detailed investigation. The collected history data is ingested into Azure Log Analytics (Censys_Host_History_Data table) for analysis and reporting. Comprehensive error handling is implemented for HTTP status codes (200, 401, 403, 404, 422).

### Prerequisites

1. Create an Azure Key Vault and store your Censys API token as a secret named 'Censys-Access-Token'.
2. Obtain your Censys Organization ID from the Censys platform account settings.
3. Deploy the Censys Host History workbook to invoke this playbook.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here (default: CensysHostHistory).
   * OrganizationID: Your Censys Organization ID from the Censys platform account settings.
   * KeyVaultName: Name of the Azure Key Vault where the Censys API token is stored.
   * TenantId: Azure AD Tenant ID where the Key Vault is located.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysHostHistory%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCensys%2FPlaybooks%2FCensysHostHistory%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for Log Analytics Data Collector connection.

#### b. Add Access policy in Key Vault

Grant the playbook's managed identity 'Key Vault Secrets User' role on the Azure Key Vault.
1. Go to Logic App → *your Logic App* → Identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to Key Vaults → *your Key Vault* → Access policies → Create.
3. Select Get and List permissions for Secrets. Click Next.
4. In the principal section, search by copied Object ID. Click Next.
5. Click Review + Create.

#### c. Configure the Censys Host History workbook

Configure the Censys Host History workbook with this playbook's HTTP trigger URL.
1. Go to Logic App → *your Logic App* → Logic app designer.
2. Copy the HTTP POST URL from the trigger.
3. Configure the Censys Host History workbook to use this URL.

#### d. Ensure Log Analytics workspace configuration

Ensure the Log Analytics workspace is configured to receive custom logs.
