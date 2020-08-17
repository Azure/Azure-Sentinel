import fs from "fs";
import { isValidSchema } from "./jsonSchemaValidator";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";
import { isValidPreviewImageFileNames } from "./workbooksValidations/previewImageValidator";
import { isUniqueKeys } from "./workbooksValidations/uniqueWorkbookKeyValidator";

export async function IsValidWorkbookMetadata(filePath: string): Promise<ExitCode> {
  let workbooksMetadata = JSON.parse(fs.readFileSync(filePath, "utf8"));
  let schema = JSON.parse(fs.readFileSync(".script/utils/schemas/WorkbooksMetadataSchema.json", "utf8"));

  isValidSchema(workbooksMetadata, schema);
  isUniqueKeys(workbooksMetadata);
  isValidPreviewImageFileNames(workbooksMetadata);
  
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
