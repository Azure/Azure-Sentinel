import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";
import { isFromTemplateIdNotSentinelUserWorkbook } from "./utils/workbookCheckers/workbookTemplateCheckers/fromTemplateIdChecker";
import { WorkbookTemplate } from "./utils/workbookTemplate";

export async function IsValidWorkbookTemplate(filePath: string): Promise<ExitCode> {
  let workbookTemplate: WorkbookTemplate = JSON.parse(fs.readFileSync(filePath, "utf8"));
  let workbooksMetadataFilePath: string = "Workbooks/WorkbooksMetadata.json";
  
  // WorkbooksMetadata.json file is not a workbook template file but is still under the same folder of the templates. Therefore we want to exclude it from this test.
  if(filePath === workbooksMetadataFilePath){
    return ExitCode.SUCCESS;
  }
  
  isFromTemplateIdNotSentinelUserWorkbook(workbookTemplate);
  
  return ExitCode.SUCCESS;
} 

let fileTypeSuffixes = [".json"];
let filePathFolderPrefixes = ["Workbooks"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidWorkbookTemplate(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`WorkbooksTemplate Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
