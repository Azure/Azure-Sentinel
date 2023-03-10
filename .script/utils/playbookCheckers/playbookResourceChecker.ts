import { PlaybookValidationError } from "../validationError";
import { ArmTemplate, ArmTemplateResource } from "./Models/armTemplateModels";
import { getTemplatePlaybookResources, PlaybookNameParameter, ResourceLocationFromResourceGroupValue } from "./playbookARMTemplateUtils";

export function validatePlaybookResource(filePath: string, playbookARMTemplate: ArmTemplate<any>): void {
    // Template can contain several playbooks that invoke one another, and we want to validate only the 'main' playbook that calls that others
    let templateMainPlaybookResource: ArmTemplateResource = getTemplateMainPlaybookResource(filePath, playbookARMTemplate);

    validatePlaybookResourceLocationIsFromResourceGroup(filePath, templateMainPlaybookResource);
}

function getTemplateMainPlaybookResource(filePath: string, playbookARMTemplate: ArmTemplate<any>): ArmTemplateResource {
    let templatePlaybookResources: ArmTemplateResource[] = getTemplatePlaybookResources(playbookARMTemplate);
    let templatePlaybookResourcesWithNameFromParameter: ArmTemplateResource[] = templatePlaybookResources.filter((resource: ArmTemplateResource) => resource.name === `[parameters('${PlaybookNameParameter}')]`);

    if (templatePlaybookResourcesWithNameFromParameter.length === 0) {
        throw new PlaybookValidationError(`Playbook in template '${filePath}' should have name from parameter '${PlaybookNameParameter}'.`);
    }

    if (templatePlaybookResourcesWithNameFromParameter.length > 1) {
        throw new PlaybookValidationError(`Template '${filePath}' contains more than 1 playbook resource with name from parameter '${PlaybookNameParameter}'.`);
    }

    return templatePlaybookResourcesWithNameFromParameter[0];
}

function validatePlaybookResourceLocationIsFromResourceGroup(filePath: string, templateMainPlaybookResource: ArmTemplateResource): void {
    if (templateMainPlaybookResource.location.toLowerCase() !== ResourceLocationFromResourceGroupValue.toLowerCase()) {
        throw new PlaybookValidationError(`Playbook resource '${filePath}' location should be the resource group location.`);
    }
}