import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import { ExitCode } from "./utils/exitCode.js";
import { isValidSchema } from "./utils/jsonSchemaChecker.js";
import * as logger from "./utils/logger.js";
import { doDefinedLogoImageFilesExist, doDefinedPreviewImageFilesExist } from "./utils/workbookCheckers/imageExistChecker.js";
import { isVersionIncrementedOnModification } from "./utils/workbookCheckers/isVersionIncrementedOnModification.js";
import { isValidPreviewImageFileNames } from "./utils/workbookCheckers/previewImageChecker.js";
import { isUniqueKeys } from "./utils/workbookCheckers/uniqueWorkbookKeyChecker.js";

export async function IsValidWorkbookMetadata(filePath: string): Promise<ExitCode> {
  let workbooksMetadata = JSON.parse(fs.readFileSync(filePath, "utf8"));
  let schema = JSON.parse(fs.readFileSync(".script/utils/schemas/workbooksMetadataSchema.json", "utf8"));

  isValidSchema(workbooksMetadata, schema);
  isUniqueKeys(workbooksMetadata);
  isValidPreviewImageFileNames(workbooksMetadata);
  doDefinedLogoImageFilesExist(workbooksMetadata);
  doDefinedPreviewImageFilesExist(workbooksMetadata);
  await isVersionIncrementedOnModification(workbooksMetadata);
  
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
