# Sentinel Playbook Template Rendering — Root Cause Analysis

## Problem

When deploying the Check Point Exposure Management Alerts Solution v3.1.0 via `Package/mainTemplate.json`, all 8 playbook templates failed to appear in the Sentinel portal's **Automation > Playbook Templates** tab. The portal showed "One or more playbook templates failed to load" error banner. The same templates worked when deployed as individual standalone ARM templates.

## Root Causes (3 issues found)

### 1. Parameter Name: `Playbook_Name` vs `PlaybookName` (PRIMARY)

The Sentinel portal's playbook template renderer **requires** the Logic App name parameter to be named exactly `PlaybookName` (PascalCase, no underscore). Our templates used `Playbook_Name` with an underscore, which caused the portal's static parser to fail to load them entirely.

**Fix:** Renamed `Playbook_Name` → `PlaybookName` across all files.

- `Package/mainTemplate.json` — 41 occurrences
- 9 standalone `azuredeploy.json` files — 27 occurrences
- 8 `readme.md` files — 8 occurrences

### 2. Metadata Variable References: Double-Bracket Escaping

Inside nested `contentTemplate` resources in `mainTemplate.json`, metadata fields (`contentId`, `version`, `sourceId`) used double-bracket ARM expressions `[[variables(...)]` where they should have used single-bracket `[variables(...)]`. The double-bracket syntax is only needed for values that must be stored as literal ARM expressions — metadata fields should be resolved at deploy time.

**Fix:** Changed `[[variables(` → `[variables(` in 24 metadata references.

### 3. Playbook Version Format: `"1.0.0"` vs `"1.0"`

The `playbookVersion` values in metadata resources used semver `"1.0.0"` format, but the Sentinel content framework expects `"major.minor"` format (`"1.0"`).

**Fix:** Changed `"1.0.0"` → `"1.0"` in 8 playbook metadata resources.

## How We Debugged It

The root cause was identified through systematic binary-search elimination:

1. **Deployed bare-bones Logic App** (simple trigger, no actions, `PlaybookName` param) inside our contentPackages → **Worked**. Proved the issue was in template content, not the package envelope.
2. **Tested metadata key variations** (`postDeployment` vs `postdeploymentsteps`) → Not the issue.
3. **Tested SecureString parameters** → Not the issue.
4. **Tested full ManualStatusUpdate template as-is** → Failed.
5. **Tested full ManualStatusUpdate with simplified metadata** → Still failed.
6. **Tested working template but with `Playbook_Name` (underscore)** → **Failed**. Root cause identified.
7. **Tested full ManualStatusUpdate actions with `PlaybookName` (no underscore)** → **Worked**. Fix confirmed.

## Key Takeaways

- The Sentinel portal **statically parses** stored `mainTemplate` JSON to render the Playbook Templates tab. It does not execute ARM — it pattern-matches on known parameter names.
- `PlaybookName` is a **hard-coded convention** the portal expects. Other parameter names are fine, but the Logic App name parameter must be exactly `PlaybookName`.
- Standalone ARM deployment succeeds regardless of parameter naming (ARM doesn't care), which is why the issue only surfaced through Content Hub / mainTemplate deployment.
- When debugging contentTemplate rendering issues, create a minimal template and progressively add complexity to isolate the failing element.
