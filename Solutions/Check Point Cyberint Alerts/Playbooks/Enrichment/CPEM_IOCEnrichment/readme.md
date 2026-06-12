# Check Point Exposure Management - IOC Enrichment and Triage

## Summary

When a new Microsoft Sentinel incident is created, this playbook automatically enriches IOC entities (IPs, domains, file hashes, URLs) using the Check Point Exposure Management threat intelligence API and adds the enrichment results as an incident comment.

**Flow:**
1. Extracts IP, FileHash, DNS, and URL entities from the Sentinel incident.
2. Calls **Check_Point_EM_Base** to retrieve API credentials.
3. For each entity, queries the appropriate Check Point Exposure Management IOC enrichment endpoint.
4. Appends enrichment details (verdict, confidence, malware family, actor attribution) as an incident comment.

## Prerequisites

1. **Check_Point_EM_Base** playbook must be deployed in the same resource group.
2. A valid Check Point Exposure Management API token configured in the Check_Point_EM_Base Key Vault.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_IOCEnrichment%2Fazuredeploy.json)

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| **PlaybookName** | No | Name of the Logic App (default: `Check_Point_EM_IOCEnrichment`) |
| **Check_Point_EM_Base_PlaybookName** | No | Name of the base playbook (default: `Check_Point_EM_Base`) |

## Post-Deployment

1. Grant the Logic App Managed Identity the **Microsoft Sentinel Responder** role on the resource group.
2. Configure an automation rule in Microsoft Sentinel to trigger this playbook on incident creation.

## API Endpoints Used

| Entity Type | Endpoint |
|-------------|----------|
| IPv4 | `GET /api/v1/file/ipv4/{ip}` |
| SHA256 Hash | `GET /api/v1/file/sha256/{hash}` |
| Domain | `GET /api/v1/file/domain/{domain}` |
| URL | `GET /api/v1/file/url?value={url}` |
