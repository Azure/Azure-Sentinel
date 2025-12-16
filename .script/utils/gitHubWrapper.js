import { Octokit } from "@octokit/rest";
import { createAppAuth } from "@octokit/auth-app";
import { execSync } from "child_process";
import fs from "fs";
import * as logger from "./logger.js";
import "./stringExtenssions.js";
const _owner = process.env.REPO_OWNER;
const _repo = process.env.REPO_NAME;
const _pr_number = process.env.PRNUM;
if (!_owner || !_repo || !_pr_number) {
    console.error("Environment variables REPO_OWNER, REPO_NAME and PRNUM are not set.");
    process.exit(1);
}
let pullRequestDetails;
let octokit;
if (process.env.GITHUB_TOKEN) {
    console.log("Creating authenticated Octokit client using GITHUB_TOKEN.");
    octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
}
else if (process.env.SYSTEM_PULLREQUEST_ISFORK === "true") {
    console.log("Running in a forked repository. Creating unauthenticated Octokit client.");
    octokit = new Octokit(); // Unauthenticated client
}
else if (process.env.GITHUBAPPID && process.env.GITHUBAPPPRIVATEKEY && process.env.GITHUBAPPINSTALLATIONID) {
    console.log("Running in a non-forked repository. Creating authenticated Octokit client.");
    octokit = new Octokit({
        authStrategy: createAppAuth,
        auth: {
            appId: process.env.GITHUBAPPID,
            privateKey: process.env.GITHUBAPPPRIVATEKEY,
            installationId: process.env.GITHUBAPPINSTALLATIONID,
        },
    });
}
else {
    console.error("GitHub App authentication is not configured.");
}

function safeExec(cmd) {
    try {
        return execSync(cmd, { stdio: ["ignore", "pipe", "ignore"] }).toString("utf8");
    }
    catch {
        return;
    }
}
function tryVerifyRef(ref) {
    return typeof safeExec(`git rev-parse --verify ${ref}^{commit}`) !== "undefined";
}
function getTargetBranchName() {
    const raw = process.env.SYSTEM_PULLREQUEST_TARGETBRANCH || process.env.GITHUB_BASE_REF;
    if (!raw)
        return;
    const parts = raw.split("/");
    return parts[parts.length - 1];
}
function getEventBaseHeadShas() {
    const eventPath = process.env.GITHUB_EVENT_PATH;
    if (!eventPath)
        return {};
    try {
        const raw = fs.readFileSync(eventPath, "utf8");
        const evt = JSON.parse(raw);
        const pr = evt?.pull_request;
        return {
            baseSha: pr?.base?.sha,
            headSha: pr?.head?.sha,
        };
    }
    catch {
        return {};
    }
}
function getMergeCommitParents() {
    const parentsLine = safeExec("git rev-list --parents -n 1 HEAD")?.trim();
    if (!parentsLine)
        return {};
    const parts = parentsLine.split(/\s+/);
    if (parts.length >= 3) {
        return { parent1: parts[1], parent2: parts[2] };
    }
    return {};
}
function parseNameStatus(output, kindsLower) {
    const entries = [];
    const lines = output.split(/\r?\n/).filter(l => l.trim().length > 0);
    for (const line of lines) {
        const parts = line.split("\t");
        if (parts.length < 2)
            continue;
        const status = parts[0];
        const code = status[0];
        let kind;
        let filename;
        if (code === "R" || code === "C") {
            kind = code === "R" ? "renamed" : "copied";
            filename = parts[2] || parts[1];
        }
        else {
            kind = code === "A" ? "added" : code === "D" ? "deleted" : "modified";
            filename = parts[1];
        }
        if (!kindsLower.includes(kind))
            continue;
        if (filename.indexOf(".script/tests") !== -1)
            continue;
        entries.push({ kind, filename });
    }
    return entries;
}
function getGitDiffEntries(fileKinds) {
    const kindsLower = fileKinds.map(k => k.toLowerCase());
    const { baseSha, headSha } = getEventBaseHeadShas();
    if (baseSha && headSha && tryVerifyRef(baseSha) && tryVerifyRef(headSha)) {
        const out = safeExec(`git diff --name-status ${baseSha} ${headSha}`);
        if (out)
            return parseNameStatus(out, kindsLower);
    }
    const { parent1, parent2 } = getMergeCommitParents();
    if (parent1 && parent2 && tryVerifyRef(parent1) && tryVerifyRef(parent2)) {
        const out = safeExec(`git diff --name-status ${parent1} ${parent2}`);
        if (out)
            return parseNameStatus(out, kindsLower);
    }
    const targetBranch = getTargetBranchName();
    const candidateRefs = targetBranch ? [`origin/${targetBranch}`, `upstream/${targetBranch}`, targetBranch] : ["origin/master", "upstream/master", "master"];
    const baseRef = candidateRefs.find(r => tryVerifyRef(r));
    if (baseRef) {
        const out = safeExec(`git diff --name-status ${baseRef}...HEAD`);
        if (out)
            return parseNameStatus(out, kindsLower);
    }
    const out = safeExec("git diff --name-status HEAD~1...HEAD");
    if (out)
        return parseNameStatus(out, kindsLower);
    return;
}
export async function GetPRDetails(owner = String(_owner), repo = String(_repo), pull_number = Number(_pr_number)) {
    if (typeof pullRequestDetails == "undefined") {
        if (!octokit) {
            console.error("Octokit is not initialized. Cannot get PR details.");
            return;
        }
        try {
            console.log("Getting PR details");
            const { data } = await octokit.pulls.get({
                owner,
                repo,
                pull_number,
            });
            pullRequestDetails = data;
        }
        catch (e) {
            console.log(`Failed to get PR details via GitHub API. Falling back to local git diff. ${e?.message || e}`);
            return;
        }
    }
    return pullRequestDetails;
}
export async function GetDiffFiles(fileKinds, fileTypeSuffixes, filePathFolderPreffixes, owner = String(_owner), repo = String(_repo), pull_number = Number(_pr_number)) {
    let changedFilePaths;
    if (octokit) {
        try {
            const pr = await GetPRDetails(owner, repo, pull_number);
            if (typeof pr !== "undefined") {
                const { data: changedFiles } = await octokit.pulls.listFiles({
                    owner,
                    repo,
                    pull_number,
                });
                console.log(`${changedFiles.length} files changed in current PR`);
                changedFilePaths = changedFiles
                    .filter((change) => fileKinds.map(kind => kind.toLowerCase()).includes(String(change.status).toLowerCase()))
                    .map((change) => String(change.filename));
            }
        }
        catch (e) {
            console.log(`Failed to list PR files via GitHub API. Falling back to local git diff. ${e?.message || e}`);
        }
    }
    if (typeof changedFilePaths === "undefined") {
        const gitEntries = getGitDiffEntries(fileKinds);
        if (typeof gitEntries === "undefined") {
            console.log("Unable to determine changed files via GitHub API or local git diff.");
            return;
        }
        console.log(`${gitEntries.length} files changed in current PR (git diff fallback)`);
        changedFilePaths = gitEntries.map(e => e.filename);
    }
    const filterChangedFiles = changedFilePaths
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
//# sourceMappingURL=gitHubWrapper.js.map