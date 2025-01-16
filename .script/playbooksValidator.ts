import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import { ExitCode } from "./utils/exitCode.js";
import { isValidSchema } from "./utils/jsonSchemaChecker.js";
import * as logger from "./utils/logger.js";
import { ArmTemplate, ArmTemplateResource } from "./utils/playbookCheckers/Models/armTemplateModels.js";
import { PlaybookTemplateMetadata } from "./utils/playbookCheckers/Models/playbookTemplateMetadata.js";
import { validateTemplateMetadata } from "./utils/playbookCheckers/playbookArmTemplateMetadataChecker.js";
import { validateTemplateParameters } from "./utils/playbookCheckers/playbookArmTemplateParametersChecker.js";
import { getTemplatePlaybookResources } from "./utils/playbookCheckers/playbookARMTemplateUtils.js";
import { validatePlaybookResource } from "./utils/playbookCheckers/playbookResourceChecker.js";

export async function IsValidTemplate(filePath: string): Promise<ExitCode> {
  let playbookARMTemplate: ArmTemplate<PlaybookTemplateMetadata> = JSON.parse(fs.readFileSync(filePath, "utf8"));
  
  validateARMTemplateSchema(playbookARMTemplate);
  
  // Some ARM template files deploy external resources required by playbooks (e.g custom connector) and not the actual playbook, so they don't require playbook-specific validations
  let templatePlaybookResources: ArmTemplateResource[] = getTemplatePlaybookResources(playbookARMTemplate);
  if (templatePlaybookResources.length > 0) {
    await validateARMTemplateWithPlaybookResource(filePath, playbookARMTemplate);
  }

  return ExitCode.SUCCESS;
}

function validateARMTemplateSchema(playbookARMTemplate: ArmTemplate<PlaybookTemplateMetadata>): void {
    let schema = JSON.parse(fs.readFileSync(".script/utils/schemas/ARM_DeploymentTemplateSchema.json", "utf8"));

    isValidSchema(playbookARMTemplate, schema);  
}

function validateARMTemplateWithPlaybookResource(filePath: string, playbookARMTemplate: ArmTemplate<PlaybookTemplateMetadata>): void {
    validateTemplateParameters(filePath, playbookARMTemplate);
    validateTemplateMetadata(filePath, playbookARMTemplate);
    validatePlaybookResource(filePath, playbookARMTemplate);
}

let fileTypeSuffixes = ["azuredeploy.json"];
let filePathFolderPrefixes = ["Playbooks","Solutions"];
let fileKinds = ["Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidTemplate(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Playbooks validation failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
