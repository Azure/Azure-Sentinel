import { GetDiffFiles, GetPRDetails } from "../gitHubWrapper.js";
import gitP, { SimpleGit } from "simple-git";
import { WorkbookValidationError } from "../validationError.js";
import { ExitCode } from "../exitCode.js";

const git: SimpleGit = gitP(process.cwd());
const metadataPath = "Workbooks/WorkbooksMetadata.json";
type MetadataVersions = Map<string, Map<string, string>>;

// Compare complete snapshots: diff context does not preserve JSON object boundaries.
export async function isVersionIncrementedOnModification() {
  const pr = await GetPRDetails();
  if (!pr) {
    return ExitCode.SUCCESS;
  }

  const changedFiles = await GetDiffFiles(["Modified"], [".json"], ["Workbooks/"]);
  const changedWorkbooks = (changedFiles || []).filter(path => path !== metadataPath);
  if (changedWorkbooks.length === 0) {
    return ExitCode.SUCCESS;
  }

  const base = await readVersions(pr.base.sha, pr.base.repo.clone_url);
  const head = await readVersions(pr.head.sha, pr.head.repo.clone_url);

  for (const path of changedWorkbooks) {
    const template = path.substring("Workbooks/".length);
    const oldEntries = base.get(template);
    const newEntries = head.get(template);
    if (!oldEntries && !newEntries) {
      continue;
    }
    if (!oldEntries || !newEntries || oldEntries.size !== newEntries.size ||
        [...oldEntries.keys()].some(key => !newEntries.has(key))) {
      throw new WorkbookValidationError(`Missing or ambiguous metadata for modified workbook ${template} in ${metadataPath}. Both PR snapshots must contain the same workbook keys for this template.`);
    }

    // Multiple gallery entries may share a template; every existing entry needs its own bump.
    for (const [key, oldVersion] of oldEntries) {
      const newVersion = newEntries.get(key)!;
      if (!isGreaterVersion(newVersion, oldVersion)) {
        throw new WorkbookValidationError(`The new updated version (${newVersion}) must be greater than the old version (${oldVersion}) for workbook ${template} (workbookKey ${key}) in ${metadataPath}.`);
      }
    }
  }
  return ExitCode.SUCCESS;
}

async function readVersions(sha: string, repository: string): Promise<MetadataVersions> {
  if (typeof sha !== "string" || !/^[a-f0-9]{40}$/i.test(sha)) {
    throw new WorkbookValidationError(`Missing or invalid PR commit SHA for ${metadataPath}.`);
  }

  let content: string;
  try {
    try {
      await git.catFile(["-e", `${sha}^{commit}`]);
    } catch {
      await git.fetch(["--no-tags", "--no-recurse-submodules", "--depth=1", repository, sha]);
    }
    content = await git.show([`${sha}:${metadataPath}`]);
  } catch (error) {
    throw new WorkbookValidationError(`Unable to read ${metadataPath} at ${sha} from git: ${error}`);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch (error) {
    throw new WorkbookValidationError(`Unable to parse ${metadataPath} at ${sha}: ${error}`);
  }
  if (!Array.isArray(parsed)) {
    throw new WorkbookValidationError(`Expected a metadata array in ${metadataPath} at ${sha}.`);
  }

  const entries: unknown[] = parsed;
  const versions: MetadataVersions = new Map();
  const keys = new Set<string>();
  for (const entry of entries) {
    if (!entry || typeof entry !== "object" ||
        !("templateRelativePath" in entry) || !("workbookKey" in entry) || !("version" in entry) ||
        typeof entry.templateRelativePath !== "string" || !entry.templateRelativePath ||
        typeof entry.workbookKey !== "string" || !entry.workbookKey ||
        typeof entry.version !== "string" || !/^\d+(?:\.\d+)+$/.test(entry.version)) {
      throw new WorkbookValidationError(`Missing or invalid template, workbook key, or numeric dotted version in ${metadataPath} at ${sha}.`);
    }
    if (keys.has(entry.workbookKey)) {
      throw new WorkbookValidationError(`Duplicate workbookKey ${entry.workbookKey} in ${metadataPath} at ${sha}.`);
    }
    keys.add(entry.workbookKey);
    let templateVersions = versions.get(entry.templateRelativePath);
    if (!templateVersions) {
      templateVersions = new Map();
      versions.set(entry.templateRelativePath, templateVersions);
    }
    templateVersions.set(entry.workbookKey, entry.version);
  }
  return versions;
}

function isGreaterVersion(newVersion: string, oldVersion: string): boolean {
  const next = newVersion.split(".").map(part => BigInt(part));
  const previous = oldVersion.split(".").map(part => BigInt(part));
  for (let i = 0; i < Math.max(next.length, previous.length); i++) {
    const difference = (next[i] || 0n) - (previous[i] || 0n);
    if (difference !== 0n) {
      return difference > 0n;
    }
  }
  return false;
}
