import { GetDiffFiles, GetPRDetails } from "../gitWrapper";
import { WorkbookMetadata } from "../workbookMetadata";
import gitP, { SimpleGit } from 'simple-git/promise';
import { WorkbookValidationError } from "../validationError";

const workingDir:string = process.cwd();
const git: SimpleGit = gitP(workingDir);

const fileTypeSuffixes = [".json"];
const filePathFolderPrefixes = ["Workbooks"];
const fileKinds = ["Modified"];

const workbooksDirectoryPath = "Workbooks";

// Checks that the version of the workbook is incremented if modified
export async function isVersionIncrementedOnModification(items: Array<WorkbookMetadata>) {
  const pr = await GetPRDetails();

  if(pr){ // pr may return undefined
    const changedFiles = await GetDiffFiles(fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
    
    if(changedFiles && changedFiles.length > 0){
      const options = [pr.targetBranch, pr.sourceBranch, "-W", `${workbooksDirectoryPath}/WorkbooksMetadata.json`]; // -W option to get the full file content
      const diffSummary = await git.diff(options);
      console.log(diffSummary);
      const diffLinesArray = diffSummary.split('\n').map(l => l.trim());
      const versionChanges = extractVersionChangesByWorkbook(diffLinesArray);

      items
      .filter((workbookMetadata: WorkbookMetadata) => changedFiles.includes(`${workbooksDirectoryPath}/${workbookMetadata.templateRelativePath}`))
      .forEach((workbookMetadata: WorkbookMetadata) => {
        const templateRelativePath = workbookMetadata.templateRelativePath;
        if(versionChanges[templateRelativePath] == null){
          // If the workbook has changed but the version was not updated (a matching key was not found in the versionChanges dictionary) - throw error
          throw new WorkbookValidationError(`The workbook ${workbookMetadata.templateRelativePath} has been modified but the version has not been incremented in the ${workbooksDirectoryPath}/WorkbooksMetadata.json file.`);
        }
        else{
          if(versionChanges[templateRelativePath]["newVersion"] <= versionChanges[templateRelativePath]["oldVersion"]){ // If the version was updated but the new version is not greater than old version - throw error
            throw new WorkbookValidationError(`The new updated version must be greater than the old version for workbook ${workbookMetadata.templateRelativePath} in the ${workbooksDirectoryPath}/WorkbooksMetadata.json file.`);
          }
        }
      });
    }
  }
}


function extractVersionChangesByWorkbook(diffLines: string[]){
  let currentLine = 0;
  let workbookVersionChanges: any = {};
  while(diffLines[currentLine++] != '['){} // Skip to beginning of Workbooks array

  while(diffLines[currentLine] != "]"){
    if(diffLines[currentLine] == "{"){ // Beginning of a workbook metadata object
      currentLine++;
      let templateRelativePath, newVersion, oldVersion;

      while(!(diffLines[currentLine] == "}" || diffLines[currentLine] == "},")){ // While current line is not end of object
        if(diffLines[currentLine].startsWith('"templateRelativePath":')){
          templateRelativePath = diffLines[currentLine].split(':')[1].trim().replace(/\"/gi, "").replace(',', "");
        }

        if(diffLines[currentLine].startsWith('+    "version":')){ // We are only interested in changes of the version value of an existing workbook
          newVersion = diffLines[currentLine].split(':')[1].trim().replace(/\"/gi, "").replace(',', "");
        }

        if(diffLines[currentLine].startsWith('-    "version":')){ // We are only interested in changes of the version value of an existing workbook
          oldVersion = diffLines[currentLine].split(':')[1].trim().replace(/\"/gi, "").replace(',', "");
        }

        currentLine++;
      }
      // Here we finish iterating over the current workbook metadata object. We will add the parsed workbook changes only if all fields are populated.
      if(templateRelativePath != null && newVersion != null && oldVersion != null){
        workbookVersionChanges[templateRelativePath] = {"newVersion": newVersion, "oldVersion": oldVersion};
      }
    }
    currentLine++;
  }

  console.log(workbookVersionChanges);
  return workbookVersionChanges;
}