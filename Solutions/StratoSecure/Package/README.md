# StratoSecure Sentinel Solution — Packaging & Submission Guide

## Status
Code content is complete. The following steps require human operator action.

---

## Step 1: Install Prerequisites (one-time)

```bash
# macOS
brew install --cask powershell
pwsh -Command "Install-Module powershell-yaml -Force"

# Clone Azure-Sentinel repo
git clone https://github.com/Azure/Azure-Sentinel.git ~/Azure-Sentinel
```

---

## Step 2: Prepare Solution Directory

```bash
# Copy solution content into Azure-Sentinel repo structure
cp -r strato-platform/infrastructure/sentinel-solution/ ~/Azure-Sentinel/Solutions/StratoSecure/
```

---

## Step 3: Run V3 Packaging Tool

```pwsh
cd ~/Azure-Sentinel/Tools/Create-Azure-Sentinel-Solution/V3
.\createSolutionV3.ps1 -SolutionDataFolderPath "../../../../Solutions/StratoSecure/Data"
```

Expected output: `Package/1.0.0.zip`, `Package/mainTemplate.json`, `Package/createUiDefinition.json`

Verify:
```bash
ls ~/Azure-Sentinel/Solutions/StratoSecure/Package/
```

### Troubleshooting ARM-TTK failures

If the tool reports ARM-TTK failures, read the error messages and fix the offending JSON. Common issues:
- Missing required template fields (`contentVersion`, `$schema`)
- Hardcoded subscription or tenant IDs (use ARM parameters)
- Invalid API versions — use `2024-09-01` for Sentinel resources
- Logic App apiVersion must be `2017-07-01`

---

## Step 4: Submit GitHub PR

1. Create a fork of `Azure/Azure-Sentinel` if not already done
2. Create a branch: `stratosecure-v1.0.0`
3. Copy `Solutions/StratoSecure/` from local clone to your fork
4. Open PR targeting `master` branch with title: `[Solution] StratoSecure Security Platform v1.0.0`
5. Record PR URL in `.planning/STATE.md`

---

## Step 5: Create Partner Center Offer

1. Go to https://partner.microsoft.com/en-us/dashboard/marketplace-offers
2. Create offer with:
   - **Offer ID**: `azure-sentinel-solution-stratosecure`
   - **Plan type**: `Solution template` (NOT Managed Application)
   - **Plan visibility**: `Public`
   - **Search keyword**: `f1de974b-f438-4719-b423-8bf704ba2aef` (Content Hub GUID)
3. Upload `Package/1.0.0.zip`
4. Submit for automated validation

---

## Step 6: Update STATE.md

After PR is submitted and Partner Center offer created, add to `.planning/STATE.md`:

```markdown
## Phase 17 — SUBMITTED (not yet published)
- GitHub PR: <URL>
- Partner Center Offer ID: azure-sentinel-solution-stratosecure
- Submission Date: YYYY-MM-DD
- Expected Publication: 3-5 weeks after Partner Center approval
```

---

## Content Summary

| Type | Count |
|------|-------|
| Analytics Rules | 6 |
| Watchlists | 8 |
| Workbooks | 3 |
| Playbooks | 7 |
| DCR Tables | 5 |

---

## Support

Email: support@stratocode.io
GitHub Issues: https://github.com/soluetechcorp/strato-platform/issues
