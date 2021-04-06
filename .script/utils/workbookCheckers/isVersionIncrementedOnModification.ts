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
const gitDiffFileFullContentOption = "-W"; // -W option to get the full file content

// Checks that the version of a workbook template is incremented if modified
export async function isVersionIncrementedOnModification(items: Array<WorkbookMetadata>) {
  const pr = await GetPRDetails();

  if(pr){ // pr may return undefined
    const changedFiles = await GetDiffFiles(fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
    
    if(changedFiles && changedFiles.length > 0){
      const options = [pr.targetBranch, pr.sourceBranch, gitDiffFileFullContentOption, `${workbooksDirectoryPath}/WorkbooksMetadata.json`];
      const diffSummary = await git.diff(options);
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
          const isNewVersionGreaterThanOldVersion = versionChanges[templateRelativePath]["newVersion"] > versionChanges[templateRelativePath]["oldVersion"];

          if(!isNewVersionGreaterThanOldVersion){ // If the version was updated but the new version is not greater than old version - throw error
            throw new WorkbookValidationError(`The new updated version (${versionChanges[templateRelativePath]["newVersion"]}) must be greater than the old version (${versionChanges[templateRelativePath]["oldVersion"]}) for workbook ${workbookMetadata.templateRelativePath} in the ${workbooksDirectoryPath}/WorkbooksMetadata.json file.`);
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
      const replaceQuotesRegex = /\"/gi; // If the replace method receives a string as the first parameter, then only the first occurrence is replaced. To replace all, a regex is required.

      while(!(diffLines[currentLine] == "}" || diffLines[currentLine] == "},")){ // While current line is not end of object
        if(diffLines[currentLine].startsWith('"templateRelativePath":')){
          templateRelativePath = diffLines[currentLine].split(':')[1].trim().replace(replaceQuotesRegex, "").replace(',', "");
        }

        // The '+' may be added to a line as part of the 'git diff' output
        if(diffLines[currentLine].startsWith('+') && diffLines[currentLine].includes('"version":')){ // We are only interested in changes of the version value of an existing workbook
          newVersion = diffLines[currentLine].split(':')[1].trim().replace(replaceQuotesRegex, "").replace(',', "");
        }

        // The '-' may be added to a line as part of the 'git diff' output
        if(diffLines[currentLine].startsWith('-') && diffLines[currentLine].includes('"version":')){ // We are only interested in changes of the version value of an existing workbook
          oldVersion = diffLines[currentLine].split(':')[1].trim().replace(replaceQuotesRegex, "").replace(',', "");
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

  return workbookVersionChanges;
}