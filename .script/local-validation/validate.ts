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
 *   --help                Show this help message
 * 
 * Exit codes:
 *   0 = All validations passed
 *   1 = One or more validations failed
 *   2 = Configuration/usage error
 * 
 * Requirements:
 *   - Run from the repository root directory
 *   - Node.js 16+ with npm dependencies installed (npm install)
 *   - TypeScript compiled (npm run tsc)
 *   - For .NET validators: .NET SDK 6.0+ installed
 *   - For ARM-TTK: PowerShell with ARM-TTK module
 */

import { execSync } from "child_process";
import fs from "fs";
import path from "path";

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


// ============================================================================
// TYPES
// ============================================================================

interface ValidationResult {
  validator: string;
  filePath: string;
  passed: boolean;
  error?: string;
  skipped?: boolean;
  skipReason?: string;
}

interface ValidatorDefinition {
  name: string;
  id: string;
  fileExtensions?: string[];
  filePathPrefixes?: string[];
  fileKinds: string[];       // "Added", "Modified", "Renamed", etc.
  validate: (filePath: string, fileKind: string) => Promise<ValidationResult>;
}

interface ChangedFile {
  status: string;   // "A" (Added), "M" (Modified), "D" (Deleted), "R" (Renamed)
  filePath: string;
}

interface CLIOptions {
  mode: "diff" | "path" | "files" | "auto";
  targetBranch?: string;
  targetPath?: string;
  files?: string[];
  skip: string[];
  only: string[];
  verbose: boolean;
  jsonOutput: boolean;
}


// ============================================================================
// CLI ARGUMENT PARSING
// ============================================================================

function printHelp(): void {
  const lines = fs.readFileSync(new URL(import.meta.url), "utf8").split("\n");
  const helpLines: string[] = [];
  let inHeader = false;
  for (const line of lines) {
    if (line.startsWith("/**")) { inHeader = true; continue; }
    if (inHeader && line.includes("*/")) { break; }
    if (inHeader && line.startsWith(" *")) {
      helpLines.push(line.replace(/^ \* ?/, ""));
    }
  }
  console.log(helpLines.join("\n"));
}

