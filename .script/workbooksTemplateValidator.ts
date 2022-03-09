import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";
import { doesNotContainResourceInfo } from "./utils/workbookCheckers/workbookTemplateCheckers/containResourceInfoChecker";
import { isFromTemplateIdNotSentinelUserWorkbook } from "./utils/workbookCheckers/workbookTemplateCheckers/fromTemplateIdChecker";
import { WorkbookTemplate } from "./utils/workbookTemplate";

const workbooksMetadataFilePath: string = "Workbooks/WorkbooksMetadata.json";

export async function IsValidWorkbookTemplate(filePath: string): Promise<ExitCode> {
  const workbookTemplateString: string = fs.readFileSync(filePath, "utf8");
  const parsedWorkbookTemplate: WorkbookTemplate = JSON.parse(workbookTemplateString);
  
  // WorkbooksMetadata.json file is not a workbook template file but is still under the same folder of the templates. Therefore we want to exclude it from this test.
  if(filePath === workbooksMetadataFilePath){
    return ExitCode.SUCCESS;
  }
  
  if(isValidWorkbookJson(parsedWorkbookTemplate))
  {
    isFromTemplateIdNotSentinelUserWorkbook(parsedWorkbookTemplate);
    doesNotContainResourceInfo(workbookTemplateString); // Pass the json file as string so we can perform a regex search on the content
  }
  return ExitCode.SUCCESS;
}

function isValidWorkbookJson(jsonFile: any) {
  if(typeof jsonFile.$schema != "undefined" && typeof jsonFile.$schema.includes("schema/workbook.json") && typeof jsonFile.version != "undefined" && jsonFile.version === "Notebook/1.0")
  {
    return true;
  }
  return false;
}

let fileTypeSuffixes = [".json"];
let filePathFolderPrefixes = ["Workbooks","Solutions"];
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
