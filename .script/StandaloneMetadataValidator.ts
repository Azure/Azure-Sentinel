import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";
import { isValidMetadata } from "./utils/StandaloneMetadataCheckers/StandaloneMetadataCheckers";
import { StandaloneMetadata } from "./utils/standaloneMetadata";

export async function IsValidDataConnectorSchema(filePath: string): Promise<ExitCode> {

  if(!filePath.includes('Templates'))
  {
    let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

    if(isPotentialConnectorJson(jsonFile))
    {
      if(!jsonFile.dataTypes[0].name.includes("Event"))
      {
        let connectorCategory = getConnectorCategory(jsonFile.dataTypes, jsonFile.instructionSteps);
        let schema = JSON.parse(fs.readFileSync(".script/utils/schemas/"+ connectorCategory +"_ConnectorSchema.json", "utf8"));
        isValidSchema(jsonFile, schema);
        isValidId(jsonFile.id);
        isValidDataType(jsonFile.dataTypes);

        /* Disabling temporarily till we get confirmation from PM*/
        // isValidFileName(filePath
        isValidPermissions(jsonFile.permissions, connectorCategory);
      }
      else{
        console.warn(`Skipping File as it is of type Events : ${filePath}`)
      }
    }
    else{
      console.warn(`Could not identify json file as a connector. Skipping File path: ${filePath}`)
    }
  }
  else{
    console.warn(`Skipping Files under Templates folder : ${filePath}`)
  }
  return ExitCode.SUCCESS;
  }

  function isPotentialConnectorJson(jsonFile: any) {
  if(typeof jsonFile.Metadata != "undefined" && typeof jsonFile.Metadata.source != "undefined" && typeof jsonFile.Metadata.source.kind != "undefined" && jsonFile.Metadata.source.kind == "Community")
  {
    return true;
  }
  return false;
}

let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["Playbooks", "Workbooks"];
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