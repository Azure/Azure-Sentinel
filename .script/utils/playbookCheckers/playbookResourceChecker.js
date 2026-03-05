import { PlaybookValidationError } from "../validationError.js";
import { getTemplatePlaybookResources, PlaybookNameParameter, ResourceLocationFromResourceGroupValue } from "./playbookARMTemplateUtils.js";
export function validatePlaybookResource(filePath, playbookARMTemplate) {
    // Template can contain several playbooks that invoke one another, and we want to validate only the 'main' playbook that calls that others
    let templateMainPlaybookResource = getTemplateMainPlaybookResource(filePath, playbookARMTemplate);
    validatePlaybookResourceLocationIsFromResourceGroup(filePath, templateMainPlaybookResource);
}
function getTemplateMainPlaybookResource(filePath, playbookARMTemplate) {
    let templatePlaybookResources = getTemplatePlaybookResources(playbookARMTemplate);
    let templatePlaybookResourcesWithNameFromParameter = templatePlaybookResources.filter((resource) => resource.name === `[parameters('${PlaybookNameParameter}')]`);
    if (templatePlaybookResourcesWithNameFromParameter.length === 0) {
        throw new PlaybookValidationError(`Playbook in template '${filePath}' should have name from parameter '${PlaybookNameParameter}'.`);
    }
    if (templatePlaybookResourcesWithNameFromParameter.length > 1) {
        throw new PlaybookValidationError(`Template '${filePath}' contains more than 1 playbook resource with name from parameter '${PlaybookNameParameter}'.`);
    }
    return templatePlaybookResourcesWithNameFromParameter[0];
}
function validatePlaybookResourceLocationIsFromResourceGroup(filePath, templateMainPlaybookResource) {
    if (templateMainPlaybookResource.location.toLowerCase() !== ResourceLocationFromResourceGroupValue.toLowerCase()) {
        throw new PlaybookValidationError(`Playbook resource '${filePath}' location should be the resource group location.`);
    }
}
//# sourceMappingURL=playbookResourceChecker.js.map