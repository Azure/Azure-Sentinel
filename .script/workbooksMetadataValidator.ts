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
  console.log("Reading workbooksMetadataSchema.json");
  let schema = JSON.parse(fs.readFileSync(".script/utils/schemas/workbooksMetadataSchema.json", "utf8"));
  console.log("Done Reading workbooksMetadataSchema.json");

  console.log("Running isValidSchema");
  isValidSchema(workbooksMetadata, schema);
  console.log("Done Running isValidSchema");
  console.log("Running isUniqueKeys");
  isUniqueKeys(workbooksMetadata);
  console.log("Done Running isUniqueKeys");
  console.log("Running isValidPreviewImageFileNames");
  isValidPreviewImageFileNames(workbooksMetadata);
  console.log("Done Running isValidPreviewImageFileNames");
  console.log("Running doDefinedLogoImageFilesExists");
  doDefinedLogoImageFilesExist(workbooksMetadata);
  console.log("Done Running doDefinedLogoImageFilesExists");
  console.log("Running doDefinedPreviewImageFilesExist");
  doDefinedPreviewImageFilesExist(workbooksMetadata);
  console.log("Done Running doDefinedPreviewImageFilesExist");
  console.log("Running isVersionIncrementedOnModification");
  await isVersionIncrementedOnModification(workbooksMetadata);
  console.log("Done Running isVersionIncrementedOnModification");
  
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
