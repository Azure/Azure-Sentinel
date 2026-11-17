#!/usr/bin/env node
/**
 * Local Validation Runner for Azure Sentinel
 *
 * Runs the same validation checks that GitHub Actions CI performs,
 * but locally — without requiring GitHub API access, PR context, or secrets.
 *
 * This script replaces the GitHub-dependent file discovery layer (gitHubWrapper / Octokit)
 * with local git operations, while reusing the exact same checker utilities that CI uses.
 *
 * Usage:
 *   node .script/local-validation/validate.js --diff <branch>        # Validate files changed vs <branch>
 *   node .script/local-validation/validate.js --path <directory>      # Validate all matching files in <directory>
 *   node .script/local-validation/validate.js --files <f1> <f2> ...   # Validate specific files
 *   node .script/local-validation/validate.js                         # Auto-detect: diff against main/master
 *
 * Options:
 *   --diff <branch>       Compare current HEAD against <branch> (default: main or master)
 *   --path <directory>    Validate all matching files under <directory>
 *   --files <f1> <f2>     Validate specific file paths
 *   --skip <validators>   Comma-separated list of validators to skip (e.g. --skip kql,arm-ttk)
 *   --only <validators>   Run only specified validators (e.g. --only json,yaml,data-connector)
 *   --verbose             Show detailed output for all files (not just failures)
 *   --json                Output results as JSON (for programmatic consumption)
 *   --json-file <path>    Write complete JSON results to a file (used by the build runner)
 *   --repository-root <path> Use this repository root for discovery and validation
 *   --help                Show this help message
 *
 * Exit codes:
 *   0 = All validations passed
 *   1 = One or more validations failed
 *   2 = Configuration/usage error
 *
 * Requirements:
 *   - Run from the repository root directory, or pass --repository-root <path>
 *   - Node.js 16+ with npm dependencies installed (npm install)
 *   - TypeScript compiled (npm run tsc)
 *   - For .NET validators: the SDK and each test project's target runtime installed
 *   - For ARM-TTK: PowerShell with ARM-TTK module
 */
import { execFileSync, execSync } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
// --- Safe imports: pure checker utilities with ZERO GitHub/Octokit dependencies ---
import { isValidSchema } from "../utils/jsonSchemaChecker.js";
import { isValidId } from "../utils/dataConnectorCheckers/idChecker.js";
import { isValidDataType } from "../utils/dataConnectorCheckers/dataTypeChecker.js";
import { isValidPermissions } from "../utils/dataConnectorCheckers/permissionsChecker.js";
import { ConnectorCategory } from "../utils/dataConnector.js";
import { isValidLogoImage } from "../utils/LogoChecker/logoImageChecker.js";
import { isValidLogoImageSVGContent } from "../utils/LogoChecker/logoImageSVGChecker.js";
import { isValidSampleData } from "../utils/sampleDataCheckers/sampleDataCheckers.js";
import { doDefinedLogoImageFilesExist, doDefinedPreviewImageFilesExist } from "../utils/workbookCheckers/imageExistChecker.js";
import { isValidPreviewImageFileNames } from "../utils/workbookCheckers/previewImageChecker.js";
import { isUniqueKeys } from "../utils/workbookCheckers/uniqueWorkbookKeyChecker.js";
import { doesNotContainResourceInfo } from "../utils/workbookCheckers/workbookTemplateCheckers/containResourceInfoChecker.js";
import { isFromTemplateIdNotSentinelUserWorkbook } from "../utils/workbookCheckers/workbookTemplateCheckers/fromTemplateIdChecker.js";
import { validateTemplateMetadata } from "../utils/playbookCheckers/playbookArmTemplateMetadataChecker.js";
import { validateTemplateParameters } from "../utils/playbookCheckers/playbookArmTemplateParametersChecker.js";
import { getTemplatePlaybookResources } from "../utils/playbookCheckers/playbookARMTemplateUtils.js";
import { validatePlaybookResource } from "../utils/playbookCheckers/playbookResourceChecker.js";
import { IsValidSolutionDomainsVerticals } from "../SolutionValidations/validDomainsVerticals.js";
import { IsValidSupportObject } from "../SolutionValidations/validSupportObject.js";
import { IsValidBrandingContent } from "../SolutionValidations/validMSBranding.js";
import { IsValidSolutionID } from "../SolutionValidations/validSolutionID.js";
const toolkitRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const invocationDirectory = process.cwd();
let contentRoot = toolkitRoot;
// ============================================================================
// CLI ARGUMENT PARSING
// ============================================================================
function printHelp() {
    const lines = fs.readFileSync(new URL(import.meta.url), "utf8").split("\n");
    const helpLines = [];
    let inHeader = false;
    for (const line of lines) {
        if (line.startsWith("/**")) {
            inHeader = true;
            continue;
        }
        if (inHeader && line.includes("*/")) {
            break;
        }
        if (inHeader && line.startsWith(" *")) {
            helpLines.push(line.replace(/^ \* ?/, ""));
        }
    }
    console.log(helpLines.join("\n"));
}
function isPathWithin(rootPath, candidatePath) {
    const relativePath = path.relative(rootPath, candidatePath);
    return relativePath === ""
        || (relativePath !== ".." && !relativePath.startsWith(`..${path.sep}`) && !path.isAbsolute(relativePath));
}
function parseArgs(argv) {
    const args = argv.slice(2); // Skip node and script path
    const options = {
        mode: "auto",
        skip: [],
        only: [],
        verbose: false,
        jsonOutput: false,
    };
    let i = 0;
    while (i < args.length) {
        switch (args[i]) {
            case "--diff":
                options.mode = "diff";
                i++;
                if (i < args.length && !args[i].startsWith("--")) {
                    options.targetBranch = args[i];
                    i++;
                }
                break;
            case "--path":
                options.mode = "path";
                i++;
                if (i < args.length && !args[i].startsWith("--")) {
                    options.targetPath = args[i];
                    i++;
                }
                else {
                    console.error("Error: --path requires a directory argument");
                    process.exit(2);
                }
                break;
            case "--files":
                options.mode = "files";
                options.files = [];
                i++;
                while (i < args.length && !args[i].startsWith("--")) {
                    options.files.push(args[i]);
                    i++;
                }
                if (options.files.length === 0) {
                    console.error("Error: --files requires at least one file argument");
                    process.exit(2);
                }
                break;
            case "--skip":
                i++;
                if (i < args.length) {
                    options.skip = args[i].split(",").map(s => s.trim().toLowerCase());
                    i++;
                }
                break;
            case "--only":
                i++;
                if (i < args.length) {
                    options.only = args[i].split(",").map(s => s.trim().toLowerCase());
                    i++;
                }
                break;
            case "--verbose":
                options.verbose = true;
                i++;
                break;
            case "--json":
                options.jsonOutput = true;
                i++;
                break;
            case "--json-file":
                i++;
                if (i < args.length && !args[i].startsWith("--")) {
                    options.jsonFilePath = args[i];
                    options.jsonOutput = true;
                    i++;
                }
                else {
                    console.error("Error: --json-file requires a file path");
                    process.exit(2);
                }
                break;
            case "--repository-root":
                i++;
                if (i < args.length && !args[i].startsWith("--")) {
                    options.repositoryRoot = args[i];
                    i++;
                }
                else {
                    console.error("Error: --repository-root requires a directory path");
                    process.exit(2);
                }
                break;
            case "--help":
            case "-h":
                printHelp();
                process.exit(0);
            default:
                console.error(`Unknown argument: ${args[i]}`);
                process.exit(2);
        }
    }
    return options;
}
// ============================================================================
// FILE DISCOVERY
// ============================================================================
/**
 * Detects the default branch name (main or master).
 */
