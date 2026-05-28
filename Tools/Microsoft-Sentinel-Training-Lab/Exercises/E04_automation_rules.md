# Exercise 4 — Automation Rules

**Topic:** Create automation rules to enrich incidents with tags and manage SOC workflow  
**Difficulty:** Beginner  
**Prerequisites:** None

---

## Objective

Create a **Microsoft Sentinel automation rule** that automatically adds tags and adjusts severity when a specific alert fires with a specific entity. This exercise demonstrates how automation rules streamline SOC triage without requiring a full playbook (Logic App).

### Background

Automation rules in Microsoft Sentinel run automatically when incidents are created or updated. They allow you to:

- **Add tags** to incidents (e.g., "phishing", "credential-access", "high-priority")
- **Change severity** or status
- **Assign incidents** to a specific owner
- **Run playbooks** (Logic Apps) for advanced response
- **Suppress** noisy or false-positive incidents

Unlike playbooks, automation rules require **no code** — they are configured entirely through the portal UI. They execute in order of priority (lower number = higher priority) and can be chained.

> **Reference:** [Create and use Microsoft Sentinel automation rules to manage response](https://learn.microsoft.com/en-us/azure/sentinel/create-manage-use-automation-rules)

---

### Steps

#### Step 1 — Review Existing Incidents

Before creating automation, let's identify an alert we want to enrich. Navigate to **Microsoft Sentinel** → **Threat management** → **Incidents**.

Look for incidents created by the lab's detection rules. You should see incidents from rules like:

- `Lab Stage 3.5 - Internal port scan detected (Palo Alto)`
- `Lab Stage 6 - Large data exfiltration to external IP (Palo Alto)`
- `Lab Stage 4 - Account Takeover Chain (Okta)`

![Sentinel incidents list](../Images/OnboardingImage29.png?raw=true)

For this exercise, we will create automation rules targeting two scenarios:

1. **AWS suspicious activity** — tag with "cloud-threat" and "aws"
2. **Security event log cleared** — escalate severity to Critical and tag with "defense-evasion"

> **Note:** The lab deploys both **custom detection rules** (via the Graph API) and **Sentinel analytics rules**. Automation rules with the "Analytic rule name" condition work with analytics rules. The analytics rules deployed by the lab include: `AWS Config Service Resource Deletion Attempts`, `Suspicious AWS CLI Command Execution`, `NRT Security Event log cleared`, and `Scheduled Task Hide`.

#### Step 2 — Create Automation Rule: Tag AWS Threats

1. Navigate to **Microsoft Sentinel** → **Configuration** → **Automation**
2. Click **+ Create** → **Automation rule**

   ![Automation rule creation dialog](../Images/OnboardingImage30.png?raw=true)

3. Fill in the rule details:

   | Field | Value |
   | --- | --- |
   | **Name** | `Tag AWS threat incidents` |
   | **Rule type** | Standard rule |
   | **Trigger** | When incident is created |
   | **Conditions** | |

4. Under **Conditions**, configure:

   - Click **+ Add condition** → **Analytic rule name**
   - Select **Contains** → enter `AWS`

   This matches any incident created by an analytics rule whose name contains "AWS" — covering both `AWS Config Service Resource Deletion Attempts` and `Suspicious AWS CLI Command Execution`.

5. Under **Actions**, add two actions:

   **Action 1:**
   - Select **Add tags**
   - Enter tag: `cloud-threat`

   **Action 2:**
   - Select **Add tags**
   - Enter tag: `aws`

6. Leave **Order** as the default (e.g., `1`)
7. Set **Status** to **Enabled**
8. Click **Apply**

#### Step 3 — Create Automation Rule: Escalate Log Cleared Events

Create a second automation rule for the security event log cleared scenario:

1. Click **+ Create** → **Automation rule**
2. Fill in the details:

   | Field | Value |
   | --- | --- |
   | **Name** | `Escalate log cleared events` |
   | **Rule type** | Standard rule |
   | **Trigger** | When incident is created |

3. Under **Conditions**, configure:

   - **Analytic rule name** → **Contains** → `Security Event log cleared`

4. Under **Actions**, add three actions:

   **Action 1:**
   - Select **Add tags**
   - Enter tag: `defense-evasion`

   **Action 2:**
   - Select **Add tags**
   - Enter tag: `log-tampering`

   **Action 3:**
   - Select **Change severity**
   - Set to: **Critical**

5. Set **Order** to `2` (runs after the port scan rule)
6. Set **Status** to **Enabled**
7. Click **Apply**

#### Step 4 — Understand Rule Ordering and Conditions

Automation rules execute in **priority order** (lowest number first). If multiple rules match the same incident, they all execute sequentially.

Review the automation rules list:

| Order | Name | Trigger | Conditions | Actions |
| --- | --- | --- | --- | --- |
| 1 | Tag AWS threat incidents | Incident created | Analytic rule name contains "AWS" | Add tags: cloud-threat, aws |
| 2 | Escalate log cleared events | Incident created | Analytic rule name contains "Security Event log cleared" | Add tags: defense-evasion, log-tampering; Change severity → Critical |

> **Key insight:** Conditions can use **AND** logic (all conditions must match) or **OR** logic (any condition matches). The default is **AND**. For the Okta rule, both the rule name _and_ the entity condition must be true.

#### Step 5 — Verify the Automation Rules

To verify the rules work:

1. Navigate to **Microsoft Sentinel** → **Threat management** → **Incidents**
2. Find a port scan or Okta account takeover incident
3. Check whether the incident has the expected **tags** and **severity**

If no new incidents have been created since you set up the rules, you can trigger them by running the detection rules manually:

1. Go to **Hunting** → **Custom detection rules**
2. Find the `Lab Stage 3.5 - Internal Port Scan Detected (Palo Alto)` rule
3. Click **Run** to generate a new incident

Then check the incident — it should have the tags `reconnaissance` and `network` applied automatically.

![Incident with auto-applied tags](../Images/OnboardingImage31.png?raw=true)

#### Step 6 — Explore Additional Automation Options

Automation rules support more advanced scenarios that you can explore:

| Action | Use case |
| --- | --- |
| **Assign owner** | Route phishing incidents to the email security team |
| **Change status** | Auto-close known false positives |
| **Run playbook** | Trigger a Logic App to send a Teams notification, block an IP, or isolate a device |
| **Add task** | Create an investigation checklist for the assigned analyst |

To explore playbook integration:

1. On the Automation page, click **+ Create** → **Playbook with incident trigger**
2. This opens the Logic App designer — a topic for a more advanced exercise

> **Tip:** For this lab, stick to tag-based automation. Playbook-based response (e.g., device isolation, user suspension) requires additional Azure resources and permissions.

---

### Key Takeaways

- **Automation rules** provide no-code SOC workflow automation — tags, severity changes, assignments, and playbook triggers
- Rules execute in **priority order** and can be chained for layered logic
- **Conditions** can match on analytics rule name, entity attributes, incident properties, and more
- **Tags** are a lightweight way to categorise incidents for filtering, dashboards, and reporting
- Automation rules are best for **triage automation** — reducing manual work for repetitive SOC tasks
- For complex response actions (isolate device, block IP), use **playbooks** triggered by automation rules

### Microsoft Learn References

- [Create and use automation rules to manage response](https://learn.microsoft.com/en-us/azure/sentinel/create-manage-use-automation-rules)
- [Automation rules reference](https://learn.microsoft.com/en-us/azure/sentinel/automation-rules-reference)
- [Automate incident handling in Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/automate-incident-handling-with-automation-rules)
- [Tutorial: Use playbooks with automation rules](https://learn.microsoft.com/en-us/azure/sentinel/tutorial-respond-threats-playbook)

---

## Next Steps

Continue to **[Exercise 5 — Cross-Platform Response Actions](./E05_device_isolation_response.md)** (optional, requires MDE) or skip to **[Exercise 6 — Port Scan Detection & Threshold Tuning](./E06_port_scan_threshold_tuning.md)**
