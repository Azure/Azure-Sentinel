import fs from "fs";
import { SchemaError, Validator } from 'jsonschema';
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function IsValidJsonFile(filePath: string): Promise<ExitCode> {
  const json = JSON.parse(fs.readFileSync(filePath, "utf8")); 
  if (filePath.endsWith('WorkbooksMetadata.json')) {
    validateWorkbookSchema(json);
  }
  return ExitCode.SUCCESS;
}

function validateWorkbookSchema(workbooksMetadataJson: object) {
  const schema = JSON.parse(fs.readFileSync('.script/utils/WorkbooksMetadataSchema.json', 'utf8'));
  var validationResult = new Validator().validate(workbooksMetadataJson, schema);
  if (!validationResult.valid) {
    let errorMsg = validationResult.errors.map(err => err.message).join(", ");
    throw new SchemaError(errorMsg, schema)
  }
}

let fileTypeSuffixes = ["json"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidJsonFile(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Incorrect Json file. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  }
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes);