function parseArgs(argv: string[]): CLIOptions {
  const args = argv.slice(2); // Skip node and script path
  const options: CLIOptions = {
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
        } else {
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
function detectDefaultBranch(): string {
  try {
    const branches = execSync("git branch -a", { encoding: "utf8" });
    if (branches.includes("remotes/origin/main") || branches.includes("* main")) {
      return "main";
    }
    if (branches.includes("remotes/origin/master") || branches.includes("* master")) {
      return "master";
    }
  } catch {
    // Ignore errors
  }
  return "main"; // Default fallback
}

/**
 * Gets files changed between current HEAD and the target branch using git diff.
 * Returns files with their change status (Added, Modified, etc.).
 */
function getChangedFiles(targetBranch: string): ChangedFile[] {
  try {
    // Make sure we have the target branch ref
    try {
      execSync(`git rev-parse --verify ${targetBranch}`, { encoding: "utf8", stdio: "pipe" });
    } catch {
      // Try fetching it
      try {
        execSync(`git fetch origin ${targetBranch}:${targetBranch} --no-tags --depth=1`, { encoding: "utf8", stdio: "pipe" });
      } catch {
        console.warn(`Warning: Could not find or fetch branch '${targetBranch}'. Trying origin/${targetBranch}...`);
        targetBranch = `origin/${targetBranch}`;
      }
    }

    const mergeBase = execSync(`git merge-base ${targetBranch} HEAD`, { encoding: "utf8" }).trim();
    const diffOutput = execSync(`git diff --name-status ${mergeBase} HEAD`, { encoding: "utf8" });

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
  } catch (e: unknown) {
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
function getFilesInPath(dirPath: string): ChangedFile[] {
  const results: ChangedFile[] = [];

  function walk(dir: string): void {
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
        walk(fullPath);
      } else {
        // Normalize to forward slashes (repo-relative paths)
        const relativePath = path.relative(process.cwd(), fullPath).replace(/\\/g, "/");
        results.push({ status: "A", filePath: relativePath }); // Treat all as "Added" for full validation
      }
    }
  }

  // Resolve relative to cwd
  const resolvedPath = path.resolve(process.cwd(), dirPath);
  walk(resolvedPath);
  return results;
}

/**
 * Gets files from explicit file list.
 */
function getExplicitFiles(filePaths: string[]): ChangedFile[] {
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
function statusToKind(status: string): string {
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
async function validateJsonSyntax(filePath: string, _fileKind: string): Promise<ValidationResult> {
  try {
    JSON.parse(fs.readFileSync(filePath, "utf8"));
    return { validator: "JSON Syntax", filePath, passed: true };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "JSON Syntax", filePath, passed: false, error: msg };
  }
}


// ----- 2. YAML Syntax Validator -----
async function validateYamlSyntax(filePath: string, _fileKind: string): Promise<ValidationResult> {
  try {
    // Dynamic import for js-yaml since it may not be typed
    const yamlModule = await import("js-yaml");
    const yamlLoad = yamlModule.default?.safeLoad || yamlModule.safeLoad;
    yamlLoad(fs.readFileSync(filePath, "utf8"));
    return { validator: "YAML Syntax", filePath, passed: true };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "YAML Syntax", filePath, passed: false, error: msg };
  }
}


// ----- 3. Data Connector Validator -----
// Copied from dataConnectorValidator.ts — these are module-private functions we can't import

function isPotentialConnectorJson(jsonFile: Record<string, unknown>): boolean {
  const dataTypes = jsonFile.dataTypes as unknown[];
  return (typeof jsonFile.id !== "undefined" &&
          typeof jsonFile.connectivityCriterias !== "undefined" &&
          Array.isArray(dataTypes) && dataTypes.length > 0);
}

function getConnectorCategory(dataTypes: { name: string }[], instructionSteps: unknown[]): string {
  const name = dataTypes[0].name;
  if (name.includes("CommonSecurityLog")) return ConnectorCategory.CEF;
  if (name.includes("Syslog")) return ConnectorCategory.SysLog;
  if (name.includes("SecurityAlert(ASC)")) return ConnectorCategory.SecurityAlertASC;
  if (name.includes("ThreatIntelligenceIndicator")) return ConnectorCategory.ThreatIntelligenceIndicator;
  if (name.includes("PowerBIActivity")) return ConnectorCategory.PowerBIActivity;
  if (name.includes("MicrosoftPurviewInformationProtection")) return ConnectorCategory.MicrosoftPurviewInformationProtection;
  if (name.includes("AzureActivity")) return ConnectorCategory.AzureActivity;
  if (name.includes("Event")) return ConnectorCategory.Event;
  if (name.includes("SecurityAlert(OATP)")) return ConnectorCategory.SecurityAlertOATP;
  if (name.includes("AzureDevOpsAuditing")) return ConnectorCategory.AzureDevOpsAuditing;
  if (name.includes("AzureDiagnostics")) return ConnectorCategory.AzureDiagnostics;
  if (name.endsWith("_CL")) {
    if (JSON.stringify(instructionSteps).includes("[Deploy To Azure]")) return ConnectorCategory.AzureFunction;
    if ((name.includes("meraki") || name.includes("vCenter")) &&
        JSON.stringify(instructionSteps).includes("\"type\":\"InstallAgent\"")) return ConnectorCategory.SysLog;
    return ConnectorCategory.RestAPI;
  }
  if (name.includes("Dynamics365Activity")) return ConnectorCategory.Dynamics365Activity;
  if (name.includes("CrowdstrikeReplicatorV2")) return ConnectorCategory.CrowdstrikeReplicatorV2;
  if (name.includes("BloodHoundEnterprise")) return ConnectorCategory.BloodHoundEnterprise;
  if (name.includes("AwsS3")) return ConnectorCategory.AwsS3;
  if (name.includes("AWS")) return ConnectorCategory.AWS;
  if (name.includes("Corelight")) return ConnectorCategory.Corelight;
  if (name.includes("SigninLogs")) return ConnectorCategory.AzureActiveDirectory;
  if (name.includes("corelight_bacnet")) return ConnectorCategory.CorelightConnectorExporter;
  if (name.includes("SecurityIncident")) return ConnectorCategory.CybleThreatIntel;
  if (name.includes("IndicatorsOfCompromise")) return ConnectorCategory.CrowdStrikeFalconIOC;
  if (name.includes("WizIssues")) return ConnectorCategory.Wiz;
  if (name.includes("vectra_isession")) return ConnectorCategory.VectraStreamAma;
  return "";
}

async function validateDataConnector(filePath: string, _fileKind: string): Promise<ValidationResult> {
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
    const schemaPath = `.script/utils/schemas/${connectorCategory}_ConnectorSchema.json`;

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
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "Data Connector", filePath, passed: false, error: msg };
  }
}


