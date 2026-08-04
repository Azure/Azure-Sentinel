# Check Point Exposure Management - Fetch Attachments On-Demand

## Summary

On-demand playbook that fetches alert attachments and analysis report for a Sentinel incident. Analysts trigger this manually from the incident Actions menu to retrieve supporting evidence and analysis from Argos.

**Flow:**
1. Calls **Check_Point_EM_Base** to retrieve API credentials.
2. Extracts alert reference IDs from the incident.
3. For each alert, fetches the full alert details including attachments list.
4. Downloads each attachment and records metadata (name, type, fetch status).
5. Fetches the analysis report for the alert.
6. Adds a comment with attachment metadata and analysis report content.
7. Tags the incident `argos-attachments-fetched`.

## Prerequisites

1. **Check_Point_EM_Base** playbook must be deployed in the same resource group.
2. A valid Check Point Exposure Management API token configured in the Check_Point_EM_Base Key Vault.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2520Cyberint%2520Alerts%2FPlaybooks%2FCheck_Point_EM_FetchAttachments%2Fazuredeploy.json)

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| **PlaybookName** | No | Name of the Logic App (default: `Check_Point_EM_FetchAttachments`) |
| **Check_Point_EM_Base_PlaybookName** | No | Name of the base playbook (default: `Check_Point_EM_Base`) |

## Post-Deployment

1. Grant the Logic App Managed Identity the **Microsoft Sentinel Responder** role on the resource group.
2. Analysts can run this playbook from the Sentinel incident **Actions > Run playbook** menu.

## Notes

- **v1**: Attachment metadata and analysis report content are added as incident comments. Actual file storage (e.g., Blob Storage) is planned for v2.
- The playbook handles 302 redirects automatically (Logic App HTTP action follows redirects by default).
- If individual attachments fail to download, the playbook continues with remaining attachments and reports per-item status.

## API Endpoints Used

| Action | Endpoint |
|--------|----------|
| Get alert details | `GET /api/v1/alerts/{alert_ref_id}` |
| Get attachment | `GET /api/v1/alerts/{alert_ref_id}/attachments/{attachment_id}` |
| Get analysis report | `GET /api/v1/alerts/{alert_ref_id}/analysis_report` |
