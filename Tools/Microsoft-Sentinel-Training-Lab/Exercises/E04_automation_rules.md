# Exercise 4 — Automation Rules

**Topic:** Create automation rules to enrich incidents with tags and manage SOC workflow
**Difficulty:** Beginner

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

- `Lab Stage 3.5 - Internal port scan detected via Palo Alto`
- `Lab Stage 6 - Large data exfiltration to external IP`
- `Lab [S4] [Okta] Account Takeover Chain`

![Sentinel incidents list](../Images/OnboardingImage29.png?raw=true)

For this exercise, we will create automation rules targeting two scenarios:

1. **Port scan alerts** — tag with "reconnaissance" and "network"
2. **Okta account takeover alerts** — tag with "identity-compromise" and escalate severity to Critical

#### Step 2 — Create Automation Rule: Tag Port Scan Incidents

1. Navigate to **Microsoft Sentinel** → **Configuration** → **Automation**
2. Click **+ Create** → **Automation rule**

   ![Automation rule creation dialog](../Images/OnboardingImage30.png?raw=true)

3. Fill in the rule details:

   | Field | Value |
   | --- | --- |
   | **Name** | `Tag port scan incidents` |
   | **Trigger** | When incident is created |
   | **Conditions** | |

4. Under **Conditions**, configure:

   - Click **+ Add condition** → **Analytics rule name**
   - Select **Contains** → enter `port scan`

   This matches any incident created by a rule whose name contains "port scan" — covering both `Lab Stage 3.5 Internal Port Scan Detected` and `Lab [E2] Port Scan Detection`.

5. Under **Actions**, add two actions:

   **Action 1:**
   - Select **Add tags**
   - Enter tag: `reconnaissance`

   **Action 2:**
   - Select **Add tags**
   - Enter tag: `network`

6. Leave **Order** as the default (e.g., `1`)
7. Set **Status** to **Enabled**
8. Click **Apply**

#### Step 3 — Create Automation Rule: Escalate Okta Account Takeover

Create a second automation rule for the Okta account takeover scenario:

1. Click **+ Create** → **Automation rule**
2. Fill in the details:

   | Field | Value |
   | --- | --- |
   | **Name** | `Escalate Okta account takeover` |
   | **Trigger** | When incident is created |

3. Under **Conditions**, add two conditions:

   **Condition 1:**
   - **Analytics rule name** → **Contains** → `Account Takeover`

   **Condition 2:** (click **+ Add condition**)
   - **Entity** → **Account** → **Name** → **Contains** → `attacker`

   > **Note:** The value `attacker` matches the `ActorUsername` from the Okta telemetry data. In a real environment, you would use a more targeted condition like a specific user or domain.

4. Under **Actions**, add three actions:

   **Action 1:**
   - Select **Add tags**
   - Enter tag: `identity-compromise`

   **Action 2:**
   - Select **Add tags**
   - Enter tag: `okta`

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
| 1 | Tag port scan incidents | Incident created | Rule name contains "port scan" | Add tags: reconnaissance, network |
| 2 | Escalate Okta account takeover | Incident created | Rule name contains "Account Takeover" AND entity Account contains "attacker" | Add tags: identity-compromise, okta; Change severity → Critical |

> **Key insight:** Conditions can use **AND** logic (all conditions must match) or **OR** logic (any condition matches). The default is **AND**. For the Okta rule, both the rule name _and_ the entity condition must be true.

#### Step 5 — Verify the Automation Rules

To verify the rules work:

1. Navigate to **Microsoft Sentinel** → **Threat management** → **Incidents**
2. Find a port scan or Okta account takeover incident
3. Check whether the incident has the expected **tags** and **severity**

If no new incidents have been created since you set up the rules, you can trigger them by running the detection rules manually:

1. Go to **Hunting** → **Custom detection rules**
2. Find the `Lab Stage 3.5 Internal Port Scan Detected` rule
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
