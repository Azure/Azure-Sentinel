import { PlaybookValidationError } from "../validationError.js";
import { ArmTemplate, ArmTemplateParameter } from "./Models/armTemplateModels.js";
import { isNullOrUndefined, PlaybookNameParameter } from "./playbookARMTemplateUtils.js";

export function validateTemplateParameters(filePath: string, playbookARMTemplate: ArmTemplate<any>): void {
    validateTemplateHasPlaybookNameParameter(filePath, playbookARMTemplate);
}

function validateTemplateHasPlaybookNameParameter(filePath: string, playbookARMTemplate: ArmTemplate<any>): void {
    let playbookNameParameter: ArmTemplateParameter = playbookARMTemplate.parameters && playbookARMTemplate.parameters[PlaybookNameParameter];
    if (isNullOrUndefined(playbookNameParameter)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' missing required parameter '${PlaybookNameParameter}'.`);
    }
}