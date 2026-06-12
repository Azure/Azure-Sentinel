# Check Point Exposure Management - Credential Leak Validation and Response

## Summary

When a new Microsoft Sentinel incident is created for leaked credentials, this playbook queries the Check Point Exposure Management credential leak API for the affected company domain, enriches the incident with exposed credential details, and escalates severity when the leak volume is high.

**Flow:**
1. Calls **Check_Point_EM_Base** to retrieve API credentials.
2. Extracts account entities from the Sentinel incident.
3. Queries `POST /by_domain/` for leaked credentials matching the configured company domain.
4. Adds a comment listing each exposed credential (email, source, last seen).
5. If more than 10 credentials are found, escalates incident severity to **High**.

## Prerequisites

1. **Check_Point_EM_Base** playbook must be deployed in the same resource group.
2. A valid Check Point Exposure Management API token configured in the Check_Point_EM_Base Key Vault.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_CredentialLeakResponse%2Fazuredeploy.json)

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| **PlaybookName** | No | Name of the Logic App (default: `Check_Point_EM_CredentialLeakResponse`) |
| **Check_Point_EM_Base_PlaybookName** | No | Name of the base playbook (default: `Check_Point_EM_Base`) |
| **CompanyDomain** | Yes | Primary company domain to check for leaked credentials (e.g., `example.com`) |

## Post-Deployment

1. Grant the Logic App Managed Identity the **Microsoft Sentinel Responder** role on the resource group.
2. Configure an automation rule in Microsoft Sentinel to trigger this playbook on credential leak incidents.
3. Optionally integrate with your Identity Provider (Entra ID, Okta) to automate password resets for exposed accounts.

## API Endpoints Used

| Action | Endpoint |
|--------|----------|
| Query leaked credentials | `POST /by_domain/` |