// ----- 4. Content Validator (MS Branding) -----
async function validateContent(filePath: string, _fileKind: string): Promise<ValidationResult> {
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

    const jsonTagObj = JSON.parse(fs.readFileSync("./.script/validate-tag.json", "utf8"));
    let tagName = "";

    if (jsonTagObj.hasOwnProperty("createUiDefinition") && filePath.includes("createUiDefinition")) {
      tagName = jsonTagObj.createUiDefinition;
    } else if (hasDataFolder && jsonTagObj.hasOwnProperty("data")) {
      tagName = jsonTagObj.data;
    } else if (hasDataConnectorFolder && jsonTagObj.hasOwnProperty("dataConnectors")) {
      tagName = jsonTagObj.dataConnectors;
    }

    if (tagName) {
      const fileContentObj = JSON.parse(fs.readFileSync(filePath, "utf8"));
      let tagContent: string | undefined;

      if (filePath.includes("createUiDefinition.json")) {
        tagContent = fileContentObj?.parameters?.config?.basics?.[tagName]
                  || fileContentObj?.parameters?.config?.basics?.[tagName.charAt(0).toUpperCase() + tagName.slice(1)];
      } else {
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
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "Content (MS Branding)", filePath, passed: false, error: msg };
  }
}


// ----- 5. Logo Validator -----
async function validateLogo(filePath: string, _fileKind: string): Promise<ValidationResult> {
  try {
    if (filePath.includes("Logos") || filePath.includes("Data Connectors/Logo")
        || filePath.includes("Workbooks/Images/Logo") || filePath.includes("Workbooks/Images/Logos")) {
      isValidLogoImage(filePath);
      const svgContent = fs.readFileSync(filePath, { encoding: "utf8", flag: "r" });
      if (svgContent !== "undefined") {
        isValidLogoImageSVGContent(svgContent);
      }
    } else {
      return { validator: "Logo", filePath, passed: true, skipped: true, skipReason: "Not a logo path" };
    }
    return { validator: "Logo", filePath, passed: true };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "Logo", filePath, passed: false, error: msg };
  }
}


// ----- 6. Sample Data Validator -----
async function validateSampleData(filePath: string, _fileKind: string): Promise<ValidationResult> {
  try {
    const jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));
    isValidSampleData(jsonFile);
    return { validator: "Sample Data", filePath, passed: true };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "Sample Data", filePath, passed: false, error: msg };
  }
}


// ----- 7. Playbook Validator -----
async function validatePlaybook(filePath: string, _fileKind: string): Promise<ValidationResult> {
  try {
    const playbookARMTemplate = JSON.parse(fs.readFileSync(filePath, "utf8"));

    // Pre-check: only validate files that are actually ARM templates
    if (!playbookARMTemplate.$schema || !String(playbookARMTemplate.$schema).toLowerCase().includes("deploymenttemplate")) {
      return { validator: "Playbook", filePath, passed: true, skipped: true, skipReason: "Not an ARM template" };
    }

    // Validate ARM template schema
    const schemaPath = ".script/utils/schemas/ARM_DeploymentTemplateSchema.json";
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
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "Playbook", filePath, passed: false, error: msg };
  }
}


