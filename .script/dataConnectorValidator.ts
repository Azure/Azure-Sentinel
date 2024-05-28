import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import { isValidSchema } from "./utils/jsonSchemaChecker";
import { isValidId } from "./utils/dataConnectorCheckers/idChecker";
import { isValidDataType } from "./utils/dataConnectorCheckers/dataTypeChecker";
import { isValidPermissions } from "./utils/dataConnectorCheckers/permissionsChecker";
import * as logger from "./utils/logger";
import { ConnectorCategory } from "./utils/dataConnector";

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
  else if (dataTypes[0].name.includes("SecurityAlert(ASC)"))
  {
    return ConnectorCategory.SecurityAlertASC;
  }
  else if (dataTypes[0].name.includes("ThreatIntelligenceIndicator"))
  {
    return ConnectorCategory.ThreatIntelligenceIndicator;
  }
  else if (dataTypes[0].name.includes("PowerBIActivity"))
  {
    return ConnectorCategory.PowerBIActivity;
  }
  else if (dataTypes[0].name.includes("MicrosoftPurviewInformationProtection"))
  {
    return ConnectorCategory.MicrosoftPurviewInformationProtection;
  }
  else if (dataTypes[0].name.includes("AzureActivity"))
  {
    return ConnectorCategory.AzureActivity;
  }
  else if (dataTypes[0].name.includes("Event"))
  {
    return ConnectorCategory.Event;
  }
  else if (dataTypes[0].name.includes("SecurityAlert(OATP)"))
  {
    return ConnectorCategory.SecurityAlertOATP;
  }
  else if (dataTypes[0].name.includes("AzureDevOpsAuditing"))
  {
    return ConnectorCategory.AzureDevOpsAuditing;
  }
  else if (dataTypes[0].name.includes("AzureDiagnostics"))
  {
    return ConnectorCategory.AzureDiagnostics;
  }
  else if(dataTypes[0].name.endsWith("_CL"))
  {
    if(JSON.stringify(instructionSteps).includes("[Deploy To Azure]"))
    {
        return ConnectorCategory.AzureFunction;
    }
    else if((dataTypes[0].name.includes("meraki") || dataTypes[0].name.includes("vCenter")) && JSON.stringify(instructionSteps).includes("\"type\":\"InstallAgent\""))
    {
        return ConnectorCategory.SysLog;
    }
    return ConnectorCategory.RestAPI;
  }
  else if (dataTypes[0].name.includes("Dynamics365Activity"))
  {
    return ConnectorCategory.Dynamics365Activity;
  }
  else if (dataTypes[0].name.includes("CrowdstrikeReplicatorV2"))
  {
    return ConnectorCategory.CrowdstrikeReplicatorV2;
  }
  else if (dataTypes[0].name.includes("BloodHoundEnterprise"))
  {
    return ConnectorCategory.BloodHoundEnterprise;
  }
  else if (dataTypes[0].name.includes("AwsS3"))
  {
    return ConnectorCategory.AwsS3;
  }
  else if (dataTypes[0].name.includes("AWS"))
  {
    return ConnectorCategory.AWS;
  }
  else if (dataTypes[0].name.includes("Corelight"))
  {
    return ConnectorCategory.Corelight;
  }
  else if (dataTypes[0].name.includes("SigninLogs"))
  {
    return ConnectorCategory.AzureActiveDirectory;
  }
  else if (dataTypes[0].name.includes("corelight_bacnet"))
  {
    return ConnectorCategory.CorelightConnectorExporter;
  }
  else if (dataTypes[0].name.includes("SecurityIncident"))
  {
    return ConnectorCategory.CybleThreatIntel;
  }
  return "";
} 
let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["DataConnectors","Solutions"];
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