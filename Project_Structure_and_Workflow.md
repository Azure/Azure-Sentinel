# Project Context, Structure, and Workflow Memory

## Critical Deployment Rules
**ALWAYS FOLLOW THESE RULES TO AVOID CONFLICTS:**
1.  **One Solution Per PR**: Never bundle multiple solutions into a single Pull Request.
2.  **Separate Branches**: Create a dedicated feature branch for each solution (e.g., `feature/solution-name`).
3.  **Clean History**: Ensure your branch only contains commits relevant to that specific solution.

## Active Pull Requests & Status

### 1. Cyren Threat Intelligence
- **PR #13224**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13224)
- **Status**: Active / In Review
- **Source Branch**: [`feature/cyren-threat-intelligence-clean`](https://github.com/mazamizo21/Azure-Sentinel/tree/feature/cyren-threat-intelligence-clean)

### 2. TacitRed CrowdStrike IOC
- **PR #13241**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13241)
- **Status**: Active / In Review
- **Source Branch**: [`feature/tacitred-crowdstrike-ioc`](https://github.com/mazamizo21/Azure-Sentinel/tree/feature/tacitred-crowdstrike-ioc)

### 3. TacitRed Threat Intelligence (CCF)
- **PR #13242**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13242)
- **Status**: Active / In Review
- **Source Branch**: [`feature/tacitred-ccf-hub-v2`](https://github.com/mazamizo21/Azure-Sentinel/tree/feature/tacitred-ccf-hub-v2)

### 4. TacitRed SentinelOne
- **PR #13243**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13243)
- **Status**: Active / In Review
- **Source Branch**: [`feature/tacitred-sentinelone-v1`](https://github.com/mazamizo21/Azure-Sentinel/tree/feature/tacitred-sentinelone-v1)

### 5. TacitRed Defender Threat Intelligence
- **PR #13247**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13247)
- **Status**: **Submitted / Waiting for CI**
- **Source Branch**: [`feature/tacitred-defender-ti`](https://github.com/mazamizo21/Azure-Sentinel/tree/feature/tacitred-defender-ti)

### Guidance
- Use **“Conversation”** tab on the PR to see reviewer comments.
- Use **“Checks”** tab to see latest SolutionValidations / arm‑ttk / KQL checks.

### Previous/Related PR
- **PR #13204**: [Azure-Sentinel Pull Request](https://github.com/Azure/Azure-Sentinel/pull/13204) (Superseded)

### Important Links

#### TacitRed CCF solution folders (in Azure repo)
- **TacitRedThreatIntelligence (Master)**: [Link](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/TacitRedThreatIntelligence)
- **CyrenThreatIntelligence (Master)**: [Link](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/CyrenThreatIntelligence)
- *Note: When the PR is merged, these folders in master will contain your final code.*

#### TacitRed CrowdStrike IOC solution
- **TacitRed-IOC-CrowdStrike (Master)**: [Link](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/TacitRed-IOC-CrowdStrike)
- **TacitRed-IOC-CrowdStrike (Fork/PR Context)**: [Link](https://github.com/mazamizo21/Azure-Sentinel/tree/feature/tacitred-ccf-hub-v2threatintelligence/Solutions/TacitRed-IOC-CrowdStrike)

---

## Standard Operating Procedure (SOP)

### 1. Development (Staging)
- **Action**: Make all code changes, edits, and fixes in the **Staging** environment.
- **Locations**:
    - **TacitRed CCF**: `sentinel-production/Tacitred-CCF-Hub-v2`
    - **Cyren CCF**: `sentinel-production/Cyren-CCF-Hub`
    - **TacitRed CrowdStrike**: `sentinel-production/TacitRed-IOC-CrowdStrike`
    - **TacitRed SentinelOne**: `sentinel-production/TacitRed-SentinelOne`
- **Note**: These folders are the **Source of Truth**. Any changes made directly to the Production folder will be overwritten by the Deployment script.

### 2. Validation (Local)
- **Action**: Run validation tools locally against the **Staging** files to catch errors before uploading.
- **Location**: `sentinel-production/Project/Deployment-Workflows/`
- **Tools**:
    - **API Version Check**: Verify all Azure resource API versions are up-to-date
        - Check https://learn.microsoft.com/en-us/azure/templates/ for latest versions
        - Common resources: Microsoft.Web/sites (2024-04-01), Microsoft.Logic/workflows (2019-05-01)
    - **ARM-TTK**: Run `RUN-TTK-Validation.ps1 -SolutionName "Tacitred-CCF-Hub-v2"` (or other solution name).
    - **TruffleHog**: Automatically run as part of the deployment script, or manually via `TruffleHog/run_safe_scan.sh`.


### 3. Promotion & Deployment (Unified)
- **Action**: Run the **Unified Deployment Script** to handle everything end-to-end.
- **Script**: `DEPLOY-UNIFIED.ps1`
- **Location**: `sentinel-production/Project/Deployment-Workflows/`
- **Usage**: 
    - **Live Deployment**: `pwsh -NoLogo -ExecutionPolicy Bypass -File ./Project/Deployment-Workflows/DEPLOY-UNIFIED.ps1`
    - **Dry Run (Test)**: `pwsh -NoLogo -ExecutionPolicy Bypass -File ./Project/Deployment-Workflows/DEPLOY-UNIFIED.ps1 -DryRun`
- **What this SINGLE script does**:
    1.  **Security Scan**: Runs TruffleHog once for the whole project.
    2.  **Upstream Sync**: Syncs your repo with Microsoft's `master` branch once.
    3.  **Loop Through All Solutions**:
        *   **Auto-Versioning**: Increments version in `packageMetadata.json` (and `mainTemplate.json` if applicable).
        *   **Packaging**: Zips the appropriate folder (`Data Connectors` or `Playbooks`) into a versioned zip (e.g., `3.0.1.zip`).
        *   **Promote**: Copies all files to the Production folder.
        *   **Git Stage**: Adds changes to git staging area.
    4.  **Commit & Push**: Commits all changes for all solutions in one go and pushes to GitHub (Microsoft Fork).
    5.  **Sync to Data443**: Automatically pushes the same changes to the private Data443 repository (`data443` remote) as a backup.

### 4. CI/CD (Remote)
- **Action**: Monitor the Pull Request on GitHub.
- **Check**: Ensure "SolutionValidations", "TruffleHog", and other Microsoft CI checks pass.

---

## Environments & Structure

### Staging
- **TacitRed CCF**: `sentinel-production/Tacitred-CCF-Hub-v2`
- **Cyren CCF**: `sentinel-production/Cyren-CCF-Hub`
- **TacitRed CrowdStrike**: `sentinel-production/TacitRed-IOC-CrowdStrike`
- **TacitRed SentinelOne**: `sentinel-production/TacitRed-SentinelOne`

### Production
- **Location**: `sentinel-production/Project/Tools/Azure-Sentinel/Solutions/`
- **Purpose**: The official production version of the solutions, located within the Azure-Sentinel solutions repository structure.

## Tools

### ARM TTK (Template Test Kit)
- **Location**: `sentinel-production/Project/Tools/arm-ttk`
- **Runner Script**: `sentinel-production/Project/Deployment-Workflows/RUN-TTK-Validation.ps1`

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
- [ ] **Common Tools**: Do NOT modify shared scripts like `Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1`.

### 2. Metadata Consistency
- [ ] **Resource Existence**: Ensure `mainTemplate.json` includes the `Microsoft.OperationalInsights/workspaces/providers/contentPackages` resource (kind: Solution).
- [ ] **Variables**: Ensure `mainTemplate.json` has `_solutionName`, `_solutionVersion`, `_solutionId` variables defined.
- [ ] **Version Match**: The `_solutionVersion` in `mainTemplate.json` **MUST MATCH** the version in `packageMetadata.json`.

### 3. JSON Validation
- [ ] **Syntax Check**: Run `jq empty mainTemplate.json` or use an IDE linter to ensure valid JSON syntax. Trailing commas are a common failure cause.

## Standardized Solution Mapping

| Solution Name | Staging Path | Prod Zip Folder | Notes |
| :--- | :--- | :--- | :--- |
| **TacitRedThreatIntelligence** | `Tacitred-CCF-Hub` | `Solutions/TacitRedThreatIntelligence/Package` | Uses `Data Connectors` zip source. |
| **CyrenThreatIntelligence** | `Cyren-CCF-Hub` | `Solutions/CyrenThreatIntelligence/Package` | Uses `Data Connectors` zip source. |
| **TacitRed-IOC-CrowdStrike** | `TacitRed-IOC-CrowdStrike` | `Solutions/TacitRed-IOC-CrowdStrike/Package` | Uses `Playbooks` zip source. |
| **TacitRed-SentinelOne** | `TacitRed-SentinelOne` | `Solutions/TacitRed-SentinelOne/Package` | Uses `Playbooks` zip source. |

## PR & Validation Procedure

1. **Clean Staging**: Always delete `*.zip` in Staging *before* running deployment script (`rm *.zip`).
2. **Run Script**: `pwsh ... -SolutionName "TacitRedThreatIntelligence"`.
3. **Clean Production**: The script creates a new zip but **does not delete old ones** in Prod. You **MUST** manually run `rm 1.0.X.zip` in `Tools/Azure-Sentinel/Solutions/.../Package` to leave *only* the new version.
4. **Push & Verify**: Push to branch. Check PR.
5. **Security Approval**: New PRs require "Security Approval" in GitHub. You cannot bypass this. Ask repository owner.

## Sync Documentation
When updating `Project_Structure_and_Workflow.md`, you **MUST** sync this single file to ALL active feature branches immediately to prevent outdated instructions.
