import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { GetPRDetails } from "./utils/gitWrapper";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";
import gitP, { SimpleGit } from 'simple-git/promise';

const workingDir = process.cwd();
const templateIdRegex = "id: [0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}";
const git: SimpleGit = gitP(workingDir);

export async function IsIdHasChanged(filePath: string): Promise<ExitCode> {
  filePath = workingDir + '/' + filePath;
  console.log("Id test:   " + filePath);
  const pr = await GetPRDetails();

  if (typeof pr === "undefined") {
    console.log("Azure DevOps CI for a Pull Request wasn't found. If issue persists - please open an issue");
    return ExitCode.ERROR;
  }
  console.log(pr.targetBranch);
  console.log(pr.sourceBranch);
  let options = [pr.targetBranch, pr.sourceBranch, filePath];
  let diffSummary = await git.diff(options);

  if (diffSummary.search(templateIdRegex) > 0){
      throw new Error(diffSummary);
  }
  return ExitCode.SUCCESS;
}

let fileTypeSuffixes = ["yaml", "yml", "json"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsIdHasChanged(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Changes:\n ${e} \n As you can see, the id of file - "${filePath}" has changed.`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  }
};

runCheckOverChangedFiles(CheckOptions, fileTypeSuffixes);
