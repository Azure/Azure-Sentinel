# Project Context, Structure, and Workflow Memory

## Critical Deployment Rules
**ALWAYS FOLLOW THESE RULES TO AVOID CONFLICTS:**
1.  **Repository Source of Truth**: The active repository is **[Data443/Azure-Sentinel](https://github.com/Data443/Azure-Sentinel)**.
2.  **Primary Branch**: All development, fixes, and synchronization must occur on the **`data443-main`** branch.
3.  **One Solution Per PR**: Maintain separate feature branches on the Data443 fork for submitting PRs to specific solutions.
4.  **Clean History**: Ensure your branch only contains commits relevant to that specific solution.

## Active Pull Requests & Status

### 1. TacitRed Defender Threat Intelligence (Official)
- **PR #13266**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13266)
- **Status**: **Active / Official Data443 Submission**
- **Source Branch**: `Data443:feature/tacitred-defender-ti`

### 2. TacitRed SentinelOne IOC Automation (Official)
- **PR #13267**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13267)
- **Status**: **Active / Official Data443 Submission**
- **Source Branch**: `Data443:feature/tacitred-sentinelone-v1`

### 3. TacitRed Threat Intelligence (CCF) (Official)
- **PR #13268**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13268)
- **Status**: **Active / Official Data443 Submission**
- **Source Branch**: `Data443:feature/tacitred-ccf-hub-v2`

### 4. TacitRed CrowdStrike IOC Automation (Official)
- **PR #13269**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13269)
- **Status**: **Active / Official Data443 Submission**
- **Source Branch**: `Data443:feature/tacitred-crowdstrike-ioc`

### 5. Cyren Threat Intelligence (Official)
- **PR #13278**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13278)
- **Status**: **Active / Official Data443 Submission**
- **Source Branch**: `Data443:feature/cyren-threat-intelligence`

### Previous/Obsolete PRs (Closed)
- **PR #13270** (Cyren) -> Replaced by #13278 (branch deleted)
- **PR #13247** (Defender TI) -> Replaced by #13266
- **PR #13243** (SentinelOne) -> Replaced by #13267
- **PR #13242** (TacitRed CCF) -> Replaced by #13268
- **PR #13241** (CrowdStrike) -> Replaced by #13269
- **PR #13224** (Cyren) -> Replaced by #13270

### Important Links

#### TacitRed CCF solution folders (in Azure repo)
- **TacitRedThreatIntelligence (Master)**: [Link](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/TacitRedThreatIntelligence)
- **CyrenThreatIntelligence (Master)**: [Link](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/CyrenThreatIntelligence)
- *Note: When the PR is merged, these folders in master will contain your final code.*

#### TacitRed CrowdStrike IOC solution
- **TacitRed-IOC-CrowdStrike (Master)**: [Link](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/TacitRed-IOC-CrowdStrike)

---

## Standard Operating Procedure (SOP)

### 1. Development (Unified on data443-main)
- **Action**: Make all code changes, edits, and fixes in the **`Solutions/`** folder inside the **`data443-main`** branch.
- **Why**: We push the **actual final package** to Data443, not the staging files. The `Solutions/` folder is the Source of Truth for submission.
- **Development Paths (USE THESE)**:
    - **TacitRed CCF**: `Solutions/TacitRedThreatIntelligence`
    - **Cyren CCF**: `Solutions/CyrenThreatIntelligence`
    - **TacitRed CrowdStrike**: `Solutions/TacitRed-IOC-CrowdStrike`
    - **TacitRed SentinelOne**: `Solutions/TacitRed-SentinelOne`
    - **TacitRed Defender TI**: `Solutions/TacitRed-Defender-ThreatIntelligence`
- **DO NOT USE**: `sentinel-production/` folders for direct editing anymore. Obsolete.
- **Source of Truth**: The `data443-main` branch on `Data443/Azure-Sentinel`.

### 2. Validation (Local)
- **Action**: Run validation tools locally against your changes in the `Solutions/` folder.
- **Location**: `Tools/Azure-Sentinel/`
- **Tools**:
    - **API Version Check**: Verify all Azure resource API versions are up-to-date.
    - **V3 + ARM-TTK (Branch-Agnostic)**: Use the branch-agnostic tooling wrappers under `Deployment-Workflows/Tooling/` (recommended).
        - **Sync tooling once from `data443-main`** (creates stable tooling shim): `Deployment-Workflows/Tooling/SYNC-AZURE-SENTINEL-TOOLING.ps1`
        - **Run V3 packaging + ARM-TTK on any branch**: `Deployment-Workflows/Tooling/RUN-V3-AND-TTK.ps1 -SolutionName <SolutionName>`
        - **ARM-TTK cache**: `Deployment-Workflows/.tooling-cache/arm-ttk/` (persists across branch switches)
        - **V3 tooling shim**: `Deployment-Workflows/.tooling-cache/azure-sentinel-shim/` (stable V3 + `.script` deps)
        - **ARM-TTK version**: Pinned to **v0.26** for PowerShell 7+ compatibility.
        - **CI parity**: The wrapper filters known Microsoft CI-skipped false positives for `id` and `contentProductId`.
        - **Wrapper behavior (important)**:
            - During the V3 run the wrapper sets `DATA443_SKIP_INTERNAL_ARM_TTK=1` to prevent internal ARM-TTK runs inside the V3 tool.
            - ARM-TTK is executed with non-terminating error behavior so filtering can be applied consistently.
        - **Additional CI parity**: The wrapper also filters known false positives in some Logic App validations (ex: `concat()` usage inside `uri`).
        - **Known V3 pitfall (fixed in shim)**: Some V3 tool versions incorrectly treat description arrays (ex: `WorkbookDescription` / `PlaybookDescription`) as file lists. If you see "Failed to download" errors pointing at description text, re-run the tooling sync so your shim is sourced from `data443-main`.
        - **Logs**: `Project/Docs/Validation/<timestamp>/` and `Project/Docs/Tooling-Sync/<timestamp>/`
    - **ARM-TTK (Legacy)**: Run `RUN-TTK-Validation.ps1` against the `Solutions/` folder directly.
    - **TruffleHog**: Scan the specific solution folder in `Solutions/`.

### 3. Promotion & Deployment (Push to Data443)
- **Action**: Commit changes to `data443-main` and push to the Data443 remote.
- **Important**: This pushes the **actual Solution Package** (including clean zips, updated metadata, and correct templates) to the company repo. This is what Microsoft reviews.
- **Manual Push**:
    ```bash
    git checkout data443-main
    git pull origin data443-main
    
    # 1. Edit files in Solutions/YourSolution
    # 2. Cleanup old Zips if needed
    
    git add .
    git commit -m "fix(solution): description of change"
    git push data443-fork data443-main
    ```

### 4. Updating PRs (Branch Sync)
- **Rule (critical)**: Solution PR branches must remain solution-scoped. Do **NOT** merge a shared tooling branch (ex: `data443-main`) into a PR branch if that branch contains shared tooling changes.
- **Tooling updates (recommended)**: To consume the latest V3 + ARM-TTK fixes:
    - Checkout `data443-main` locally and run `Deployment-Workflows/Tooling/SYNC-AZURE-SENTINEL-TOOLING.ps1`.
    - Switch back to the PR branch and run `Deployment-Workflows/Tooling/RUN-V3-AND-TTK.ps1 -SolutionName <SolutionName>`.
    - This keeps tooling changes out of the PR branch while still using the latest known-good tooling.
- **PR updates (content changes)**: Only commit and push changes under `Solutions/<YourSolution>/**` to the PR branch.
- **PR updates (upstream sync)**: If you need to bring in upstream changes, merge/rebase from `upstream/master` (or the repo’s default branch) into your feature branch; avoid merging internal shared tooling branches.

### 5. CI/CD (Remote)
- **Action**: Monitor the Pull Request on GitHub.
- **Check**: Ensure "SolutionValidations", "TruffleHog", and other Microsoft CI checks pass.
- **Archive evidence (required)**: After CI completes, capture and save proof of results under `Project/Docs/Validation/<timestamp>/` (links + copied job output or screenshots for failures).

---

## Environments & Structure

### Production (Primary Source of Truth)
- **Location**: `Tools/Azure-Sentinel/Solutions/` (on `data443-main` branch)
- **Purpose**: This is the live code submitted to Microsoft. **Work here.**

### Staging (Deprecated/Cleanup)
- **Old Location**: `sentinel-production/`
- **Action**: Do not rely on this folder for official fixes. Changes must be made in `Solutions/` to be tracked by the official repo.

## Tools

### ARM TTK (Template Test Kit)
- **Recommended (Branch-Agnostic)**:
    - `Deployment-Workflows/Tooling/SYNC-AZURE-SENTINEL-TOOLING.ps1` (sync stable V3 tooling from `data443-main`)
    - `Deployment-Workflows/Tooling/RUN-V3-AND-TTK.ps1 -SolutionName <SolutionName>` (runs V3 + ARM-TTK with consistent cache)
- **Cache Location**: `Deployment-Workflows/.tooling-cache/arm-ttk/`
- **Log Location**: `Project/Docs/Validation/<timestamp>/`
- **Legacy Location**: `sentinel-production/Project/Tools/arm-ttk`
- **Legacy Runner Script**: `sentinel-production/Project/Deployment-Workflows/RUN-TTK-Validation.ps1`

### Sentinel CI
- **Location**: `sentinel-production/Project/Tools/SentinelCI`

## Workflows

### Unified Deployment
- **Directory**: `sentinel-production/Project/Deployment-Workflows`
- **Script**: `DEPLOY-UNIFIED.ps1`
- **Features**: Auto-versioning, Auto-zipping, TruffleHog Scan, Upstream Sync, Git Push.

## Pre-Submission Checklist (Critical Lessons Learned)
Before creating a Pull Request, you **MUST** verify the following to ensure it passes 'SolutionValidations' and 'SafeToRun' constraints:

### 1. File Hygiene
- [ ] **Allowed Extensions Only**: Ensure the solution folder contains **ONLY** `.json`, `.zip`, `.md`, `.txt`, `.png`, `.svg`.
- [ ] **Prohibited Files**: Remove ALL `.ps1`, `.py`, `.sh`, `.exe`, `.dll`, `.bin` files.
- [ ] **Clean Up**: Remove any temporary files (`.outofscope`, `.bak`) and **DELETE OLD ZIP VERSIONS** (only keep latest).
- [ ] **Common Tools**: Do NOT modify shared scripts like `Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1` in solution PR branches. If tooling updates are required, land them in `data443-main` and refresh the local shim via `Deployment-Workflows/Tooling/SYNC-AZURE-SENTINEL-TOOLING.ps1`.

### 2. Metadata Consistency
- [ ] **Resource Existence**: Ensure `mainTemplate.json` includes the `Microsoft.OperationalInsights/workspaces/providers/contentPackages` resource (kind: Solution).
- [ ] **Variables**: Ensure `mainTemplate.json` has `_solutionName`, `_solutionVersion`, `_solutionId` variables defined.
- [ ] **Version Match**: The `_solutionVersion` in `mainTemplate.json` **MUST MATCH** the version in `packageMetadata.json`.
- [ ] **Package icon format**: Keep `Package/packageMetadata.json` `icon` as inline `<svg ...>` (avoid `<img ...>` tags to reduce validator risk).

### 3. JSON Validation
- [ ] **Syntax Check**: Run `jq empty mainTemplate.json` or use an IDE linter to ensure valid JSON syntax. Trailing commas are a common failure cause.
- [ ] **CreateUIDefinition safety**: Ensure `createUiDefinition.json` has no `null`/blank required fields (especially `label` and `text` in sections).

## Standardized Solution Mapping

| Solution Name | Prod Zip Folder (Work Here) | Notes |
| :--- | :--- | :--- |
| **TacitRedThreatIntelligence** | `Solutions/TacitRedThreatIntelligence/Package` | Uses `Data Connectors` zip source. |
| **CyrenThreatIntelligence** | `Solutions/CyrenThreatIntelligence/Package` | Uses `Data Connectors` zip source. |
| **TacitRed-IOC-CrowdStrike** | `Solutions/TacitRed-IOC-CrowdStrike/Package` | Uses `Playbooks` zip source. |
| **TacitRed-SentinelOne** | `Solutions/TacitRed-SentinelOne/Package` | Uses `Playbooks` zip source. |
| **TacitRed-Defender-ThreatIntelligence** | `Solutions/TacitRed-Defender-ThreatIntelligence/Package` | Uses `Playbooks` zip source. |

## Sync Documentation
When updating `Project_Structure_and_Workflow.md`, you **MUST** commit it to `data443-main` immediately. Updates will be propagated to feature branches during the PR update workflow.