function detectDefaultBranch() {
    try {
        const branches = execSync("git branch -a", { encoding: "utf8" });
        if (branches.includes("remotes/origin/main") || branches.includes("* main")) {
            return "main";
        }
        if (branches.includes("remotes/origin/master") || branches.includes("* master")) {
            return "master";
        }
    }
    catch {
        // Ignore errors
    }
    return "main"; // Default fallback
}
/**
 * Gets files changed between current HEAD and the target branch using git diff.
 * Returns files with their change status (Added, Modified, etc.).
 */
function getChangedFiles(targetBranch) {
    try {
        // Make sure we have the target branch ref
        try {
            execFileSync("git", ["rev-parse", "--verify", targetBranch], { encoding: "utf8", stdio: "pipe" });
        }
        catch {
            // Try fetching it
            try {
                execFileSync("git", ["fetch", "origin", `${targetBranch}:${targetBranch}`, "--no-tags", "--depth=1"], { encoding: "utf8", stdio: "pipe" });
            }
            catch {
                console.warn(`Warning: Could not find or fetch branch '${targetBranch}'. Trying origin/${targetBranch}...`);
                targetBranch = `origin/${targetBranch}`;
            }
        }
        const mergeBase = execFileSync("git", ["merge-base", targetBranch, "HEAD"], { encoding: "utf8" }).trim();
        const diffOutput = execFileSync("git", ["diff", "--name-status", mergeBase, "HEAD"], { encoding: "utf8" });
        return diffOutput
            .split("\n")
            .filter(line => line.trim().length > 0)
            .map(line => {
            const parts = line.split("\t");
            const status = parts[0].charAt(0); // First character: A, M, D, R, C
            const filePath = parts.length >= 3 ? parts[2] : parts[1]; // Renamed files have old\tnew
            return { status, filePath };
        })
            .filter(f => f.filePath && !f.filePath.startsWith(".script/tests/")); // Exclude test files
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        console.error(`Error getting changed files: ${msg}`);
        console.error("Make sure you're in a git repository and the target branch exists.");
        process.exit(2);
        return []; // Unreachable but satisfies TS
    }
}
/**
 * Recursively gets all files under a directory path.
 */
function getFilesInPath(dirPath) {
    const results = [];
    const resolvedPath = path.resolve(process.cwd(), dirPath);
    if (!isPathWithin(process.cwd(), resolvedPath)
        || !fs.existsSync(resolvedPath)
        || !fs.lstatSync(resolvedPath).isDirectory()
        || fs.lstatSync(resolvedPath).isSymbolicLink()) {
        console.error(`Error: --path must name an existing directory: ${dirPath}`);
        process.exit(2);
    }
    const selectedPathParts = path.relative(process.cwd(), resolvedPath).split(path.sep);
    const isSelectedSolution = selectedPathParts.length === 2 && selectedPathParts[0].toLowerCase() === "solutions";
    function walk(dir) {
        if (!fs.existsSync(dir)) {
            return;
        }
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            if (entry.isDirectory()) {
                if (entry.name === ".git" || entry.name === "node_modules" || entry.name === ".script") {
                    continue; // Skip these directories
                }
                if (isSelectedSolution && ["logs", "reports", "evidence"].includes(entry.name.toLowerCase())) {
                    continue;
                }
                walk(fullPath);
            }
            else {
                if (entry.isSymbolicLink()) {
                    const realPath = fs.realpathSync(fullPath);
                    if (!isPathWithin(process.cwd(), realPath)) {
                        console.error(`Error: content path escapes the selected repository root: ${fullPath}`);
                        process.exit(2);
                    }
                }
                // Normalize to forward slashes (repo-relative paths)
                const relativePath = path.relative(process.cwd(), fullPath).replace(/\\/g, "/");
                results.push({ status: "M", filePath: relativePath }); // Validate current files using modified-file rules
            }
        }
    }
    walk(resolvedPath);
    return results;
}
/**
 * Gets files from explicit file list.
 */
function getExplicitFiles(filePaths) {
    return filePaths
        .map(f => f.replace(/\\/g, "/"))
        .filter(f => {
        if (!fs.existsSync(f)) {
            console.warn(`Warning: File not found, skipping: ${f}`);
            return false;
        }
        return true;
    })
        .map(filePath => ({ status: "A", filePath })); // Treat as "Added" for full validation
}
/**
 * Maps git status codes to human-readable file kinds.
 */
