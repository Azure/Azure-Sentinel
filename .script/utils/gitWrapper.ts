import { cli, devOps } from "@azure/avocado";
import * as logger from "./logger";
import "./stringExtenssions";
import { PullRequestProperties } from '@azure/avocado/dist/dev-ops';

let pullRequestDetails: PullRequestProperties | undefined;

export async function GetPRDetails() {
  if (typeof pullRequestDetails == "undefined"){
    console.log("Getting PR details");
    const config = cli.defaultConfig();
    console.log(`config Details are ${config}`)
    pullRequestDetails = await devOps.createPullRequestProperties(config);
    console.log(`PR Details are ${pullRequestDetails}`)
    var ss1 = pullRequestDetails.structuralDiff
    var ss2 = pullRequestDetails.targetBranch
    var ss3 = pullRequestDetails.sourceBranch
    var ss4 = pullRequestDetails.workingDir

    console.log(`structuralDiff Details are ${ss1}`)
    console.log(`targetBranch Details are ${ss2}`)
    console.log(`sourceBranch Details are ${ss3}`)
    console.log(`workingDir Details are ${ss4}`)

  }
  return pullRequestDetails;
}

export async function GetDiffFiles(fileKinds: string[], fileTypeSuffixes?: string[], filePathFolderPreffixes?: string[]) {
  const pr = await GetPRDetails();
  if (typeof pr === "undefined") {
    console.log("Azure DevOps CI for a Pull Request wasn't found. If issue persists - please open an issue");
    return;
  }

  let changedFiles = await pr.diff();
  //console.log(`${changedFiles.length} files changed in current PR`);

  const filterChangedFiles = changedFiles
    .filter(change => fileKinds.includes(change.kind))
    .map(change => change.path)
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
  console.log(`Changed files are ${filterChangedFiles}`);
  return filterChangedFiles;
}
