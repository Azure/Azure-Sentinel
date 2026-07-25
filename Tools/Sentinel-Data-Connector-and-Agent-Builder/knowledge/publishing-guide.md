# Publishing Agent to Security Store

## Overview

This guide covers packaging a Security Copilot agent and publishing it to the Microsoft Security Store via Partner Center.

**Architecture:**
```
Agent Development → Create Package (.zip) → SaaS Offer in Partner Center → Review → Live in Security Store
```

## Prerequisites

- Working Security Copilot agent (Lab 5 completed)
- Microsoft Partner Center account
- Agent tested and SCU consumption measured

---

## Task 1: Create the Deployment Package

### Package Structure

```
agent-package/
├── PackageManifest.yaml    (required)
└── YourAgentName/
    └── AgentManifest.yaml  (required)
```

### PackageManifest.yaml

```yaml
manifest:
  - id: "IdentityDriftInvestigationAgent"    # No spaces
    description: "Agent to investigate Identity Threats"
    type: CopilotAgent                        # or SentinelLake for notebooks
schema:
  version: "1.0.0"
```

### AgentManifest.yaml

Export from Security Copilot:
1. Go to [securitycopilot.microsoft.com](https://securitycopilot.microsoft.com)
2. Navigate to **Build** tab
3. Select your agent
4. Download the manifest

### Critical Manifest Rules

| Rule | Requirement |
|------|-------------|
| `Product` and `Publisher` | Must be actual ISV name, NOT "Custom" |
| Settings key names | Must EXACTLY match Skill input names (no spaces, case-sensitive) |
| Input descriptions | Every field must have meaningful `Description` |
| Skill names | Must be descriptive actions (e.g., `GetSignInLogsForUser`) NOT `"Agent v3"` |
| `RequiredSkillsets` | Must include `MCP.Sentinel` if using Sentinel |
| KQL time windows | Never hardcode — use parameterized `{{TimeRange}}` |
| Grammar | Full grammar check on all YAML text fields |

### Create ZIP Package

**Mac (avoid hidden files):**
```bash
cd /path/to/agent-package
zip -r agent-package.zip . -x ".*" -x "__MACOSX"
```

**Windows/Linux:**
```bash
cd agent-package
zip -r agent-package.zip .
```

**Verify:**
```bash
unzip -l agent-package.zip
# Should show only:
# PackageManifest.yaml
# YourAgentName/AgentManifest.yaml
```

---

## Task 2: Gather Required Information

Before Partner Center, prepare:

| Item | Requirement |
|------|-------------|
| Agent name | Must NOT contain Microsoft product names |
| Agent description | Structured format (Tasks, Inputs, Outputs) |
| Marketing/Product URL | Required under Links section |
| User guide PDF | Instructions to install/use the agent |
| Logo | 216×216 px |
| Screenshots | 1280×720 px, showing full agent execution |
| Webhook URL | For order notifications (placeholder OK) |
| SCU estimate | From 3-5 test runs averaged |

### Agent Description Format

```
[Agent name] is a security investigation agent that integrates with 
Microsoft Sentinel to [brief purpose statement].

Agent Tasks:
- Task 1 (e.g., Identity threat triage)
- Task 2 (e.g., Authentication analysis)
- Task 3 (e.g., Cross-telemetry correlation)

Agent Workflow:

Input:
- UserPrincipalName (UPN) — the user account to investigate
- Access to Microsoft Sentinel Data Lake tables (TableA_CL, TableB_CL)
- Time range: TimeGenerated > ago(24h)

Output:
- MFA activity summary
- Sign-in success/failure summary with distinct IPs
- User risk level and state
- Suspicious process execution summary
- Correlated identity-to-endpoint insights
- Concise triage summary report
```

---

## Task 3: Create SaaS Offer in Partner Center

### Step 3.1: Access Partner Center
1. Go to [partner.microsoft.com/dashboard](https://partner.microsoft.com/dashboard)
2. Navigate to **Marketplace offers**

### Step 3.2: Create Offer
1. Click **New offer** → **Software as a Service (SaaS)**
2. **Start with blank offer** or **Clone existing offer** (faster)
3. **Offer ID:** lowercase with hyphens (e.g., `identity-drift-agent`)
4. **Alias:** Display name

### Step 3.3: Offer Setup
1. **Sell through Microsoft?** → Yes
2. **Microsoft license management?** → No
3. **Microsoft integrations:** ✓ "My offer integrates with Microsoft Security services"

> **CRITICAL:** Without checking "integrates with Microsoft Security services", the Security services section won't appear in navigation — this is where you upload the .zip package.

### Step 3.4: Properties
1. **Categories:** Security or Compliance
2. **Legal:** Standard Contract or custom

### Step 3.5: Offer Listing
1. **Search results summary** — Single line description
2. **Description** — Structured format (Tasks, Inputs, Outputs)
3. **Images:** Logo (216×216) + Screenshots (1280×720)
4. **Product information documents:** Upload User Guide PDF
5. **Links:** Add marketing/product page URL

### Step 3.6: Microsoft Security Services
1. **Integrated services:** ✓ Microsoft Security Copilot ✓ Microsoft Sentinel ✓ Microsoft Defender ✓ Microsoft Entra (as applicable)
2. **Product prerequisites:** ✓ Microsoft Security Copilot, ✓ Microsoft Sentinel, ✓ Microsoft Defender, ✓ Microsoft Entra (check all that apply to the agent's data sources)
3. **Solution type:** ✓ Deployable solution
4. **License management:** Choose based on your model
5. **Security Copilot agent:** ✓ Check **"Security Copilot agent"**
6. **Upload .zip package**

> Integrated products selection MUST match what agent actually uses. Mismatches = hard failure.

### Step 3.7: Preview Audience
1. Add Entra IDs of testers
2. Share preview URL for feedback

### Step 3.8: Technical Configuration
1. **Landing page URL:** `https://securitystore.microsoft.com/mysolutions`
2. **Connection webhook:** Your URL (placeholder OK)
3. **Entra tenant ID** and **App ID**

> Partner Center BLOCKS submission if Technical Config isn't filled. Use dummy values if not ready.

### Step 3.9: Plan and Pricing

**For Free agents:**
- Flat rate, $0 USD
- Include SCU estimate in plan description

**For Paid agents:**
- Choose flat rate or per-user
- Set contract duration and billing

**Plan description example:**
```
The Acme Identity Threat Triage Agent is available at no cost. 
This agent typically consumes 1.0 SCU per analysis run.
```

### Step 3.10: Supplement Content
1. SaaS Scenarios → "SaaS solution is not hosted in Azure"
2. Text box: "Offer listing is for Security Copilot Agent in Microsoft Security Store"
3. Upload architecture diagram

---

## Task 4: Publish

### Pre-Publish Checklist

- [ ] Agent name has NO Microsoft product names
- [ ] `Product`/`Publisher` in manifest = actual ISV name
- [ ] Settings keys match Skill input names exactly
- [ ] `MCP.Sentinel` in RequiredSkillsets
- [ ] Marketing link added in Offer Listing → Links
- [ ] User guide PDF uploaded
- [ ] Screenshot shows full agent execution + Sentinel under Plugins
- [ ] SCU estimate in plan description
- [ ] Technical config filled (dummy values OK)
- [ ] Grammar check on all text fields

### Submit
1. Click **Review and publish**
2. Fix any validation errors
3. Click **Publish**
4. After automated review → Click **Go Live**

### Monitor Status
- 🟡 In review — Being validated
- 🔴 Changes required — Corrections needed
- 🟢 Published — Live in Security Store

### Verify
Check listing at: `https://securitystore.microsoft.com/agents`

---

## Common Review Failures

| Failure | Fix |
|---------|-----|
| Agent name contains "Security Copilot" | Remove all Microsoft product names |
| `Product: Custom` in manifest | Replace with actual ISV product name |
| Screenshots show only config | Include full execution run screenshot |
| No marketing link | Add under Offer Listing → Links |
| No SCU estimate | Add to Plan description |
| No user guide | Upload PDF under Product information documents |
| Grammar errors | Audit all YAML and description text fields |

---

## References

- [Publish Security Copilot Agent to Security Store](https://learn.microsoft.com/en-us/security/store/publish-a-security-copilot-agent-or-analytics-solution-in-security-store)
- [Microsoft Security Store](https://securitystore.microsoft.com/)
- [Microsoft Partner Center](https://partner.microsoft.com/)
- [Preview and test offer listing](https://learn.microsoft.com/en-us/security/store/preview-and-test-your-offer-listing-for-security-store)
- [SaaS Fulfillment Webhook](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/pc-saas-fulfillment-webhook)
- [Manage SCU Usage](https://learn.microsoft.com/en-us/copilot/security/manage-usage)
- [Reference example agent listing](https://securitystore.microsoft.com/)