// ----- 8. Workbook Template Validator -----
async function validateWorkbookTemplate(filePath: string, _fileKind: string): Promise<ValidationResult> {
  try {
    // Skip WorkbooksMetadata.json — that's handled by the metadata validator
    if (filePath.endsWith("WorkbooksMetadata.json")) {
      return { validator: "Workbook Template", filePath, passed: true, skipped: true, skipReason: "Metadata file" };
    }

    const workbookTemplateString = fs.readFileSync(filePath, "utf8");
    const parsedWorkbookTemplate = JSON.parse(workbookTemplateString);

    // Check if it's actually a workbook JSON
    if (typeof parsedWorkbookTemplate.$schema !== "undefined"
        && String(parsedWorkbookTemplate.$schema).includes("schema/workbook.json")
        && typeof parsedWorkbookTemplate.version !== "undefined"
        && parsedWorkbookTemplate.version === "Notebook/1.0") {
      isFromTemplateIdNotSentinelUserWorkbook(parsedWorkbookTemplate);
      doesNotContainResourceInfo(workbookTemplateString);
    }

    return { validator: "Workbook Template", filePath, passed: true };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "Workbook Template", filePath, passed: false, error: msg };
  }
}


// ----- 9. Workbook Metadata Validator -----
async function validateWorkbookMetadata(filePath: string, _fileKind: string): Promise<ValidationResult> {
  try {
    const workbooksMetadata = JSON.parse(fs.readFileSync(filePath, "utf8"));
    const schemaPath = ".script/utils/schemas/workbooksMetadataSchema.json";
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
        const mergeBase = execSync(`git merge-base ${targetBranch} HEAD`, { encoding: "utf8" }).trim();
        const diffOutput = execSync(`git diff ${mergeBase} HEAD -W -- Workbooks/WorkbooksMetadata.json`, { encoding: "utf8" });

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
      } catch {
        // Git-based version check failed — not fatal, just skip
        console.warn("  ⚠ Skipped version increment check (git diff unavailable)");
      }
    }

    return { validator: "Workbook Metadata", filePath, passed: true };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "Workbook Metadata", filePath, passed: false, error: msg };
  }
}

/**
 * Extracts version changes from a git diff of WorkbooksMetadata.json.
 * Reimplemented from isVersionIncrementedOnModification.ts without GitHub dependency.
 */
