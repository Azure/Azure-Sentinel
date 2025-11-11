import { Octokit } from "@octokit/rest";
import { createAppAuth } from "@octokit/auth-app";
import * as logger from "./logger.js";
import "./stringExtenssions.js";


const _owner = process.env.REPO_OWNER;
const _repo = process.env.REPO_NAME;
const _pr_number = process.env.PRNUM;


if (!_owner || !_repo || !_pr_number) {
  console.error("Environment variables REPO_OWNER, REPO_NAME and PRNUM are not set.");
  process.exit(1);
}

let pullRequestDetails: any | undefined;
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

export async function GetPRDetails(owner :string  = String(_owner), repo = String(_repo), pull_number: number = Number(_pr_number)) {
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

export async function GetDiffFiles(fileKinds: string[], fileTypeSuffixes?: string[], filePathFolderPreffixes?: string[], owner :string  = String(_owner), repo = String(_repo), pull_number: number = Number(_pr_number)) {
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