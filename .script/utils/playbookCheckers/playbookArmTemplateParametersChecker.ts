import { PlaybookValidationError } from "../validationError";
import { ArmTemplate, ArmTemplateParameter } from "./Models/armTemplateModels";
import { isNullOrUndefined, PlaybookNameParameter } from "./playbookARMTemplateUtils";

export function validateTemplateParameters(filePath: string, playbookARMTemplate: ArmTemplate<any>): void {
    validateTemplateHasPlaybookNameParameter(filePath, playbookARMTemplate);
    validateParametersHaveDescription(filePath, playbookARMTemplate);
}

function validateTemplateHasPlaybookNameParameter(filePath: string, playbookARMTemplate: ArmTemplate<any>): void {
    let playbookNameParameter: ArmTemplateParameter = playbookARMTemplate.parameters && playbookARMTemplate.parameters[PlaybookNameParameter];
    if (isNullOrUndefined(playbookNameParameter)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' missing required parameter '${PlaybookNameParameter}'.`);
    }
}

function validateParametersHaveDescription(filePath: string, playbookARMTemplate: ArmTemplate<any>): void {
    Object.keys(playbookARMTemplate.parameters).forEach((parameterName: string) => {
        if (isNullOrUndefined(playbookARMTemplate.parameters[parameterName].metadata?.description)) {
            throw new PlaybookValidationError(`Playbook template '${filePath}' missing required description for parameter '${parameterName}'.`);
        }
    });
}