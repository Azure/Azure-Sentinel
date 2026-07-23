import { Octokit } from "@octokit/rest";
import { createAppAuth } from "@octokit/auth-app";
import * as logger from "./logger.js";
import "./stringExtenssions.js";


const _owner = process.env.REPO_OWNER || process.env.GITHUB_REPOSITORY_OWNER;
const _repo = process.env.REPO_NAME || process.env.GITHUB_REPOSITORY?.split("/")[1];
const _pr_number = process.env.PRNUM ? Number(process.env.PRNUM) : undefined;


if (!_owner || !_repo) {
  console.error("Environment variables REPO_OWNER and REPO_NAME are not set.");
  process.exit(1);
}

let pullRequestDetails: any | undefined;
let resolvedPRNumber: number | undefined;
let octokit: Octokit;

if (process.env.SYSTEM_PULLREQUEST_ISFORK === "true") {
  console.log("Running in a forked repository. Creating unauthenticated Octokit client.");
  octokit = new Octokit(); // Unauthenticated client
} else if (process.env.GITHUBAPPID && process.env.GITHUBAPPPRIVATEKEY && process.env.GITHUBAPPINSTALLATIONID) {
  console.log("Running in a non-forked repository. Creating authenticated Octokit client.");
  octokit = new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: process.env.GITHUBAPPID,
      privateKey: process.env.GITHUBAPPPRIVATEKEY,
      installationId: process.env.GITHUBAPPINSTALLATIONID,
    },
  });
} else {
  console.error("GitHub App authentication is not configured.");
}

export async function GetPRDetails(owner :string  = String(_owner), repo = String(_repo), pull_number: number | undefined = _pr_number) {
  if (!pull_number || Number.isNaN(pull_number)) {
    pull_number = await GetPRNumber(owner, repo);
    if (!pull_number) {
      return;
    }
  }

  if (typeof pullRequestDetails == "undefined") {
    if (!octokit) {
      console.error("Octokit is not initialized. Cannot get PR details.");
      return;
    }
    console.log("Getting PR details");
    const { data } = await octokit.pulls.get({
      owner,
      repo,
      pull_number,
    });
    pullRequestDetails = data;
  }
  return pullRequestDetails;
}

export async function GetDiffFiles(fileKinds: string[], fileTypeSuffixes?: string[], filePathFolderPreffixes?: string[], owner :string  = String(_owner), repo = String(_repo), pull_number: number | undefined = _pr_number) {
  if (!pull_number || Number.isNaN(pull_number)) {
    pull_number = await GetPRNumber(owner, repo);
    if (!pull_number) {
      return;
    }
  }

  const pr = await GetPRDetails(owner, repo, pull_number);

  if (typeof pr === "undefined") {
    console.log("GitHub Pull Request wasn't found. If issue persists - please open an issue");
    return;
  }

  if (!octokit) {
    console.log("Octokit is not initialized. Cannot get diff files.");
    return;
  }

  const { data: changedFiles } = await octokit.pulls.listFiles({
    owner,
    repo,
    pull_number,
  });
  console.log(`${changedFiles.length} files changed in current PR`);

  const filterChangedFiles = changedFiles
    .filter(change => fileKinds.map(kind => kind.toLowerCase()).includes(change.status.toLowerCase()))
    .map(change => change.filename)
    .filter(filePath => typeof fileTypeSuffixes === "undefined" || filePath.endsWithAny(fileTypeSuffixes))
    .filter(filePath => typeof filePathFolderPreffixes === "undefined" || filePath.startsWithAny(filePathFolderPreffixes))
    .filter(filePath => filePath.indexOf(".script/tests") === -1);

  if (filterChangedFiles.length === 0) {
    logger.logWarning(`No changed files in current PR after files filter. File type filter: ${fileTypeSuffixes ? fileTypeSuffixes.toString() : null}, 
        File path filter: ${filePathFolderPreffixes ? filePathFolderPreffixes.toString() : null}`);
    return;
  }

  let fileKindsLogValue = fileKinds.join(",");
  let fileTypeSuffixesLogValue = typeof fileTypeSuffixes === "undefined" ? null : fileTypeSuffixes.join(",");
  let filePathFolderPreffixesLogValue = typeof filePathFolderPreffixes === "undefined" ? null : filePathFolderPreffixes.join(",");
  console.log(`${filterChangedFiles.length} files changed in current PR after filter. File Type Filter: ${fileTypeSuffixesLogValue}, File path Filter: ${filePathFolderPreffixesLogValue}, File Kind Filter: ${fileKindsLogValue}`);

  return filterChangedFiles;
}

async function GetPRNumber(owner: string, repo: string) {
  if (_pr_number && !Number.isNaN(_pr_number)) {
    return _pr_number;
  }

  if (resolvedPRNumber) {
    return resolvedPRNumber;
  }

  const headBranch = process.env.GITHUB_HEAD_REF || process.env.GITHUB_REF_NAME;
  if (!headBranch) {
    console.error("Environment variable PRNUM is not set and branch context is unavailable.");
    return;
  }

  if (!octokit) {
    console.error("Octokit is not initialized. Cannot resolve PR number.");
    return;
  }

  console.log(`Environment variable PRNUM is not set. Resolving PR number for branch '${headBranch}'.`);

  const { data: pullRequests } = await octokit.pulls.list({
    owner,
    repo,
    state: "open",
    head: `${owner}:${headBranch}`,
    per_page: 1,
  });

  resolvedPRNumber = pullRequests?.[0]?.number;

  if (!resolvedPRNumber) {
    console.error(`Could not resolve PR number for branch '${headBranch}'. Please set PRNUM environment variable.`);
    return;
  }

  return resolvedPRNumber;
}