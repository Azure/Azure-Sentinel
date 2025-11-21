import { PlaybookValidationError } from "../validationError.js";
import { isNullOrUndefined, PlaybookNameParameter } from "./playbookARMTemplateUtils.js";
export function validateTemplateParameters(filePath, playbookARMTemplate) {
    validateTemplateHasPlaybookNameParameter(filePath, playbookARMTemplate);
}
function validateTemplateHasPlaybookNameParameter(filePath, playbookARMTemplate) {
    let playbookNameParameter = playbookARMTemplate.parameters && playbookARMTemplate.parameters[PlaybookNameParameter];
    if (isNullOrUndefined(playbookNameParameter)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' missing required parameter '${PlaybookNameParameter}'.`);
    }
}
//# sourceMappingURL=playbookArmTemplateParametersChecker.js.map