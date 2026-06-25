# Darktrace - Comment On Model Alert

## Summary

This playbook syncs comments from Microsoft Sentinel incidents back to the corresponding Darktrace Model Alert. When triggered by an incident update, it retrieves the latest comment from the Sentinel incident and posts it to the associated model breach in Darktrace via the Darktrace API.

## Prerequisites

- A Darktrace ActiveAI Platform instance with API access enabled.
- OAuth2 client credentials (Client ID and Client Secret) provisioned in Darktrace with permissions to post comments on model alerts.
- Your Darktrace instance ID.
- The Microsoft Sentinel incident must have been created by the **Darktrace Model Alert** analytic rule (which maps the `threatId` field as a custom detail — this is the policy breach ID used by the Darktrace API).

## Deployment

1. Click **Deploy to Azure** or deploy `azuredeploy.json` via the Azure Portal / CLI.
2. Provide the required parameters:
   - **PlaybookName**: Name for the Logic App (default: `Darktrace-CommentOnModelAlert`)
   - **DarktraceInstanceId**: Your Darktrace instance ID
   - **DarktraceClientId**: OAuth2 Client ID
   - **DarktraceClientSecret**: OAuth2 Client Secret
3. After deployment, grant the Logic App's managed identity the **Microsoft Sentinel Responder** role on the resource group containing your Sentinel workspace.
4. Create an **Automation Rule** in Microsoft Sentinel:
   - Trigger: When incident is updated
   - Action: Run playbook → select this playbook

## How It Works

1. The playbook triggers when a Sentinel incident is updated.
2. It fetches the latest comment on the incident.
3. If a comment exists, it retrieves the alerts associated with the incident.
4. For each alert, it extracts the Darktrace policy breach ID (`threatId`) from the alert's custom details.
5. It authenticates to Darktrace using the OAuth2 client credentials flow (`https://auth.activeai.darktrace.com/oauth/token`).
6. It posts the comment to the Darktrace Model Alert via `POST https://api.darktrace.com/products/{instanceId}/modelbreaches/{pbid}/comments`.

## Authentication

The playbook uses OAuth2 client credentials to authenticate with Darktrace. A fresh token is obtained on each run — no manual token rotation required.

- **Token endpoint**: `https://auth.activeai.darktrace.com/oauth/token`
- **API base**: `https://api.darktrace.com/products/{instanceId}/`
