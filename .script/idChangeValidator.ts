import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { GetPRDetails } from "./utils/gitWrapper";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";
import gitP, { SimpleGit } from 'simple-git/promise';

const workingDir:string = process.cwd();
const guidRegex:string = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}";
const templateIdRegex:string = `(id: ${guidRegex}(.|\n)*){2}`;
const git: SimpleGit = gitP(workingDir);

export async function IsIdHasChanged(filePath: string): Promise<ExitCode> {
  filePath = workingDir + '/' + filePath;
  const pr = await GetPRDetails();
  console.log(filePath);
  
  if (typeof pr === "undefined") {
    console.log("Azure DevOps CI for a Pull Request wasn't found. If issue persists - please open an issue");
    return ExitCode.ERROR;
  }
  
  let options = [pr.targetBranch, pr.sourceBranch, filePath];
  let diffSummary = await git.diff(options);
  let idHasChanged = diffSummary.search(templateIdRegex) > 0;
  if (idHasChanged){
      throw new Error();
  }
  return ExitCode.SUCCESS;
}

let fileKinds = ["Modified"];
let fileTypeSuffixes = ["yaml", "yml", "json"];
let filePathFolderPrefixes = ["Detections","Solutions"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsIdHasChanged(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`${e}: Id of file - "${filePath}" has changed, please make sure you do not change any file id.`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  }
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
