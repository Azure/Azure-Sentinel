import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import { isValidSchema } from "./utils/jsonSchemaChecker";
import { isValidId } from "./utils/dataConnectorCheckers/idChecker";
import { isValidDataType } from "./utils/dataConnectorCheckers/dataTypeChecker";
import * as logger from "./utils/logger";

export async function IsValidDataConnectorSchema(filePath: string): Promise<ExitCode> {
  let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));
  let schema = JSON.parse(fs.readFileSync(".script/utils/schemas/DataConnectorSchema.json", "utf8"));
if(isPotentialConnectorJson(jsonFile))
{
  isValidSchema(jsonFile, schema);
  isValidId(jsonFile.id);
  isValidDataType(jsonFile.dataTypes);
}
else{
  console.warn(`Could not identify json file as a connector. Skipping File path: ${filePath}`)
}

  return ExitCode.SUCCESS;
}

function isPotentialConnectorJson(jsonFile: any) {
  if(typeof jsonFile.id != "undefined" && typeof jsonFile.connectivityCriterias != "undefined")
  {
    return true;
  }
  return false;
}

let fileTypeSuffixes = ["*.json"];
let filePathFolderPrefixes = ["DataConnectors"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidDataConnectorSchema(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Data Connector Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