function statusToKind(status) {
    switch (status) {
        case "A": return "Added";
        case "M": return "Modified";
        case "D": return "Deleted";
        case "R": return "Renamed";
        case "C": return "Copied";
        default: return "Modified";
    }
}
// ============================================================================
// VALIDATORS — Reimplemented using pure checker utilities
// ============================================================================
// ----- 1.JSON Syntax Validator -----
async function validateJsonSyntax(filePath, _fileKind) {
    try {
        JSON.parse(fs.readFileSync(filePath, "utf8"));
        return { validator: "JSON Syntax", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "JSON Syntax", filePath, passed: false, error: msg };
    }
}
// ----- 2. YAML Syntax Validator -----
async function validateYamlSyntax(filePath, _fileKind) {
    try {
        // Dynamic import for js-yaml since it may not be typed
        const yamlModule = await import("js-yaml");
        const yamlLoad = yamlModule.default?.load || yamlModule.load;
        yamlLoad(fs.readFileSync(filePath, "utf8"));
        return { validator: "YAML Syntax", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "YAML Syntax", filePath, passed: false, error: msg };
    }
}
// ----- 3. Data Connector Validator -----
// Copied from dataConnectorValidator.ts — these are module-private functions we can't import
function isPotentialConnectorJson(jsonFile) {
    const dataTypes = jsonFile.dataTypes;
    return (typeof jsonFile.id !== "undefined" &&
        typeof jsonFile.connectivityCriterias !== "undefined" &&
        Array.isArray(dataTypes) && dataTypes.length > 0);
}
function getConnectorCategory(dataTypes, instructionSteps) {
    const name = dataTypes[0].name;
    if (name.includes("CommonSecurityLog"))
        return ConnectorCategory.CEF;
    if (name.includes("Syslog"))
        return ConnectorCategory.SysLog;
    if (name.includes("SecurityAlert(ASC)"))
        return ConnectorCategory.SecurityAlertASC;
    if (name.includes("ThreatIntelligenceIndicator"))
        return ConnectorCategory.ThreatIntelligenceIndicator;
    if (name.includes("PowerBIActivity"))
        return ConnectorCategory.PowerBIActivity;
    if (name.includes("MicrosoftPurviewInformationProtection"))
        return ConnectorCategory.MicrosoftPurviewInformationProtection;
    if (name.includes("AzureActivity"))
        return ConnectorCategory.AzureActivity;
    if (name.includes("Event"))
        return ConnectorCategory.Event;
    if (name.includes("SecurityAlert(OATP)"))
        return ConnectorCategory.SecurityAlertOATP;
    if (name.includes("AzureDevOpsAuditing"))
        return ConnectorCategory.AzureDevOpsAuditing;
    if (name.includes("AzureDiagnostics"))
        return ConnectorCategory.AzureDiagnostics;
    if (name.endsWith("_CL")) {
        if (JSON.stringify(instructionSteps).includes("[Deploy To Azure]"))
            return ConnectorCategory.AzureFunction;
        if ((name.includes("meraki") || name.includes("vCenter")) &&
            JSON.stringify(instructionSteps).includes("\"type\":\"InstallAgent\""))
            return ConnectorCategory.SysLog;
        return ConnectorCategory.RestAPI;
    }
    if (name.includes("Dynamics365Activity"))
        return ConnectorCategory.Dynamics365Activity;
    if (name.includes("CrowdstrikeReplicatorV2"))
        return ConnectorCategory.CrowdstrikeReplicatorV2;
    if (name.includes("BloodHoundEnterprise"))
        return ConnectorCategory.BloodHoundEnterprise;
    if (name.includes("AwsS3"))
        return ConnectorCategory.AwsS3;
    if (name.includes("AWS"))
        return ConnectorCategory.AWS;
    if (name.includes("Corelight"))
        return ConnectorCategory.Corelight;
    if (name.includes("SigninLogs"))
        return ConnectorCategory.AzureActiveDirectory;
    if (name.includes("corelight_bacnet"))
        return ConnectorCategory.CorelightConnectorExporter;
    if (name.includes("SecurityIncident"))
        return ConnectorCategory.CybleThreatIntel;
    if (name.includes("IndicatorsOfCompromise"))
        return ConnectorCategory.CrowdStrikeFalconIOC;
    if (name.includes("WizIssues"))
        return ConnectorCategory.Wiz;
    if (name.includes("vectra_isession"))
        return ConnectorCategory.VectraStreamAma;
    return "";
}
async function validateDataConnector(filePath, _fileKind) {
    try {
        if (filePath.includes("Templates")) {
            return { validator: "Data Connector", filePath, passed: true, skipped: true, skipReason: "Templates folder" };
        }
        const jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));
        if (!isPotentialConnectorJson(jsonFile)) {
            return { validator: "Data Connector", filePath, passed: true, skipped: true, skipReason: "Not a connector JSON" };
        }
        if (!jsonFile.dataTypes || jsonFile.dataTypes.length === 0) {
            return { validator: "Data Connector", filePath, passed: true, skipped: true, skipReason: "No dataTypes" };
        }
        if (jsonFile.dataTypes[0].name.includes("Event")) {
            return { validator: "Data Connector", filePath, passed: true, skipped: true, skipReason: "Event type connector" };
        }
        const connectorCategory = getConnectorCategory(jsonFile.dataTypes, jsonFile.instructionSteps || []);
        const schemaPath = path.join(toolkitRoot, `.script/utils/schemas/${connectorCategory}_ConnectorSchema.json`);
        if (fs.existsSync(schemaPath)) {
            const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
            isValidSchema(jsonFile, schema);
        }
        isValidId(jsonFile.id);
        isValidDataType(jsonFile.dataTypes);
        if (!filePath.includes("Microsoft Exchange Security - Exchange On-Premises")) {
            isValidPermissions(jsonFile.permissions, connectorCategory);
        }
        return { validator: "Data Connector", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "Data Connector", filePath, passed: false, error: msg };
    }
}
// ----- 4. Content Validator (MS Branding) -----
async function validateContent(filePath, _fileKind) {
    try {
        const ignoreFiles = ["azure-pipelines", "azureDeploy", "host.json", "proxies.json", "azuredeploy", "function.json"];
        const dataFolder = ["/Data/", "/data/"];
        const dataConnectorsFolder = ["/DataConnectors/", "/Data Connectors/"];
        const requiredFolderFiles = [...dataFolder, ...dataConnectorsFolder, "createUiDefinition.json"];
        const hasIgnoredFile = ignoreFiles.some(item => filePath.includes(item));
        const hasRequiredFolderFiles = requiredFolderFiles.some(item => filePath.includes(item));
        if (hasIgnoredFile || !hasRequiredFolderFiles) {
            return { validator: "Content (MS Branding)", filePath, passed: true, skipped: true, skipReason: "Not applicable" };
        }
        const searchText = "Azure Sentinel";
        const expectedText = "Microsoft Sentinel";
        const hasDataFolder = dataFolder.some(item => filePath.includes(item));
        const hasDataConnectorFolder = dataConnectorsFolder.some(item => filePath.includes(item));
        const jsonTagObj = JSON.parse(fs.readFileSync(path.join(toolkitRoot, ".script/validate-tag.json"), "utf8"));
        let tagName = "";
        if (jsonTagObj.hasOwnProperty("createUiDefinition") && filePath.includes("createUiDefinition")) {
            tagName = jsonTagObj.createUiDefinition;
        }
        else if (hasDataFolder && jsonTagObj.hasOwnProperty("data")) {
            tagName = jsonTagObj.data;
        }
        else if (hasDataConnectorFolder && jsonTagObj.hasOwnProperty("dataConnectors")) {
            tagName = jsonTagObj.dataConnectors;
        }
        if (tagName) {
            const fileContentObj = JSON.parse(fs.readFileSync(filePath, "utf8"));
            let tagContent;
            if (filePath.includes("createUiDefinition.json")) {
                tagContent = fileContentObj?.parameters?.config?.basics?.[tagName]
                    || fileContentObj?.parameters?.config?.basics?.[tagName.charAt(0).toUpperCase() + tagName.slice(1)];
            }
            else {
                tagContent = fileContentObj[tagName]
                    || fileContentObj[tagName.charAt(0).toUpperCase() + tagName.slice(1)];
            }
            if (tagContent && tagContent.toLowerCase().includes(searchText.toLowerCase())) {
                return {
                    validator: "Content (MS Branding)",
                    filePath,
                    passed: false,
                    error: `Please update text from '${searchText}' to '${expectedText}' in '${tagName}' tag`,
                };
            }
        }
        return { validator: "Content (MS Branding)", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "Content (MS Branding)", filePath, passed: false, error: msg };
    }
}
// ----- 5. Logo Validator -----
async function validateLogo(filePath, _fileKind) {
    try {
        if (filePath.includes("Logos") || filePath.includes("Data Connectors/Logo")
            || filePath.includes("Workbooks/Images/Logo") || filePath.includes("Workbooks/Images/Logos")) {
            isValidLogoImage(filePath);
            const svgContent = fs.readFileSync(filePath, { encoding: "utf8", flag: "r" });
            if (svgContent !== "undefined") {
                isValidLogoImageSVGContent(svgContent);
            }
        }
        else {
            return { validator: "Logo", filePath, passed: true, skipped: true, skipReason: "Not a logo path" };
        }
        return { validator: "Logo", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "Logo", filePath, passed: false, error: msg };
    }
}
// ----- 6. Sample Data Validator -----
async function validateSampleData(filePath, _fileKind) {
    try {
        const jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));
        isValidSampleData(jsonFile);
        return { validator: "Sample Data", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "Sample Data", filePath, passed: false, error: msg };
    }
}
// ----- 7. Playbook Validator -----
async function validatePlaybook(filePath, _fileKind) {
    try {
        const playbookARMTemplate = JSON.parse(fs.readFileSync(filePath, "utf8"));
        // Pre-check: only validate files that are actually ARM templates
        if (!playbookARMTemplate.$schema || !String(playbookARMTemplate.$schema).toLowerCase().includes("deploymenttemplate")) {
            return { validator: "Playbook", filePath, passed: true, skipped: true, skipReason: "Not an ARM template" };
        }
        // Validate ARM template schema
        const schemaPath = path.join(toolkitRoot, ".script/utils/schemas/ARM_DeploymentTemplateSchema.json");
        if (fs.existsSync(schemaPath)) {
            const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
            isValidSchema(playbookARMTemplate, schema);
        }
        // Validate playbook-specific checks
        const templatePlaybookResources = getTemplatePlaybookResources(playbookARMTemplate);
        if (templatePlaybookResources.length > 0) {
            validateTemplateParameters(filePath, playbookARMTemplate);
            validateTemplateMetadata(filePath, playbookARMTemplate);
            validatePlaybookResource(filePath, playbookARMTemplate);
        }
        return { validator: "Playbook", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "Playbook", filePath, passed: false, error: msg };
    }
}
// ----- 8. Workbook Template Validator -----
async function validateWorkbookTemplate(filePath, _fileKind) {
    try {
        // Skip WorkbooksMetadata.json — that's handled by the metadata validator
        if (filePath.endsWith("WorkbooksMetadata.json")) {
            return { validator: "Workbook Template", filePath, passed: true, skipped: true, skipReason: "Metadata file" };
        }
        if (/(^|[\\/])XDR Workbooks[\\/]/.test(filePath)) {
            return {
                validator: "Workbook Template",
                filePath,
                passed: true,
                skipped: true,
                skipReason: "Legacy Sentinel Workbook Template validator does not apply to XDR Workbooks; validated by XDR Workbook validator",
            };
        }
        const workbookTemplateString = fs.readFileSync(filePath, "utf8");
        const parsedWorkbookTemplate = JSON.parse(workbookTemplateString);
        // Check if it's actually a Sentinel workbook JSON
        if (typeof parsedWorkbookTemplate.$schema !== "undefined"
            && String(parsedWorkbookTemplate.$schema).includes("schema/workbook.json")
            && typeof parsedWorkbookTemplate.version !== "undefined"
            && parsedWorkbookTemplate.version === "Notebook/1.0") {
            isFromTemplateIdNotSentinelUserWorkbook(parsedWorkbookTemplate);
            doesNotContainResourceInfo(workbookTemplateString);
            return { validator: "Workbook Template", filePath, passed: true };
        }
        if (/(^|[\\/])Workbooks[\\/]/.test(filePath) && parsedWorkbookTemplate.version === "Notebook/1.0") {
            isFromTemplateIdNotSentinelUserWorkbook(parsedWorkbookTemplate);
            doesNotContainResourceInfo(workbookTemplateString);
            return { validator: "Workbook Template", filePath, passed: true };
        }
        return {
            validator: "Workbook Template",
            filePath,
            passed: true,
            skipped: true,
            skipReason: "Not a Sentinel Workbook Template",
        };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "Workbook Template", filePath, passed: false, error: msg };
    }
}
// ----- 9. Workbook Metadata Validator -----
async function validateWorkbookMetadata(filePath, _fileKind) {
    try {
        const workbooksMetadata = JSON.parse(fs.readFileSync(filePath, "utf8"));
        const schemaPath = path.join(toolkitRoot, ".script/utils/schemas/workbooksMetadataSchema.json");
        if (fs.existsSync(schemaPath)) {
            const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
            isValidSchema(workbooksMetadata, schema);
        }
        isUniqueKeys(workbooksMetadata);
        isValidPreviewImageFileNames(workbooksMetadata);
        doDefinedLogoImageFilesExist(workbooksMetadata);
        doDefinedPreviewImageFilesExist(workbooksMetadata);
        // Note: Version increment check (isVersionIncrementedOnModification) requires git diff.
        // In --diff mode, we perform a local git-based version increment check.
        // In --path/--files mode, this check is skipped.
        if (_fileKind === "Modified") {
            // Attempt local version increment check using git
            try {
                const targetBranch = detectDefaultBranch();
                const mergeBase = execFileSync("git", ["merge-base", targetBranch, "HEAD"], { encoding: "utf8" }).trim();
                const diffOutput = execFileSync("git", ["diff", mergeBase, "HEAD", "-W", "--", "Workbooks/WorkbooksMetadata.json"], { encoding: "utf8" });
                if (diffOutput) {
                    const diffLines = diffOutput.split("\n").map(l => l.trim());
                    const versionChanges = extractVersionChanges(diffLines);
                    for (const item of workbooksMetadata) {
                        const templatePath = item.templateRelativePath;
                        if (versionChanges[templatePath] != null) {
                            if (versionChanges[templatePath].newVersion <= versionChanges[templatePath].oldVersion) {
                                return {
                                    validator: "Workbook Metadata",
                                    filePath,
                                    passed: false,
                                    error: `New version (${versionChanges[templatePath].newVersion}) must be greater than old version (${versionChanges[templatePath].oldVersion}) for ${templatePath}`,
                                };
                            }
                        }
                    }
                }
            }
            catch {
                // Git-based version check failed — not fatal, just skip
                console.warn("  ⚠ Skipped version increment check (git diff unavailable)");
            }
        }
        return { validator: "Workbook Metadata", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "Workbook Metadata", filePath, passed: false, error: msg };
    }
}
/**
 * Extracts version changes from a git diff of WorkbooksMetadata.json.
 * Reimplemented from isVersionIncrementedOnModification.ts without GitHub dependency.
 */
