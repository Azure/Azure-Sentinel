# StealthTalk - Alert to Microsoft Teams

A Microsoft Sentinel playbook (Logic App) that posts a formatted Adaptive Card with the
incident summary into a Microsoft Teams channel whenever a Microsoft Sentinel incident is created
by one of the StealthTalk anomalous-auth analytic rules.

## How it works

1. **Trigger:** `Microsoft_Sentinel_incident` (via the `azuresentinel` API connection in the
 Logic App). The trigger fires on every incident created in the workspace where the
 playbook is granted `Microsoft Sentinel Responder`.
2. **Action:** `HTTP POST` to the Teams Workflow incoming-webhook URL with an Adaptive Card
 payload (title, severity, status, createdTimeUtc, and an "Open in Microsoft Sentinel" button that
 deeplinks to the incident).

The playbook fires for every incident; the SOC scopes it to StealthTalk-only by configuring
a Microsoft Microsoft Sentinel **Automation Rule** that runs this playbook only when the incident's analytic
rule name matches one of the four StealthTalk rules.

## Prerequisites

1. A Microsoft Teams channel with a Workflows incoming webhook already configured
 (`Workflows -> Build from scratch -> "When a Teams Webhook request is received" trigger ->
 "Post card in a chat or channel" action`). Save and copy the workflow's webhook URL.
2. Microsoft Sentinel enabled on the destination Log Analytics workspace.

## Deployment parameters

| Parameter | Required | Description |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `PlaybookName` | optional | Name of the Logic App resource. Default: `StealthTalk-LogicApp-AlertToTeams`. |
| `TeamsWebhookUrl` | required | The Power Automate / Teams Workflow webhook URL captured in step 1 of Prerequisites. The URL contains an embedded HMAC signature and is treated as a secret. |

## Post-deployment configuration

After deploying via the Solution or directly via the ARM template:

1. **Grant the playbook's managed identity access to the Microsoft Sentinel workspace**
 - Open the Log Analytics workspace -> **Access control (IAM)** -> **+ Add role assignment**.
 - Role: **Microsoft Sentinel Responder**. Assign access to: **Managed identity** -> select the playbook's system-assigned identity.

2. **Allow Microsoft Sentinel to start the playbook**
 - Open the Logic App's resource group -> **Access control (IAM)** -> **+ Add role assignment**.
 - Role: **Microsoft Sentinel Automation Contributor**. Assign access to: **Service principal** -> select **Azure Security Insights**.

3. **Create an Automation Rule**
 - Microsoft Sentinel -> **Automation** -> **+ Create** -> **Automation rule**.
 - Trigger: `When incident is created`.
 - Conditions - add **one** condition with multi-select values:
 - Property: `Analytic rule name`
 - Operator: `Equals`
 - Values: `StealthTalk - After Hours Work`, `StealthTalk - Multi New Devices Registration`, `StealthTalk - Login Outside Work Zone`, `StealthTalk - Password Brute Force`.
 - Actions: **Run playbook** -> select this Logic App.

 > Important: use **one** condition with multiple values, not four separate OR-conditions - Microsoft Sentinel UI evaluates multi-value conditions correctly; four OR-conditions sometimes don't trigger.

After the rule is saved, every new StealthTalk incident triggers a Teams card.

## Validating

1. Trigger any of the StealthTalk rules using the simulator scripts under
 `assets/Scripts/sim_*.py` (or via real anomalous activity in StealthTalk).
2. Wait up to ~5 minutes for Microsoft Sentinel to schedule the analytic rule, create an incident,
 match the automation rule, and start the playbook.
3. Open Logic Apps -> **Runs history** to see the latest run; expand the HTTP action to
 verify the response status from Teams (should be `2xx`).
4. Verify the card appeared in the target Teams channel.

## Troubleshooting

| Symptom | Likely cause | Resolution |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HTTP action returns `401 Unauthorized` | The Teams Workflows webhook URL signature is invalid or the webhook was deleted/recreated. | Recreate the webhook in Teams (`Workflows -> "When a Teams Webhook request is received" -> "Post card"`) and redeploy the playbook with the new `TeamsWebhookUrl` parameter. |
| HTTP action returns `403 Forbidden` | The webhook URL was tampered with or its embedded HMAC signature was stripped (e.g., the URL was copied through a system that trims query strings). | Copy the webhook URL again from Teams **as a single string** without truncation, then redeploy the playbook. |
| `Microsoft_Sentinel_incident` trigger fires but the playbook fails to start | The Logic App's system-assigned managed identity is missing the **Microsoft Sentinel Responder** role on the workspace. | In the Log Analytics workspace -> **Access control (IAM)** -> assign **Microsoft Sentinel Responder** to the playbook's managed identity. |
| Automation Rule UI shows the playbook in the dropdown but cannot save it | The **Azure Security Insights** service principal does not have **Microsoft Sentinel Automation Contributor** on the Logic App's resource group. | In the Logic App's resource group -> **Access control (IAM)** -> assign **Microsoft Sentinel Automation Contributor** to the **Azure Security Insights** service principal. |
| New StealthTalk incidents created in Microsoft Sentinel, but no Teams card posted | Automation Rule conditions are not matching the incident's `Analytic rule name`. | Verify the Automation Rule uses **one** condition with **multiple values** (not four separate OR-conditions). Re-check that the analytic rule names match exactly (case-sensitive). |
| Adaptive Card appears in Teams but fields like `Title` or `Severity` are empty | The Microsoft Sentinel incident payload schema changed, or the trigger body lacks the expected `object.properties` path. | Open the Logic App run history -> expand the `HTTP` action -> inspect the `triggerBody()?['object']?['properties']` content. Update the Adaptive Card field bindings if the schema differs. |
| Card posts but the **Open in Microsoft Sentinel** button URL is wrong | The trigger payload does not contain `incidentUrl` (older Microsoft Sentinel API versions), or the resource group/subscription is missing from the workspace URL. | Replace the `incidentUrl` binding in the Adaptive Card action with a manually constructed URL: `https://portal.azure.com/#@<tenant>/blade/Microsoft_Azure_Security_Insights/IncidentBlade/incidentName/<incidentName>`. |
