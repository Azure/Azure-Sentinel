import fs from "fs";
import { isValidSchema } from "./jsonSchemaValidator";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";
import { isValidPreviewImageFileNames } from "./workbooksValidations/previewImageValidator";
import { isUniqueKeys } from "./workbooksValidations/uniqueWorkbookKeyValidator";

export async function IsValidWorkbook(filePath: string): Promise<ExitCode> {
  if (filePath.endsWith("WorkbooksMetadata.json")) {
    let workbooksMetadata = JSON.parse(fs.readFileSync(filePath, "utf8"));
    let schema = JSON.parse(fs.readFileSync(".script/utils/schemas/WorkbooksMetadataSchema.json", "utf8"));

    isValidSchema(workbooksMetadata, schema);
    isUniqueKeys(workbooksMetadata);
    isValidPreviewImageFileNames(workbooksMetadata);
  }
  return ExitCode.SUCCESS;
} 

let fileTypeSuffixes = [".json"];
let filePathFolderPrefixes = ["Workbooks"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidWorkbook(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Workbooks Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
