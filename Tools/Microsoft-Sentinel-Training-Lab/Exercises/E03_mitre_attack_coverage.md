# Exercise 3 — MITRE ATT&CK Coverage

**Topic:** Understand and review detection coverage mapped to the MITRE ATT&CK framework
**Difficulty:** Beginner

---

## Objective

Use the **MITRE ATT&CK** page in Microsoft Sentinel to visualise which tactics and techniques your detection rules cover, identify gaps, and understand how the lab's attack chain maps to the framework.

### Background

The MITRE ATT&CK framework is the industry standard for classifying adversary behaviour. Microsoft Sentinel maps every analytics rule to MITRE tactics and techniques, giving you a heat-map view of your detection posture.

The lab solution deploys **17 detection rules** covering a multi-stage attack that spans:

| Tactic | Techniques | Rule examples |
| --- | --- | --- |
| **Initial Access** | T1566.001, T1566.002, T1078.004 | Phishing emails (MailGuard), AWS console login without MFA |
| **Execution** | T1204.002 | Malicious payload execution (CrowdStrike) |
| **Persistence** | T1136.003 | AWS backdoor account creation |
| **Privilege Escalation** | T1098 | Okta account takeover, GCP IAM escalation |
| **Credential Access** | T1003.001, T1556.006 | Credential dumping, MFA factor manipulation |
| **Discovery** | T1046 | Internal port scan (Palo Alto) |
| **Command & Control** | T1071.001 | Data lake promoted threat (Palo Alto) |
| **Exfiltration** | T1041 | Large data transfer to external IP |
| **Impact** | T1496 | AWS/GCP resource abuse |
| **Defense Evasion** | T1562.008 | CloudTrail / GCP logging disabled |

> **Reference:** [View MITRE coverage for your organization from Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/mitre-coverage)

---

### Steps

#### Step 1 — Open the MITRE ATT&CK Page

