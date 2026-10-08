# Google Threat Intelligence - Session Assistant

## Summary

This playbook lets analysts ask Google Threat Intelligence (GTI) questions directly from a Microsoft Sentinel incident. When an analyst adds an incident comment that starts with `#ask-gti:`, the playbook sends the question and the incident context to the GTI Agentspace Session API and posts the answer back to the incident. Follow-up questions on the same incident continue the same multi-turn GTI session, tracked with the `GTI-Session` and `GTI-LastProcessed` incident tags.

The full answer is saved as an HTML page in a private Azure Blob Storage container and shared as a time-limited, read-only SAS link in the incident comment. If saving or linking fails, the answer is posted inline instead.

### Prerequisites

1. Obtain the Key Vault name and secret name where the GTI (VirusTotal) API key is stored. The Key Vault permission model must be **Azure role-based access control**.
2. Obtain the Storage Account name where answer pages are saved. The blob container is created automatically on first use. 
3. Obtain the Storage Account access key (key1 or key2). It is required only to generate the time-limited SAS link, which does not support managed identity. Provide it as a Key Vault reference in your parameters file where possible.
4. A Log Analytics workspace with Microsoft Sentinel enabled.

### Deployment Instructions

1. Click the Deploy to Azure button to launch the ARM template deployment wizard.
2. Fill in the parameters:
   * PlaybookName: Name of the Logic App (default: GTISessionAssistant).
   * KeyVaultName / KeyVaultSecretName: Key Vault and secret that hold the GTI API key.
   * StorageAccountName / StorageAccountKey: Storage Account that holds the answer pages and its access key.
   * ContainerName: Blob container for answer pages (optional, a default is used when empty).
   * SASExpiryDays: Number of days the answer link stays valid.
   * BlobRetentionDays: Optional. Days after which answer pages are deleted by a lifecycle rule (see post-deployment step d).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTISessionAssistant%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovernbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGoogle%2520Threat%2520Intelligence%2FPlaybooks%2FGTISessionAssistant%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Assign roles to the playbook's managed identity

| Role | Scope |
|------|-------|
| Key Vault Secrets User | The Key Vault |
| Storage Blob Data Contributor | The Storage Account |
| Microsoft Sentinel Responder | The Sentinel workspace |

For each: open the resource, go to Access control (IAM), Add role assignment, select the role, choose User, group, or service principal, select the playbook by name, then Review + assign.

#### b. Create an automation rule

1. In Microsoft Sentinel, go to Automation, Create, Automation rule.
2. Trigger: **When incident is updated**.
3. Condition: Updated field - Comments - Added.
4. Action: Run playbook, and select **Google Threat Intelligence - Session Assistant**.
5. Enable the rule and click Apply.

#### c. Verify API connections

The `azuresentinel`, `keyvault` and `azureblob` connections use the playbook's managed identity; `azureblobkey` uses the supplied storage key. If a connection shows as unauthorized, open it, click Edit API connection, Save, and re-check the role assignments.

#### d. Optional: automatic cleanup of answer pages

Set the `BlobRetentionDays` parameter (greater than or equal to `SASExpiryDays`) to create a lifecycle rule that deletes answer pages after that many days. A Storage Account has a single lifecycle policy, so this replaces any existing policy; leave it empty to keep answer pages indefinitely and add a rule manually if the account already has lifecycle rules.

### Usage & Triggering

The playbook triggers automatically through the automation rule whenever a comment is added to an incident.

1. Open an incident and add a comment in the form `#ask-gti: <your question>`.
2. The answer is posted back as an incident comment, with a link to the full answer page.
3. Add another `#ask-gti:` comment on the same incident to ask a follow-up in the same GTI session.

Comments that do not start with `#ask-gti:` are ignored.

Security notes: the answer link is a bearer token, so anyone with the URL can view the page until it expires.

### Troubleshooting

| Symptom | Cause and fix |
|---------|---------------|
| Run fails at the Key Vault step | The managed identity lacks Key Vault Secrets User, or the Key Vault does not use the Azure RBAC permission model. |
| Answer is posted inline with no link | Blob upload or SAS creation failed. Check Storage Blob Data Contributor, the storage key, and storage firewall settings. |
| Sentinel connection errors | Check Microsoft Sentinel Responder on the workspace and re-save the `azuresentinel` API connection. |
| GTI error comment on the incident | Usually transient. Post the question again with the `#ask-gti:` prefix. Verify the GTI API key in Key Vault if it persists. |
| Playbook does not run | Confirm the automation rule is enabled and targets this playbook. Run history is under Logic App, Overview, Runs history. |
