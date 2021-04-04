import { GetDiffFiles, GetPRDetails } from "../gitWrapper";
import { WorkbookMetadata } from "../workbookMetadata";
import gitP, { SimpleGit } from 'simple-git/promise';

const workingDir:string = process.cwd();
const git: SimpleGit = gitP(workingDir);

let fileTypeSuffixes = [".json"];
let filePathFolderPrefixes = ["Workbooks"];
let fileKinds = ["Modified"];

// Checks that the version of the workbook is incremented if modified
export async function isVersionIncrementedOnModification(items: Array<WorkbookMetadata>) {
  const pr = await GetPRDetails();

  if(pr){ // pr may return undefined
    const changedFiles = await GetDiffFiles(fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
    const options = [pr.targetBranch, pr.sourceBranch, "Workbooks/WorkbooksMetadata.json", "-W"];
    console.log("options: " + options)
    const diffSummary = await git.diff(options);
    console.log(diffSummary)
    if(changedFiles && changedFiles.length > 0){
      items
      .filter((workbookMetadata: WorkbookMetadata) => changedFiles.includes(`Workbooks/${workbookMetadata.templateRelativePath}`))
      .forEach(async (workbookMetadata: WorkbookMetadata) => {
        workbookMetadata["version"] = workbookMetadata["version"]
        //console.log(workbookMetadata)
        //console.log(diffSummary)
      });
    }
  }
}