1. Open the [**Microsoft Defender portal**](https://security.microsoft.com)
2. Navigate to **Microsoft Sentinel** → **Threat management** → **MITRE ATT&CK (Preview)**

![MITRE ATT&CK matrix overview](../Images/OnboardingImage26.png?raw=true)

You will see the ATT&CK matrix with **colour-coded cells**:

| Colour | Meaning |
| --- | --- |
| **Blue (shaded)** | At least one active analytics rule covers this technique |
| **Grey / unshaded** | No rule currently covers this technique |

The number inside each cell indicates how many rules map to that technique.

#### Step 2 — Filter by Active Rules

By default, the matrix shows all coverage sources (analytics rules, hunting queries, etc.). To focus on **deployed detection rules only**:

1. Click the **Filters** button at the top
2. Under **Simulated**, deselect all options
3. Under **Active**, ensure **Analytics rules** is selected

![Filtered analytics rules coverage](../Images/OnboardingImage27.png?raw=true)

The matrix now reflects only your scheduled detection rules. You should see coverage across multiple tactics from the lab's deployed rules.

#### Step 3 — Explore a Covered Technique

Click on a **shaded cell** — for example, **T1046 (Network Service Discovery)** under the **Discovery** tactic.

A side panel opens showing:

- **Description** of the technique
- List of **analytics rules** mapped to it — you should see rules like `Lab Stage 3.5 Internal Port Scan Detected (Palo Alto)` and `Lab [E2] [Palo Alto] Port Scan Detection`
- Coverage from **hunting queries** and **threat intelligence** (if applicable)

![Technique detail side panel](../Images/OnboardingImage28.png?raw=true)

> **Observation:** Notice that some techniques — like **T1046** — have _both_ a stage rule (always enabled) and an exercise rule (disabled by default). The stage rules represent the SOC baseline; the exercise rules are for students to practise.

#### Step 4 — Identify Coverage Gaps

Scroll through the matrix and look for **unshaded cells** in critical tactics. Common gaps you may notice in the lab:

| Tactic | Missing techniques | Why |
| --- | --- | --- |
| **Lateral Movement** | T1021 (Remote Services) | No east-west movement data in the current telemetry |
| **Collection** | T1560 (Archive Collected Data) | Exfiltration is detected at the network level, not at the archiving stage |
| **Resource Development** | T1583 (Acquire Infrastructure) | Pre-attack activity — out of scope for SOC telemetry |

> **Key insight:** Coverage gaps do not always mean risk. Some techniques require specific data sources that may not be available (e.g., host-level telemetry for lateral movement). The MITRE page helps prioritise where to invest detection engineering effort.

#### Step 5 — Map the Lab Attack Chain

Use the MITRE matrix to trace the lab's 10-stage attack chain visually:

1. **Stage 1 (Initial Access)** — Phishing email delivered via MailGuard → T1566.001, T1566.002
2. **Stage 2 (Execution)** — Malicious payload executed on endpoint → T1204.002
3. **Stage 3 (Credential Access)** — Credential dumping via LSASS → T1003.001
4. **Stage 3.5 (Discovery)** — Internal port scan detected by Palo Alto → T1046
5. **Stage 4 (Privilege Escalation)** — Okta account takeover with foreign login → T1078.004, T1098
6. **Stage 6 (Exfiltration)** — Large data transfer to external IP → T1041
7. **Stage 7 (Impact)** — AWS IAM escalation and resource abuse → T1078, T1098, T1496, T1562.008
8. **Stage 8 (Persistence)** — AWS backdoor account login → T1136.003, T1078.004
9. **Stage 9 (Privilege Escalation)** — GCP IAM escalation → T1136.003, T1098, T1496, T1562.008
10. **Stage 10 (Initial Access)** — Phishing campaign bypassing email filtering → T1566.001, T1566.002

Each stage corresponds to one or more shaded cells on the matrix. Clicking through them shows the detection rule responsible.

#### Step 6 — Evaluate a New Detection Idea

Consider a gap you identified in Step 4 and think about how you would close it:

- **What data source do I need?**
- **What KQL query would detect this technique?**
- **What MITRE technique ID should I assign?**

For example, if you wanted to detect **T1110.003 (Password Spraying)** using Okta data:

```kusto
OktaV2_CL
| where TimeGenerated > ago(4h)
| where EventOriginalType == "user.session.start"
| where OriginalOutcomeResult == "FAILURE"
| summarize
    FailedAttempts = count(),
    DistinctUsers = dcount(ActorUsername),
    TargetUsers = make_set(ActorUsername, 25)
    by SrcIpAddr
| where DistinctUsers >= 5
```

This finds a single IP failing authentication against 5 or more distinct users — a classic password spray pattern. If you deployed this as a detection rule and assigned it **T1110.003**, it would appear on the MITRE matrix under **Credential Access**.

> **Tip:** You do not need to deploy this rule. The point is to understand how the MITRE coverage page reflects your detection engineering decisions.

---

### Key Takeaways

- The **MITRE ATT&CK page** in Sentinel provides a real-time heat map of your detection coverage
- Every analytics rule can be tagged with one or more **MITRE technique IDs** — these drive the matrix
- **Coverage gaps** highlight where you lack detections — but not all gaps are equal; prioritise based on available data sources and threat relevance
- The lab's attack chain spans **10 tactics** across multiple data sources — the MITRE page lets you visualise this end-to-end
- Use the technique side panel to see which **specific rules** cover each technique and whether they are enabled or disabled

### Microsoft Learn References

- [View MITRE ATT&CK coverage for your organization](https://learn.microsoft.com/en-us/azure/sentinel/mitre-coverage)
- [MITRE ATT&CK framework](https://attack.mitre.org/)
- [Map data sources to the MITRE ATT&CK framework](https://learn.microsoft.com/en-us/azure/sentinel/map-data-fields-to-entities)
