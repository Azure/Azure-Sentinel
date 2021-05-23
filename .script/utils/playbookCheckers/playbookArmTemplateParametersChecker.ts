import { PlaybookValidationError } from "../validationError";
import { ArmTemplate, ArmTemplateParameter } from "./Models/armTemplateModels";
import { isNullOrUndefined } from "./playbookARMTemplateUtils";

export function validateTemplateParameters(filePath: string, playbookARMTemplate: ArmTemplate<any>): void {
    validateTemplateHasPlaybookNameParameter(filePath, playbookARMTemplate);
}

function validateTemplateHasPlaybookNameParameter(filePath: string, playbookARMTemplate: ArmTemplate<any>): void {
    let playbookNameParameter: ArmTemplateParameter = playbookARMTemplate.parameters && playbookARMTemplate.parameters["PlaybookName"];
    if (isNullOrUndefined(playbookNameParameter)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' missing required parameter 'PlaybookName'.`);
    }
}