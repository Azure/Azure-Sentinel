import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ConnectorCategory } from "./utils/dataConnector";
import { isValidRequirementBanner } from "./utils/dataConnectorCheckers/additionalBannerRequirementCheckers";
import { isValidDataType } from "./utils/dataConnectorCheckers/dataTypeChecker";
import { isValidFileName } from "./utils/dataConnectorCheckers/fileNameChecker";
import { isValidId } from "./utils/dataConnectorCheckers/idChecker";
import { isValidPermissions } from "./utils/dataConnectorCheckers/permissionsChecker";
import { ExitCode } from "./utils/exitCode";
import { isValidSchema } from "./utils/jsonSchemaChecker";
import * as logger from "./utils/logger";

export async function IsValidDataConnectorSchema(filePath: string): Promise<ExitCode> {
  let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));
  var filename = filePath.replace(/^.*[\\\/]/, '')
  console.log(filename);
  if(isPotentialConnectorJson(jsonFile))
  {
    let connectorCategory = getConnectorCategory(jsonFile.dataTypes, jsonFile.instructionSteps);
    let schema = JSON.parse(fs.readFileSync(".script/utils/schemas/"+ connectorCategory +"_ConnectorSchema.json", "utf8"));
    isValidSchema(jsonFile, schema);
    isValidId(jsonFile.id);
    isValidDataType(jsonFile.dataTypes);
     isValidFileName(filePath)
    console.log(jsonFile.additionalRequirementBanner)
    if(jsonFile.additionalRequirementBanner!="" && jsonFile.additionalRequirementBanner!= undefined)
    {
    isValidRequirementBanner(jsonFile.additionalRequirementBanner)
    }
    isValidPermissions(jsonFile.permissions, connectorCategory);
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

function getConnectorCategory(dataTypes : any, instructionSteps:[])
{
  if (dataTypes[0].name.includes("CommonSecurityLog"))
  {
    return ConnectorCategory.CEF;
  }
  else if (dataTypes[0].name.includes("Syslog"))
  {
    return ConnectorCategory.SysLog;
  }
  else if(dataTypes[0].name.endsWith("_CL"))
  {
    let isAzureFunction:boolean = false;
    if(JSON.stringify(instructionSteps).includes("[Deploy To Azure]"))
    {
      isAzureFunction = true;
    }    
    return isAzureFunction ? ConnectorCategory.AzureFunction: ConnectorCategory.RestAPI;
  }

  return "";
}

let fileTypeSuffixes = ["json"];
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