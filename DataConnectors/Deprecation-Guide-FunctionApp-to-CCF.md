# Deprecation Guide: Migrating Function App Connectors to CCF/CCP

This document defines the safe deprecation path for ISVs migrating legacy Azure Function App data connectors to the Codeless Connector Framework (CCF) or Codeless Connector Platform (CCP).

## Why This Matters

When a customer deploys a function app connector via an ARM template, the deployment permanently writes a Microsoft-owned `aka.ms` link into their Azure Function App's `WEBSITE_RUN_FROM_PACKAGE` setting. That link points to a zip file hosted in this GitHub repository. Azure Functions re-fetches this zip on every cold start.

**If the zip file is deleted from this repository, any customer function app referencing it will silently fail and log ingestion stops — with no warning to the customer.**

## Rules

1. **Never delete the function app zip** (`*AzureFunction.zip`) from the repository as part of a CCF/CCP migration PR.
2. **Never delete the ARM deployment template** (`azuredeploy_*_API_FunctionApp.json`) while customers may still reference it.
3. **Never delete the connector UI definition** (`*_API_FunctionApp.json`) until the solution is fully transitioned in Content Hub.
4. The `aka.ms` redirects are owned by Microsoft. Coordinate with the Microsoft Sentinel Content Hub team before any removal.

## Deprecation Process

### Phase 1: Build and Ship CCF Connector

- Develop and validate your new CCF/CCP connector.
- Submit a PR adding the new connector files alongside the existing function app connector.
- Update the solution's `Data/Solution_*.json` to include both connectors (legacy + new).
- The legacy connector remains fully functional during this phase.

### Phase 2: Mark Legacy Connector as Deprecated

Once the CCF connector is GA-ready and available in Content Hub:

- Add a `[DEPRECATED]` prefix to the legacy connector's `title` field in the connector JSON.
- Update the connector's `description` to inform customers about the migration path.
- Update the solution's `ReleaseNotes.md` with a deprecation notice entry.
- **Do NOT delete any files.** The zip, ARM template, and connector definition must remain.

Example title change:
```json
"title": "[DEPRECATED] Cisco ETD Data Connector"
```

### Phase 3: Migration Window

- Allow a minimum migration window (typically 3–6 months) for customers to transition.
- During this window, both connectors remain available in Content Hub.
- Monitor adoption of the new CCF connector.

### Phase 4: Removal (Post-Deprecation)

After the migration window closes and with explicit approval from the Microsoft Sentinel Content Hub team:

1. **Retarget the aka.ms redirect** to a durable blob copy (coordinated by Microsoft) so existing deployments continue to function.
2. Remove the legacy connector from the solution's content list.
3. Update the Content Hub offer to remove the deprecated connector.
4. The zip file may remain in the repository indefinitely as a safety net, or be removed only after the aka.ms redirect is confirmed retargeted.

## PR Checklist for ISVs

When submitting a CCF migration PR, ensure:

- [ ] New CCF connector files are added (not replacing legacy files)
- [ ] Legacy function app zip (`*.zip`) is **NOT** deleted
- [ ] Legacy ARM template (`azuredeploy_*.json`) is **NOT** deleted
- [ ] Legacy connector JSON (`*_FunctionApp.json`) is **NOT** deleted
- [ ] Solution metadata is updated to include the new connector
- [ ] ReleaseNotes.md is updated with the new version entry
- [ ] No aka.ms redirect changes are assumed (Microsoft owns these)

## PR Checklist for Reviewers

When reviewing a CCF migration PR:

- [ ] Verify no legacy function app files are deleted
- [ ] Confirm the zip file is intact
- [ ] Check that aka.ms links are not broken or assumed to be retargeted
- [ ] If legacy files ARE deleted, **block the PR** and direct the contributor to this guide

## Contact

- For Content Hub offer changes: Contact the Microsoft Sentinel Content Hub representative
- For aka.ms redirect retargeting: Contact the Microsoft Sentinel partner team at [AzureSentinelPartner@microsoft.com](mailto:AzureSentinelPartner@microsoft.com)
- For CCF engineering questions: [aka.ms/ccf-eng-support](https://aka.ms/ccf-eng-support)
