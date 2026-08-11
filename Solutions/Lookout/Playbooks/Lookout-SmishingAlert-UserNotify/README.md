# Lookout-SmishingAlert-UserNotify

## Overview

This playbook triggers automatically when Microsoft Sentinel creates an incident from the **Lookout - Critical Smishing and Phishing Alerts (v2)** analytic rule. Speed is critical for smishing — the device owner must be warned before they act on the malicious message. The playbook performs three automated actions:

1. **SOC Notification** — Posts an urgent Teams message to the SOC channel with full phishing context: alert type, threat category, impersonation risk, campaign indicators, risk score, and a direct link to the Sentinel incident.
2. **User Warning Email** — Sends an urgent HTML email to the targeted device owner instructing them not to click suspicious links, not to enter credentials on sites reached via SMS, to forward suspicious messages to IT Security, and to contact IT immediately if they have already clicked a link.
3. **Incident Enrichment** — Adds a structured comment with attack intelligence, campaign context, and recommended next steps including credential reset procedures if a link was clicked.

## Analytic Rules Supported

| Rule | Severity |
|---|---|
| Lookout - Critical Smishing and Phishing Alerts (v2) | High |

## Prerequisites

1. A Microsoft Teams team and channel configured for SOC security alerts.
2. A Microsoft 365 / Office 365 account authorized to send email.
3. The playbook managed identity must be granted the **Microsoft Sentinel Responder** role on the Log Analytics workspace.

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FLookout%2FPlaybooks%2FLookout-SmishingAlert-UserNotify%2Fazuredeploy.json)

### Deployment Parameters

| Parameter | Required | Description |
|---|---|---|
| PlaybookName | No | Name of the Logic App (default: `Lookout-SmishingAlert-UserNotify`) |
| TeamsGroupId | Yes | Microsoft Teams Group (Team) ID for SOC notifications |
| TeamsChannelId | Yes | Microsoft Teams Channel ID for SOC notifications |

**Finding your Teams IDs:** In Microsoft Teams, right-click the channel → **Get link to channel**. The URL contains both `groupId` and the channel ID.

## Post-Deployment Configuration

### Step 1 — Authorize API Connections

After deployment, navigate to the resource group in the Azure portal and authorize the API connections:

1. Open the **teams-Lookout-SmishingAlert-UserNotify** connection → **Edit API connection** → **Authorize** → **Save**.
2. Open the **office365-Lookout-SmishingAlert-UserNotify** connection → **Edit API connection** → **Authorize** → **Save**.

### Step 2 — Assign Sentinel Responder Role

1. Navigate to your **Microsoft Sentinel** workspace → **Settings** → **Workspace settings**.
2. Select **Access control (IAM)** → **Add role assignment**.
3. Role: **Microsoft Sentinel Responder**.
4. Assign to: the Logic App's managed identity (`Lookout-SmishingAlert-UserNotify`).

### Step 3 — Create Automation Rule

1. In **Microsoft Sentinel**, go to **Automation** → **+ Create** → **Automation rule**.
2. Configure:
   - **Trigger**: When incident is created
   - **Conditions**: Analytics rule name — Contains — `Lookout - Critical Smishing and Phishing`
   - **Actions**: Run playbook → `Lookout-SmishingAlert-UserNotify`
3. Save the automation rule.

## Permissions Summary

| Connection | Auth Method | Permission Required |
|---|---|---|
| Microsoft Sentinel | Managed Identity | Microsoft Sentinel Responder |
| Microsoft Teams | User Account | Channel Post Messages |
| Office 365 | User Account | Send Email |
