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

## Post-Deployment Steps

### 1. Assign Microsoft Sentinel Responder to the Logic App's managed identity

This allows the playbook to interact with Sentinel incidents (add comments, close incidents).

1. In the Azure Portal, go to your **Resource Group** containing the Sentinel workspace.
2. Go to **Access control (IAM)** → **Add role assignment**.
3. Role: **Microsoft Sentinel Responder**.
4. Members: select **Managed identity** → pick the Logic App (`Darktrace-ReleaseHeldEmail`).
5. Save.

### 2. Assign Microsoft Sentinel Automation Contributor

This allows Sentinel automation rules to trigger the playbook.

1. In the Azure Portal, go to the **Logic App** resource (`Darktrace-ReleaseHeldEmail`).
2. Go to **Access control (IAM)** → **Add role assignment**.
3. Role: **Microsoft Sentinel Automation Contributor**.
4. Members: select **User, group, or service principal** → search for **Microsoft Sentinel** (or **Azure Security Insights**).
5. Save.

### 3. Attach the playbook to incidents

Attach this playbook to incidents created by the **DarktraceEmailHeldForRelease** analytic rule. You can run it manually via "Run playbook" on an incident, or create an automation rule to trigger it automatically.

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