function extractVersionChanges(diffLines: string[]): Record<string, { newVersion: string; oldVersion: string }> {
  let currentLine = 0;
  const workbookVersionChanges: Record<string, { newVersion: string; oldVersion: string }> = {};
  const replaceQuotesRegex = /"/gi;

  while (currentLine < diffLines.length && diffLines[currentLine] !== "[") {
    currentLine++;
  }

  while (currentLine < diffLines.length && diffLines[currentLine] !== "]") {
    if (diffLines[currentLine] === "{") {
      let templateRelativePath: string | null = null;
      let newVersion: string | null = null;
      let oldVersion: string | null = null;
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
          } else {
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
async function validateDocumentsLink(filePath: string, _fileKind: string): Promise<ValidationResult> {
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
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "Documents Link", filePath, passed: false, error: msg };
  }
}


// ----- 11. Solution Validator -----
async function validateSolution(filePath: string, _fileKind: string): Promise<ValidationResult> {
  try {
    IsValidSolutionDomainsVerticals(filePath);
    IsValidSupportObject(filePath);
    IsValidBrandingContent(filePath);
    IsValidSolutionID(filePath);
    return { validator: "Solution", filePath, passed: true };
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    return { validator: "Solution", filePath, passed: false, error: msg };
  }
}


// ----- 12. ID Change Validator (Local Git-Based) -----
async function validateIdChange(filePath: string, fileKind: string): Promise<ValidationResult> {
  if (fileKind !== "Modified") {
    return { validator: "ID Change", filePath, passed: true, skipped: true, skipReason: "Only checks modified files" };
  }

  if (!filePath.includes("Detections") && !filePath.includes("Analytic Rules")) {
    return { validator: "ID Change", filePath, passed: true, skipped: true, skipReason: "Not a detection file" };
  }

  try {
    const skipFilePath = ".script/tests/idChangeValidatorTest/SkipIdValidationsTemplates.json";
    const skipIds: string[] = fs.existsSync(skipFilePath) ? JSON.parse(fs.readFileSync(skipFilePath, "utf8")) : [];

    const guidRegex = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}";
    const templateIdRegex = `(id: ${guidRegex}(.|\n)*){2}`;

    const targetBranch = detectDefaultBranch();
    const mergeBase = execSync(`git merge-base ${targetBranch} HEAD`, { encoding: "utf8" }).trim();
    const fullPath = path.resolve(process.cwd(), filePath);
    const diffSummary = execSync(`git diff ${mergeBase} HEAD -- "${fullPath}"`, { encoding: "utf8" });

    const idPosition = diffSummary.search(new RegExp(templateIdRegex));
    if (idPosition > 0) {
      const regex = /[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/g;
      let match;
      let oldId = "";
      let newId = "";

      while ((match = regex.exec(diffSummary)) !== null) {
        if (oldId === "") {
          oldId = match[0];
        } else {
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
  } catch (e: unknown) {
    const msg = e instanceof Error ? e.message : String(e);
    // If git diff fails (e.g., in --path mode), skip gracefully
    return { validator: "ID Change", filePath, passed: true, skipped: true, skipReason: `Git diff unavailable: ${msg}` };
  }
}


// ----- 13–15. .NET Validators (subprocess invocation) -----
async function runDotNetValidator(projectPath: string, validatorName: string): Promise<ValidationResult[]> {
  const results: ValidationResult[] = [];
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

    execSync(`dotnet test "${projectPath}" --configuration Release --verbosity minimal`, {
      encoding: "utf8",
      stdio: "pipe",
      timeout: 300000, // 5 minute timeout
    });

    results.push({ validator: validatorName, filePath: projectPath, passed: true });
  } catch (e: unknown) {
    const msg = e instanceof Error ? (e as { stdout?: string }).stdout || e.message : String(e);
    results.push({ validator: validatorName, filePath: projectPath, passed: false, error: msg });
  }
  return results;
}


// ----- 16. ARM-TTK Validator (PowerShell subprocess) -----
async function runArmTtkValidator(files: ChangedFile[]): Promise<ValidationResult[]> {
  const results: ValidationResult[] = [];
  const armFiles = files.filter(f =>
    (f.filePath.endsWith("mainTemplate.json") || f.filePath.endsWith("createUiDefinition.json"))
    && f.filePath.startsWith("Solutions/")
  );

  if (armFiles.length === 0) {
    return results;
  }

  const scriptPath = ".script/package-automation/arm-ttk-tests.ps1";
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
      execSync(`pwsh -NoProfile -File "${scriptPath}" -FilePath "${file.filePath}"`, {
        encoding: "utf8",
        stdio: "pipe",
        timeout: 120000,
      });
      results.push({ validator: "ARM-TTK", filePath: file.filePath, passed: true });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      results.push({ validator: "ARM-TTK", filePath: file.filePath, passed: false, error: msg });
    }
  }

  return results;
}


// ============================================================================
// VALIDATOR REGISTRY — maps validators to file routing rules
// ============================================================================

const VALIDATORS: ValidatorDefinition[] = [
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
async function validateFile(
  file: ChangedFile,
  validators: ValidatorDefinition[],
): Promise<ValidationResult[]> {
  const results: ValidationResult[] = [];
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

function printReport(results: ValidationResult[], verbose: boolean, jsonOutput: boolean): void {
  if (jsonOutput) {
    console.log(JSON.stringify({
      summary: {
        total: results.length,
        passed: results.filter(r => r.passed && !r.skipped).length,
        failed: results.filter(r => !r.passed).length,
        skipped: results.filter(r => r.skipped).length,
      },
      results,
    }, null, 2));
    return;
  }

  const passed = results.filter(r => r.passed && !r.skipped);
  const failed = results.filter(r => !r.passed);
  const skipped = results.filter(r => r.skipped);

  console.log("\n" + "=".repeat(70));
  console.log("  LOCAL VALIDATION REPORT");
  console.log("=".repeat(70));

  // Group by validator
  const byValidator = new Map<string, ValidationResult[]>();
  for (const r of results) {
    const existing = byValidator.get(r.validator) || [];
    existing.push(r);
    byValidator.set(r.validator, existing);
  }

  for (const [validatorName, validatorResults] of byValidator) {
    const failures = validatorResults.filter(r => !r.passed);
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
    } else {
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

async function main(): Promise<void> {
  const options = parseArgs(process.argv);

  // Ensure we're in the repo root
  if (!fs.existsSync(".script") || !fs.existsSync("package.json")) {
    console.error("Error: Please run this script from the Azure Sentinel repository root directory.");
    process.exit(2);
  }

  // --- File Discovery ---
  let files: ChangedFile[];
  let modeDescription: string;

  switch (options.mode) {
    case "diff":
      const branch = options.targetBranch || detectDefaultBranch();
      files = getChangedFiles(branch);
      modeDescription = `diff against '${branch}'`;
      break;
    case "path":
      files = getFilesInPath(options.targetPath!);
      modeDescription = `all files in '${options.targetPath}'`;
      break;
    case "files":
      files = getExplicitFiles(options.files!);
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

  if (!options.jsonOutput) {
    console.log(`🔧 Active validators: ${activeValidators.map(v => v.id).join(", ")}`);
  }

  // --- Run Validations ---
  const allResults: ValidationResult[] = [];

  for (const file of files) {
    // Ensure file exists before validating
    if (!fs.existsSync(file.filePath)) {
      continue;
    }

    const fileResults = await validateFile(file, activeValidators);
    allResults.push(...fileResults);
  }

  // --- Run .NET Validators (if not skipped) ---
  const dotnetValidators = [
    { id: "kql", name: "KQL Validation", project: ".script/tests/KqlvalidationsTests/Kqlvalidations.Tests.csproj" },
    { id: "detection-schema", name: "Detection Template Schema", project: ".script/tests/detectionTemplateSchemaValidation/DetectionTemplateSchemaValidation.Tests.csproj" },
    { id: "non-ascii", name: "Non-ASCII", project: ".script/tests/NonAsciiValidationsTests/NonAsciiValidations.Tests.csproj" },
  ];

  for (const dotnetValidator of dotnetValidators) {
    const shouldRun = (options.only.length === 0 || options.only.includes(dotnetValidator.id))
                   && !options.skip.includes(dotnetValidator.id);
    if (shouldRun) {
      // Only run .NET validators if dotnet is available
      try {
        execSync("dotnet --version", { encoding: "utf8", stdio: "pipe" });
        const dotnetResults = await runDotNetValidator(dotnetValidator.project, dotnetValidator.name);

        // Detect GitHub App credential failures and convert to skips with clear guidance
        for (const result of dotnetResults) {
          if (!result.passed && result.error && result.error.includes("GitHub App ID")) {
            result.passed = true;
            result.skipped = true;
            result.skipReason = "Requires GitHub App credentials (only available in CI) — skip locally with --skip " + dotnetValidator.id;
            result.error = undefined;
          }
        }

        allResults.push(...dotnetResults);
      } catch {
        allResults.push({
          validator: dotnetValidator.name,
          filePath: dotnetValidator.project,
          passed: true,
          skipped: true,
          skipReason: ".NET SDK not found — install .NET SDK to run this validator",
        });
      }
    }
  }

  // --- Run ARM-TTK (if not skipped) ---
  const shouldRunArmTtk = (options.only.length === 0 || options.only.includes("arm-ttk"))
                       && !options.skip.includes("arm-ttk");
  if (shouldRunArmTtk) {
    try {
      execSync("pwsh --version", { encoding: "utf8", stdio: "pipe" });
      const armTtkResults = await runArmTtkValidator(files);
      allResults.push(...armTtkResults);
    } catch {
      // PowerShell not available — skip silently
    }
  }

  // --- Report ---
  printReport(allResults, options.verbose, options.jsonOutput);

  // --- Exit Code ---
  const hasFailures = allResults.some(r => !r.passed);
  process.exit(hasFailures ? 1 : 0);
}

// Run
main().catch(e => {
  console.error("Fatal error:", e);
  process.exit(2);
});
