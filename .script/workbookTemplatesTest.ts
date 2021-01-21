import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function IsValidWorkbookMetadata(filePath: string): Promise<ExitCode> {
  return ExitCode.SUCCESS;
} 

let fileTypeSuffixes = ["WorkbooksMetadata.json"];
let filePathFolderPrefixes = ["Workbooks"];
let fileKinds = ["Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidWorkbookMetadata(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`WorkbooksMetadata Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