function extractVersionChanges(diffLines) {
    let currentLine = 0;
    const workbookVersionChanges = {};
    const replaceQuotesRegex = /"/gi;
    while (currentLine < diffLines.length && diffLines[currentLine] !== "[") {
        currentLine++;
    }
    while (currentLine < diffLines.length && diffLines[currentLine] !== "]") {
        if (diffLines[currentLine] === "{") {
            let templateRelativePath = null;
            let newVersion = null;
            let oldVersion = null;
            currentLine++;
            while (currentLine < diffLines.length && diffLines[currentLine] !== "}") {
                const line = diffLines[currentLine];
                if (line.trim().startsWith("\"templateRelativePath\":")) {
                    templateRelativePath = line.split(":")[1].trim().replace(replaceQuotesRegex, "").replace(",", "");
                }
                if ((line.trim().startsWith("+") || line.trim().startsWith("-")) && line.includes("\"version\":")) {
                    const version = line.split(":")[1].trim().replace(replaceQuotesRegex, "").replace(",", "");
                    if (line.trim().startsWith("+")) {
                        newVersion = version;
                    }
                    else {
                        oldVersion = version;
                    }
                }
                currentLine++;
            }
            if (templateRelativePath && newVersion && oldVersion) {
                workbookVersionChanges[templateRelativePath] = { newVersion, oldVersion };
            }
        }
        currentLine++;
    }
    return workbookVersionChanges;
}
// ----- 10. Documents Link Validator -----
async function validateDocumentsLink(filePath, _fileKind) {
    try {
        const content = fs.readFileSync(filePath, "utf8");
        if (/(https:\/\/docs.microsoft.com|https:\/\/azure.microsoft.com)(\/[a-z]{2}-[a-z]{2})/i.test(content)) {
            return {
                validator: "Documents Link",
                filePath,
                passed: false,
                error: "Documentation links should not include locale codes (e.g., /en-us/)",
            };
        }
        return { validator: "Documents Link", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "Documents Link", filePath, passed: false, error: msg };
    }
}
// ----- 11. Solution Validator -----
async function validateSolution(filePath, _fileKind) {
    if (!filePath.endsWith("mainTemplate.json") && !filePath.endsWith("createUiDefinition.json")) {
        return {
            validator: "Solution",
            filePath,
            passed: true,
            skipped: true,
            skipReason: "Not mainTemplate.json or createUiDefinition.json",
        };
    }
    try {
        IsValidSolutionDomainsVerticals(filePath);
        IsValidSupportObject(filePath);
        IsValidBrandingContent(filePath);
        IsValidSolutionID(filePath);
        return { validator: "Solution", filePath, passed: true };
    }
    catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        return { validator: "Solution", filePath, passed: false, error: msg };
    }
}
// ----- 12. ID Change Validator (Local Git-Based) -----
async function validateIdChange(filePath, fileKind) {
    if (fileKind !== "Modified") {
        return { validator: "ID Change", filePath, passed: true, skipped: true, skipReason: "Only checks modified files" };
    }
    const isXdrWorkbook = /(^|[\\/])XDR Workbooks[\\/]/.test(filePath);
    const isDetection = filePath.includes("Detections") || filePath.includes("Analytic Rules");
    if (!isDetection && !isXdrWorkbook) {
        return { validator: "ID Change", filePath, passed: true, skipped: true, skipReason: "Not a detection or XDR workbook file" };
    }
    try {
        const skipFilePath = path.join(toolkitRoot, ".script/tests/idChangeValidatorTest/SkipIdValidationsTemplates.json");
        const skipIds = fs.existsSync(skipFilePath) ? JSON.parse(fs.readFileSync(skipFilePath, "utf8")) : [];
        const guidRegex = "(?:xdr-)?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}";
        const templateIdRegex = isXdrWorkbook
            ? `("(?:contentId|instanceId)"\\s*:\\s*"${guidRegex}"(.|\\n)*){2}`
            : `(id:\\s*['"]?${guidRegex}['"]?(.|\\n)*){2}`;
        const targetBranch = detectDefaultBranch();
        const mergeBase = execFileSync("git", ["merge-base", targetBranch, "HEAD"], { encoding: "utf8" }).trim();
        const fullPath = path.resolve(process.cwd(), filePath);
        if (!isPathWithin(process.cwd(), fullPath)) {
            return {
                validator: "ID Change",
                filePath,
                passed: false,
                error: "File path resolves outside the repository root",
            };
        }
        const diffSummary = execFileSync("git", ["diff", mergeBase, "HEAD", "--", fullPath], { encoding: "utf8" });
        if (/^new file mode /m.test(diffSummary) || diffSummary.includes("--- /dev/null")) {
            return { validator: "ID Change", filePath, passed: true, skipped: true, skipReason: "New file in branch" };
        }
        const isXdrDetection = /(^|[\\/])XDR Detections[\\/]/.test(filePath);
        if (isXdrDetection) {
            const removedPropId = diffSummary.match(/^-[ \t]+id:\s*['"]?(xdr-[0-9a-fA-F-]{36}|[0-9a-fA-F-]{36})['"]?/m);
            const addedPropId = diffSummary.match(/^\+[ \t]+id:\s*['"]?(xdr-[0-9a-fA-F-]{36}|[0-9a-fA-F-]{36})['"]?/m);
            if (removedPropId && addedPropId && removedPropId[1] !== addedPropId[1]) {
                if (skipIds.indexOf(addedPropId[1]) > -1) {
                    return { validator: "ID Change", filePath, passed: true, skipped: true, skipReason: "ID in skip list" };
                }
                return {
                    validator: "ID Change",
                    filePath,
                    passed: false,
                    error: `Template ID changed from ${removedPropId[1]} to ${addedPropId[1]} — IDs must not be modified`,
                };
            }
            return { validator: "ID Change", filePath, passed: true };
        }
        const idPosition = diffSummary.search(new RegExp(templateIdRegex));
        if (idPosition > 0) {
            const regex = /(?:xdr-)?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/g;
            let match;
            let oldId = "";
            let newId = "";
            while ((match = regex.exec(diffSummary)) !== null) {
                if (oldId === "") {
                    oldId = match[0];
                }
                else {
                    newId = match[0];
                }
            }
            if (skipIds.indexOf(newId) > -1) {
                return { validator: "ID Change", filePath, passed: true, skipped: true, skipReason: "ID in skip list" };
            }
            if (oldId !== newId) {
                return {
                    validator: "ID Change",
                    filePath,
                    passed: false,
                    error: `Template ID changed from ${oldId} to ${newId} — IDs must not be modified`,
                };
            }
        }
        return { validator: "ID Change", filePath, passed: true };
    }
    catch (e) {
        const msg = (e instanceof Error ? e.message : String(e)).replace(/[\r\n]+/g, " ").trim();
        // If git diff fails (e.g., in --path mode), skip gracefully
        return { validator: "ID Change", filePath, passed: true, skipped: true, skipReason: `Git diff unavailable: ${msg}` };
    }
}
// ----- 12b. XDR Detections & XDR Workbooks Validators (Python subprocess) -----
function resolvePythonExecutable() {
    const candidates = [
        process.env.PYTHON_EXECUTABLE,
        "/opt/anaconda3/bin/python3.12",
        "python3",
        "python",
    ].filter((c) => Boolean(c && c.trim()));
    for (const candidate of candidates) {
        try {
            execFileSync(candidate, ["--version"], { encoding: "utf8", stdio: "pipe" });
            return candidate;
        }
        catch {
            // try next
        }
    }
    return null;
}
async function runXdrContentValidators(files, options, runDetections, runWorkbooks) {
    const results = [];
    if (!runDetections && !runWorkbooks) {
        return results;
    }
    const scriptPath = path.join(toolkitRoot, ".script/local-validation/validate-xdr-content.py");
    if (!fs.existsSync(scriptPath)) {
        if (runDetections) {
            results.push({
                validator: "XDR Detection",
                filePath: scriptPath,
                passed: false,
                error: `XDR validation script not found: ${scriptPath}`,
            });
        }
        if (runWorkbooks) {
            results.push({
                validator: "XDR Workbook",
                filePath: scriptPath,
                passed: false,
                error: `XDR validation script not found: ${scriptPath}`,
            });
        }
        return results;
    }
    const pythonExe = resolvePythonExecutable();
    if (!pythonExe) {
        const reason = "Python 3 interpreter not available to run XDR content validator";
        if (runDetections) {
            results.push({
                validator: "XDR Detection",
                filePath: scriptPath,
                passed: true,
                skipped: true,
                skipReason: reason,
            });
        }
        if (runWorkbooks) {
            results.push({
                validator: "XDR Workbook",
                filePath: scriptPath,
                passed: true,
                skipped: true,
                skipReason: reason,
            });
        }
        return results;
    }
    const family = runDetections && runWorkbooks ? "all" : runDetections ? "detections" : "workbooks";
    const args = [
        scriptPath,
        "--toolkit-root",
        toolkitRoot,
        "--content-root",
        contentRoot,
        "--family",
        family,
    ];
    if (options.mode === "path" && options.targetPath) {
        args.push("--solution-path", options.targetPath);
    }
    else {
        args.push("--files", ...files.map(f => f.filePath));
    }
    let rawOutput = "";
    try {
        rawOutput = execFileSync(pythonExe, args, {
            encoding: "utf8",
            stdio: ["ignore", "pipe", "pipe"],
            timeout: 120000,
        });
    }
    catch (e) {
        const errObj = e;
        if (errObj && typeof errObj.stdout === "string" && errObj.stdout.trim().startsWith("{")) {
            rawOutput = errObj.stdout;
        }
        else {
            const msg = (errObj?.stderr || errObj?.message || String(e)).trim();
            if (runDetections) {
                results.push({
                    validator: "XDR Detection",
                    filePath: options.targetPath || "Solutions",
                    passed: false,
                    error: `XDR content validator process failed: ${msg}`,
                });
            }
            if (runWorkbooks) {
                results.push({
                    validator: "XDR Workbook",
                    filePath: options.targetPath || "Solutions",
                    passed: false,
                    error: `XDR content validator process failed: ${msg}`,
                });
            }
            return results;
        }
    }
    const parsed = JSON.parse(rawOutput);
    if (Array.isArray(parsed.results)) {
        for (const item of parsed.results) {
            results.push({
                validator: String(item.validator),
                filePath: String(item.filePath),
                passed: Boolean(item.passed),
                error: item.error ? String(item.error) : undefined,
                skipped: Boolean(item.skipped),
                skipReason: item.skipReason ? String(item.skipReason) : undefined,
            });
        }
    }
    return results;
}
// ----- 13–15. .NET Validators (subprocess invocation) -----
async function runDotNetValidator(projectPath, validatorName, selectedContentRoot, requiredRuntimeRegex, requiredRuntimeLabel) {
    const results = [];
    try {
        if (!fs.existsSync(projectPath)) {
            results.push({
                validator: validatorName,
                filePath: projectPath,
                passed: true,
                skipped: true,
                skipReason: "Project file not found",
            });
            return results;
        }
        if (requiredRuntimeRegex) {
            const runtimesOut = execSync("dotnet --list-runtimes", { encoding: "utf8", stdio: "pipe" });
            if (!requiredRuntimeRegex.test(runtimesOut)) {
                results.push({
                    validator: validatorName,
                    filePath: projectPath,
                    passed: true,
                    skipped: true,
                    skipReason: `${requiredRuntimeLabel || "Required .NET runtime"} not installed`,
                });
                return results;
            }
        }
        const testOut = execFileSync("dotnet", ["test", projectPath, "--configuration", "Release", "--verbosity", "minimal"], {
            encoding: "utf8",
            stdio: "pipe",
            timeout: 300000, // 5 minute timeout
            env: {
                ...process.env,
                SENTINEL_VALIDATION_CONTENT_ROOT: selectedContentRoot,
            },
        });
        if (/Total:\s*0\b|No test is available/i.test(testOut)) {
            results.push({
                validator: validatorName,
                filePath: projectPath,
                passed: true,
                skipped: true,
                skipReason: "No applicable tests executed by .NET test runner",
            });
            return results;
        }
        results.push({ validator: validatorName, filePath: projectPath, passed: true });
    }
    catch (e) {
        const msg = e instanceof Error ? e.stdout || e.message : String(e);
        results.push({ validator: validatorName, filePath: projectPath, passed: false, error: msg });
    }
    return results;
}
// ----- 16. ARM-TTK Validator (PowerShell subprocess) -----
async function runArmTtkValidator(files) {
    const results = [];
    const armFiles = files.filter(f => (f.filePath.endsWith("mainTemplate.json") || f.filePath.endsWith("createUiDefinition.json"))
        && f.filePath.startsWith("Solutions/"));
    if (armFiles.length === 0) {
        results.push({
            validator: "ARM-TTK",
            filePath: "Solutions",
            passed: true,
            skipped: true,
            skipReason: "No mainTemplate.json or createUiDefinition.json found in scope",
        });
        return results;
    }
    const legacyScriptPath = path.join(toolkitRoot, ".script/package-automation/arm-ttk-tests.ps1");
    const localScriptPath = path.join(toolkitRoot, ".script/local-validation/run-arm-ttk.ps1");
    const scriptPath = fs.existsSync(legacyScriptPath) ? legacyScriptPath : localScriptPath;
    if (!fs.existsSync(scriptPath)) {
        results.push({
            validator: "ARM-TTK",
            filePath: scriptPath,
            passed: true,
            skipped: true,
            skipReason: "ARM-TTK script not found",
        });
        return results;
    }
    for (const file of armFiles) {
        try {
            const resolvedFilePath = path.resolve(contentRoot, file.filePath);
            if (!isPathWithin(contentRoot, resolvedFilePath)) {
                results.push({
                    validator: "ARM-TTK",
                    filePath: file.filePath,
                    passed: false,
                    error: "File path resolves outside the selected content root",
                });
                continue;
            }
            const pwshArgs = scriptPath === localScriptPath
                ? ["-NoProfile", "-File", scriptPath, "-PackagePath", path.dirname(resolvedFilePath)]
                : ["-NoProfile", "-File", scriptPath, "-FilePath", file.filePath];
            execFileSync("pwsh", pwshArgs, {
                encoding: "utf8",
                stdio: "pipe",
                timeout: 120000,
            });
            results.push({ validator: "ARM-TTK", filePath: file.filePath, passed: true });
        }
        catch (e) {
            const msg = e instanceof Error ? e.message : String(e);
            results.push({ validator: "ARM-TTK", filePath: file.filePath, passed: false, error: msg });
        }
    }
    return results;
}
// ============================================================================
// VALIDATOR REGISTRY — maps validators to file routing rules
// ============================================================================
const VALIDATORS = [
    {
        name: "JSON Syntax",
        id: "json",
        fileExtensions: [".json"],
        fileKinds: ["Added", "Modified"],
        validate: validateJsonSyntax,
    },
    {
        name: "YAML Syntax",
        id: "yaml",
        fileExtensions: [".yaml", ".yml"],
        fileKinds: ["Added", "Modified"],
        validate: validateYamlSyntax,
    },
    {
        name: "Data Connector",
        id: "data-connector",
        fileExtensions: [".json"],
        filePathPrefixes: ["DataConnectors/", "Solutions/"],
        fileKinds: ["Added", "Modified"],
        validate: validateDataConnector,
    },
    {
        name: "Content (MS Branding)",
        id: "content",
        fileExtensions: [".json"],
        fileKinds: ["Added", "Modified"],
        validate: validateContent,
    },
    {
        name: "Logo",
        id: "logo",
        filePathPrefixes: ["Logos/", "Solutions/", "Workbooks/Images/Logos"],
        fileKinds: ["Added", "Modified"],
        validate: validateLogo,
    },
    {
        name: "Sample Data",
        id: "sample-data",
        fileExtensions: [".json"],
        filePathPrefixes: ["Sample Data/"],
        fileKinds: ["Added", "Modified"],
        validate: validateSampleData,
    },
    {
        name: "Playbook",
        id: "playbook",
        fileExtensions: [".json"],
        filePathPrefixes: ["Playbooks/", "Solutions/"],
        fileKinds: ["Modified"],
        validate: validatePlaybook,
    },
    {
        name: "Workbook Template",
        id: "workbook-template",
        fileExtensions: [".json"],
        filePathPrefixes: ["Workbooks/", "Solutions/"],
        fileKinds: ["Added", "Modified"],
        validate: validateWorkbookTemplate,
    },
    {
        name: "Workbook Metadata",
        id: "workbook-metadata",
        fileExtensions: ["WorkbooksMetadata.json"],
        filePathPrefixes: ["Workbooks/"],
        fileKinds: ["Modified"],
        validate: validateWorkbookMetadata,
    },
    {
        name: "Documents Link",
        id: "documents-link",
        fileKinds: ["Added", "Modified"],
        validate: validateDocumentsLink,
    },
    {
        name: "Solution",
        id: "solution",
        fileExtensions: [".json"],
        filePathPrefixes: ["Solutions/"],
        fileKinds: ["Added", "Modified"],
        validate: validateSolution,
    },
    {
        name: "ID Change",
        id: "id-change",
        fileExtensions: [".yaml", ".yml", ".json"],
        filePathPrefixes: ["Detections/", "Solutions/"],
        fileKinds: ["Modified"],
        validate: validateIdChange,
    },
];
// ============================================================================
// ORCHESTRATOR
// ============================================================================
/**
 * Routes a file to all applicable validators and collects results.
 */
async function validateFile(file, validators) {
    const results = [];
    const fileKind = statusToKind(file.status);
    for (const validator of validators) {
        // Check file kind
        if (!validator.fileKinds.includes(fileKind) && file.status !== "A") {
            // In --path/--files mode (status="A"), run all validators regardless of kind
            continue;
        }
        // Check file extensions
        if (validator.fileExtensions && validator.fileExtensions.length > 0) {
            if (!validator.fileExtensions.some(ext => file.filePath.endsWith(ext))) {
                continue;
            }
        }
        // Check file path prefixes
        if (validator.filePathPrefixes && validator.filePathPrefixes.length > 0) {
            if (!validator.filePathPrefixes.some(prefix => file.filePath.startsWith(prefix))) {
                continue;
            }
        }
        // Skip .script/tests/ files
        if (file.filePath.startsWith(".script/tests/")) {
            continue;
        }
        const result = await validator.validate(file.filePath, fileKind);
        results.push(result);
    }
    return results;
}
// ============================================================================
// REPORTING
// ============================================================================
function printReport(results, verbose, jsonOutput, jsonFilePath) {
    if (jsonOutput) {
        const report = JSON.stringify({
            summary: {
                total: results.length,
                passed: results.filter(r => r.passed && !r.skipped).length,
                failed: results.filter(r => !r.passed && !r.skipped).length,
                skipped: results.filter(r => r.skipped).length,
            },
            results,
        }, null, 2);
        if (jsonFilePath) {
            fs.writeFileSync(jsonFilePath, report, "utf8");
            console.log(`Complete TypeScript validation results written to ${jsonFilePath}`);
        }
        else {
            console.log(report);
        }
        return;
    }
    const passed = results.filter(r => r.passed && !r.skipped);
    const failed = results.filter(r => !r.passed && !r.skipped);
    const skipped = results.filter(r => r.skipped);
    console.log("\n" + "=".repeat(70));
    console.log("  LOCAL VALIDATION REPORT");
    console.log("=".repeat(70));
    // Group by validator
    const byValidator = new Map();
    for (const r of results) {
        const existing = byValidator.get(r.validator) || [];
        existing.push(r);
        byValidator.set(r.validator, existing);
    }
    for (const [validatorName, validatorResults] of byValidator) {
        const failures = validatorResults.filter(r => !r.passed && !r.skipped);
        const passes = validatorResults.filter(r => r.passed && !r.skipped);
        const skips = validatorResults.filter(r => r.skipped);
        if (failures.length > 0) {
            console.log(`\n❌ ${validatorName}  (${failures.length} failed, ${passes.length} passed, ${skips.length} skipped)`);
            for (const f of failures) {
                console.log(`   FAIL  ${f.filePath}`);
                if (f.error) {
                    console.log(`         ${f.error}`);
                }
            }
        }
        else if (passes.length === 0 && skips.length > 0) {
            console.log(`\n⏭ ${validatorName}  (${skips.length} skipped)`);
        }
        else {
            console.log(`\n✅ ${validatorName}  (${passes.length} passed, ${skips.length} skipped)`);
        }
        if (verbose) {
            for (const p of passes) {
                console.log(`   PASS  ${p.filePath}`);
            }
            for (const s of skips) {
                console.log(`   SKIP  ${s.filePath}${s.skipReason ? ` (${s.skipReason})` : ""}`);
            }
        }
    }
    console.log("\n" + "-".repeat(70));
    console.log(`  TOTAL: ${results.length} checks  |  ✅ ${passed.length} passed  |  ❌ ${failed.length} failed  |  ⏭ ${skipped.length} skipped`);
    console.log("-".repeat(70) + "\n");
}
// ============================================================================
// MAIN
// ============================================================================
async function main() {
    const options = parseArgs(process.argv);
    if (options.repositoryRoot) {
        const repositoryRoot = path.resolve(options.repositoryRoot);
        const realRepositoryRoot = fs.existsSync(repositoryRoot) ? fs.realpathSync(repositoryRoot) : repositoryRoot;
        const solutionsPath = path.join(repositoryRoot, "Solutions");
        if (!fs.existsSync(repositoryRoot) || !fs.statSync(repositoryRoot).isDirectory()
            || path.relative(repositoryRoot, realRepositoryRoot) !== ""
            || !fs.existsSync(solutionsPath)
            || !fs.lstatSync(solutionsPath).isDirectory()
            || fs.lstatSync(solutionsPath).isSymbolicLink()) {
            console.error(`Error: --repository-root must name a repository directory containing Solutions/: ${options.repositoryRoot}`);
            process.exit(2);
        }
        contentRoot = repositoryRoot;
    }
    if (options.jsonFilePath) {
        options.jsonFilePath = path.resolve(invocationDirectory, options.jsonFilePath);
    }
    // Keep tooling requirements rooted in the checkout that contains this runner.
    if (!fs.existsSync(path.join(toolkitRoot, ".script")) || !fs.existsSync(path.join(toolkitRoot, "package.json"))) {
        console.error("Error: Please run this script from the Azure Sentinel repository root directory.");
        process.exit(2);
    }
    process.chdir(contentRoot);
    // --- File Discovery ---
    let files;
    let modeDescription;
    switch (options.mode) {
        case "diff":
            const branch = options.targetBranch || detectDefaultBranch();
            files = getChangedFiles(branch);
            modeDescription = `diff against '${branch}'`;
            break;
        case "path":
            files = getFilesInPath(options.targetPath);
            modeDescription = `all files in '${options.targetPath}'`;
            break;
        case "files":
            files = getExplicitFiles(options.files);
            modeDescription = `${files.length} specified file(s)`;
            break;
        case "auto":
        default:
            const defaultBranch = detectDefaultBranch();
            files = getChangedFiles(defaultBranch);
            modeDescription = `auto-detected diff against '${defaultBranch}'`;
            break;
    }
    // Filter out deleted files
    files = files.filter(f => f.status !== "D");
    if (!options.jsonOutput) {
        console.log(`\n🔍 Mode: ${modeDescription}`);
        console.log(`📁 Files to validate: ${files.length}`);
    }
    if (files.length === 0) {
        if (!options.jsonOutput) {
            console.log("No files to validate. Exiting.");
        }
        else {
            printReport([], options.verbose, options.jsonOutput, options.jsonFilePath);
        }
        process.exit(0);
    }
    // --- Filter Validators ---
    let activeValidators = [...VALIDATORS];
    if (options.only.length > 0) {
        activeValidators = activeValidators.filter(v => options.only.includes(v.id));
    }
    if (options.skip.length > 0) {
        activeValidators = activeValidators.filter(v => !options.skip.includes(v.id));
    }
    const shouldRunXdrDetection = (options.only.length === 0 || options.only.includes("xdr-detection"))
        && !options.skip.includes("xdr-detection");
    const shouldRunXdrWorkbook = (options.only.length === 0 || options.only.includes("xdr-workbook"))
        && !options.skip.includes("xdr-workbook");
    if (!options.jsonOutput) {
        const activeIds = [
            ...activeValidators.map(v => v.id),
            ...(shouldRunXdrDetection ? ["xdr-detection"] : []),
            ...(shouldRunXdrWorkbook ? ["xdr-workbook"] : []),
        ];
        console.log(`🔧 Active validators: ${activeIds.join(", ")}`);
    }
    // --- Run Validations ---
    const allResults = [];
    for (const file of files) {
        // Ensure file exists before validating
        if (!fs.existsSync(file.filePath)) {
            continue;
        }
        const fileResults = await validateFile(file, activeValidators);
        allResults.push(...fileResults);
    }
    // --- Run XDR Detections & XDR Workbooks Validators ---
    if (shouldRunXdrDetection || shouldRunXdrWorkbook) {
        const xdrResults = await runXdrContentValidators(files, options, shouldRunXdrDetection, shouldRunXdrWorkbook);
        allResults.push(...xdrResults);
    }
    // --- Run .NET Validators (if not skipped) ---
    const dotnetValidators = [
        {
            id: "kql",
            name: "KQL Validation",
            project: path.join(toolkitRoot, ".script/tests/KqlvalidationsTests/Kqlvalidations.Tests.csproj"),
            runtimeRegex: /Microsoft\.NETCore\.App 8\./,
            runtimeLabel: ".NET 8.0",
        },
        {
            id: "detection-schema",
            name: "Detection Template Schema",
            project: path.join(toolkitRoot, ".script/tests/detectionTemplateSchemaValidation/DetectionTemplateSchemaValidation.Tests.csproj"),
            runtimeRegex: /Microsoft\.NETCore\.App 3\.1\./,
            runtimeLabel: ".NET Core 3.1",
        },
        {
            id: "non-ascii",
            name: "Non-ASCII",
            project: path.join(toolkitRoot, ".script/tests/NonAsciiValidationsTests/NonAsciiValidations.Tests.csproj"),
            runtimeRegex: /Microsoft\.NETCore\.App 3\.1\./,
            runtimeLabel: ".NET Core 3.1",
        },
    ];
    for (const dotnetValidator of dotnetValidators) {
        const shouldRun = (options.only.length === 0 || options.only.includes(dotnetValidator.id))
            && !options.skip.includes(dotnetValidator.id);
        if (shouldRun) {
            if (options.mode === "path") {
                allResults.push({
                    validator: dotnetValidator.name,
                    filePath: dotnetValidator.project,
                    passed: true,
                    skipped: true,
                    skipReason: "The standalone --path runner cannot safely scope this repo-wide .NET test project; use build-and-validate.ps1 for scoped solution validation",
                });
                continue;
            }
            let dotnetAvailable = false;
            try {
                execSync("dotnet --version", { encoding: "utf8", stdio: "pipe" });
                dotnetAvailable = true;
            }
            catch (e) {
                const message = e instanceof Error ? e.message : String(e);
                allResults.push({
                    validator: dotnetValidator.name,
                    filePath: dotnetValidator.project,
                    passed: true,
                    skipped: true,
                    skipReason: `.NET SDK command is unavailable: ${message}`,
                });
            }
            if (!dotnetAvailable)
                continue;
            const dotnetResults = await runDotNetValidator(dotnetValidator.project, dotnetValidator.name, contentRoot, dotnetValidator.runtimeRegex, dotnetValidator.runtimeLabel);
            for (const result of dotnetResults) {
                if (!result.passed && result.error && result.error.includes("GitHub App ID")) {
                    result.passed = true;
                    result.skipped = true;
                    result.skipReason = "Requires GitHub App credentials (only available in CI) — skip locally with --skip " + dotnetValidator.id;
                    result.error = undefined;
                }
            }
            allResults.push(...dotnetResults);
        }
    }
    // --- Run ARM-TTK (if not skipped) ---
    const shouldRunArmTtk = (options.only.length === 0 || options.only.includes("arm-ttk"))
        && !options.skip.includes("arm-ttk");
    if (shouldRunArmTtk) {
        let powershellAvailable = false;
        try {
            execSync("pwsh --version", { encoding: "utf8", stdio: "pipe" });
            powershellAvailable = true;
        }
        catch (e) {
            const message = e instanceof Error ? e.message : String(e);
            allResults.push({
                validator: "ARM-TTK",
                filePath: "pwsh",
                passed: true,
                skipped: true,
                skipReason: `PowerShell command is unavailable: ${message}`,
            });
        }
        if (powershellAvailable) {
            const armTtkResults = await runArmTtkValidator(files);
            allResults.push(...armTtkResults);
        }
    }
    // --- Report ---
    printReport(allResults, options.verbose, options.jsonOutput, options.jsonFilePath);
    // --- Exit Code ---
    const hasFailures = allResults.some(r => !r.passed && !r.skipped);
    process.exit(hasFailures ? 1 : 0);
}
// Run
main().catch(e => {
    console.error("Fatal error:", e);
    process.exit(2);
});
//# sourceMappingURL=validate.js.map