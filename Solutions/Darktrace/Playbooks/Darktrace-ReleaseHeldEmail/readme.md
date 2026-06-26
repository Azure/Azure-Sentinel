# Darktrace - Release Held Email

## Summary

This playbook releases an email held by Darktrace /Email directly from a Microsoft Sentinel incident. When a SOC analyst triggers the playbook on a held-email incident, it extracts the email UUID and recipients from the alert custom details, authenticates to the Darktrace API, and calls the release endpoint. On success it posts a confirmation comment and optionally closes the incident.

## Prerequisites

- A Darktrace ActiveAI Platform instance with API access enabled.
- OAuth2 client credentials (Client ID and Client Secret) provisioned in Darktrace with permissions to release held emails.
- Your Darktrace instance ID.
- The Microsoft Sentinel incident must have been created by the **DarktraceEmailHeldForRelease** analytic rule (which maps `emailUuid` and `recipients` as custom details).

## Deployment

1. Click **Deploy to Azure** or deploy `azuredeploy.json` via the Azure Portal / CLI.
2. Provide the required parameters:
   - **PlaybookName**: Name for the Logic App (default: `Darktrace-ReleaseHeldEmail`)
   - **DarktraceInstanceId**: Your Darktrace instance ID
   - **DarktraceClientId**: OAuth2 Client ID
   - **DarktraceClientSecret**: OAuth2 Client Secret
   - **CloseIncidentOnRelease**: Set to `true` to automatically close the incident after a successful release (default: `false`)
3. After deployment, grant the Logic App's managed identity the **Microsoft Sentinel Responder** role on the resource group containing your Sentinel workspace.
4. Attach this playbook to incidents created by the DarktraceEmailHeldForRelease analytic rule (manually run via "Run playbook" on an incident).

## How It Works

1. The playbook triggers when an analyst clicks "Run playbook" on a held-email incident.
2. It fetches the alerts associated with the incident.
3. For each alert, it extracts `emailUuid` and `recipients` from the alert's custom details.
4. It authenticates to Darktrace using the OAuth2 client credentials flow.
5. It calls `POST /products/{instanceId}/agemail/api/v1.0/emails/{emailUuid}/action` with body `{"action": "release", "recipients": [...]}`.
6. On success: posts a comment "Email released successfully at {timestamp}" and, if `CloseIncidentOnRelease` is true, closes the incident with BenignPositive classification.
7. On failure: posts an error comment with status code and response body, then terminates the run as Failed.

## Authentication

The playbook uses OAuth2 client credentials to authenticate with Darktrace. A fresh token is obtained on each run — no manual token rotation required.

- **Token endpoint**: `https://auth.activeai.darktrace.com/oauth/token`
- **API base**: `https://api.darktrace.com/products/{instanceId}/`
