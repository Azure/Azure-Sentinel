import { GetDiffFiles, GetPRDetails } from "../gitWrapper";
import { WorkbookMetadata } from "../workbookMetadata";
import gitP, { SimpleGit } from 'simple-git/promise';
import { WorkbookValidationError } from "../validationError";

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
    
    if(changedFiles && changedFiles.length > 0){
      const options = [pr.targetBranch, pr.sourceBranch, "-W", "Workbooks/WorkbooksMetadata.json"]; // -W option to get the full file content
      const diffSummary = await git.diff(options);
      const diffLinesArray = diffSummary.split('\n').map(l => l.trim());
      const versionChanges = extractVersionChangesByWorkbook(diffLinesArray);

      items
      .filter((workbookMetadata: WorkbookMetadata) => changedFiles.includes(`Workbooks/${workbookMetadata.templateRelativePath}`))
      .forEach((workbookMetadata: WorkbookMetadata) => {
        const workbookKey = workbookMetadata.workbookKey;
        console.log("here2");
        if(versionChanges[workbookKey] == null){
          console.log("here3");
          // If the workbook has changed but the version was not updated (a matching key was not found in the versionChanges dictionary) - throw error
          throw new WorkbookValidationError(`The workbook ${workbookKey} has been modified but the version has not been incremented in the Workbooks/WorkbooksMetadata.json file.`);
        }
        else{
          console.log("here4");
          if(versionChanges[workbookKey]["newVersion"] <= versionChanges[workbookKey]["oldVersion"]){ // If the version was updated but the new version is not greater than old version - throw error
            console.log("here5");
            throw new WorkbookValidationError(`The new updated version must be greater than the old version for workbook ${workbookKey} in the Workbooks/WorkbooksMetadata.json file.`);
          }
        }
      });

      throw new WorkbookValidationError("here");
    }
  }
  else{
    throw new WorkbookValidationError("here else");
  }
}

function extractVersionChangesByWorkbook(diffLines: string[]){
  let currentLine = 0;
  let workbookVersionChanges: any = {};
  while(diffLines[currentLine++] != '['){} // Skip to beginning of Workbooks array

  while(diffLines[currentLine] != "]"){
    if(diffLines[currentLine] == "{"){ // Beginning of a workbook metadata object
      currentLine++;
      let workbookKey, newVersion, oldVersion;

      while(!(diffLines[currentLine] == "}" || diffLines[currentLine] == "},")){ // While current line is not end of object
        if(diffLines[currentLine].startsWith('"workbookKey"')){
          workbookKey = diffLines[currentLine].split(':')[1].trim().replace('"', "").replace(',', "");
        }

        if(diffLines[currentLine].startsWith('+    "version"')){ // We are only interested in changes of the version value of an existing workbook
          newVersion = diffLines[currentLine].split(':')[1].trim().replace('"', "").replace(',', "");
        }

        if(diffLines[currentLine].startsWith('-    "version"')){ // We are only interested in changes of the version value of an existing workbook
          oldVersion = diffLines[currentLine].split(':')[1].trim().replace('"', "").replace(',', "");
        }

        currentLine++;
      }
      // Here we finish iterating over the current workbook metadata object. We will add the parsed workbook changes only if all fields are populated.
      if(workbookKey != null && newVersion != null && oldVersion != null){
        workbookVersionChanges[workbookKey] = {"newVersion": newVersion, "oldVersion": oldVersion};
      }
    }
    currentLine++;
  }

  console.log("here6");
  return workbookVersionChanges;
}