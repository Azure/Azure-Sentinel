# StealthTalk — Alert to Microsoft Teams

A Microsoft Sentinel playbook (Logic App) that posts a formatted Adaptive Card with the
incident summary into a Microsoft Teams channel whenever a Sentinel incident is created
by one of the StealthTalk anomalous-auth analytic rules.

## How it works

1. **Trigger:** `Microsoft_Sentinel_incident` (via the `azuresentinel` API connection in the
   Logic App). The trigger fires on every incident created in the workspace where the
   playbook is granted `Microsoft Sentinel Responder`.
2. **Action:** `HTTP POST` to the Teams Workflow incoming-webhook URL with an Adaptive Card
   payload (title, severity, status, createdTimeUtc, and an "Open in Sentinel" button that
   deeplinks to the incident).

The playbook fires for every incident; the SOC scopes it to StealthTalk-only by configuring
a Sentinel **Automation Rule** that runs this playbook only when the incident's analytic
rule name matches one of the four StealthTalk rules.

## Prerequisites

1. A Microsoft Teams channel with a Workflows incoming webhook already configured
   (`Workflows → Build from scratch → "When a Teams Webhook request is received" trigger →
   "Post card in a chat or channel" action`). Save and copy the workflow's webhook URL.
2. Microsoft Sentinel enabled on the destination Log Analytics workspace.

## Deployment parameters

| Parameter         | Required | Description                                                                                                                          |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `PlaybookName`    | optional | Name of the Logic App resource. Default: `StealthTalk-LogicApp-AlertToTeams`.                                                        |
| `TeamsWebhookUrl` | required | The Power Automate / Teams Workflow webhook URL captured in step 1 of Prerequisites. The URL contains an embedded HMAC signature and is treated as a secret. |

## Post-deployment configuration

After deploying via the Solution or directly via the ARM template:

1. **Grant the playbook's managed identity access to the Sentinel workspace**
   - Open the Log Analytics workspace → **Access control (IAM)** → **+ Add role assignment**.
   - Role: **Microsoft Sentinel Responder**. Assign access to: **Managed identity** → select the playbook's system-assigned identity.

2. **Allow Sentinel to start the playbook**
   - Open the Logic App's resource group → **Access control (IAM)** → **+ Add role assignment**.
   - Role: **Microsoft Sentinel Automation Contributor**. Assign access to: **Service principal** → select **Azure Security Insights**.

3. **Create an Automation Rule**
   - Microsoft Sentinel → **Automation** → **+ Create** → **Automation rule**.
   - Trigger: `When incident is created`.
   - Conditions — add **one** condition with multi-select values:
     - Property: `Analytic rule name`
     - Operator: `Equals`
     - Values: `StealthTalk - After Hours Work`, `StealthTalk - Multi New Devices Registration`, `StealthTalk - Login Outside Work Zone`, `StealthTalk - Password Brute Force`.
   - Actions: **Run playbook** → select this Logic App.

   > Important: use **one** condition with multiple values, not four separate OR-conditions — Sentinel UI evaluates multi-value conditions correctly; four OR-conditions sometimes don't trigger.

After the rule is saved, every new StealthTalk incident triggers a Teams card.

## Validating

1. Trigger any of the StealthTalk rules using the simulator scripts under
   `assets/Scripts/sim_*.py` (or via real anomalous activity in StealthTalk).
2. Wait up to ~5 minutes for Sentinel to schedule the analytic rule, create an incident,
   match the automation rule, and start the playbook.
3. Open Logic Apps → **Runs history** to see the latest run; expand the HTTP action to
   verify the response status from Teams (should be `2xx`).
4. Verify the card appeared in the target Teams channel.

If the HTTP action returns `401` or `403`, the webhook URL is invalid or expired — recreate
it in Teams Workflows and redeploy with the new URL.
