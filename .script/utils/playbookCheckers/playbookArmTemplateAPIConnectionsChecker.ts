import { PlaybookValidationError } from "../validationError";
import { ArmTemplate, ArmTemplateResource } from "./Models/armTemplateModels";
import { ApiConnectionResourceProperties } from "./Models/playbookArmModels";
import { getTemplateAPIConnectionResources, isNullOrUndefined } from "./playbookARMTemplateUtils";

const VariableFieldValuePrefix: string = "[variables('";
const VariableFieldValueSuffix: string = "')]";

export function validateTemplateAPIConnections(filePath: string, playbookARMTemplate: ArmTemplate<any>): void {
    let templateAPIConnectionResources: ArmTemplateResource[] = getTemplateAPIConnectionResources(playbookARMTemplate);
    templateAPIConnectionResources.forEach((apiConnectionResource: ArmTemplateResource) => validateAPIConnectionResource(filePath, playbookARMTemplate, apiConnectionResource));
}

function validateAPIConnectionResource(filePath: string, playbookARMTemplate: ArmTemplate<any>, apiConnectionResource: ArmTemplateResource): void {
    let connectionResourceNameVariableName: string | null = extractVariableNameFromTemplateFieldValue(apiConnectionResource.name);
    if (isNullOrUndefined(connectionResourceNameVariableName)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' has API connection with name '${apiConnectionResource.name}' with name not taken from template variables.`);
    }
    validateTemplateVariableExists(filePath, playbookARMTemplate, apiConnectionResource.name, connectionResourceNameVariableName as string);

    let connectionResourceDisplayName: string = (apiConnectionResource.properties as ApiConnectionResourceProperties)?.displayName;
    let connectionDisplayNameVariableName: string | null = extractVariableNameFromTemplateFieldValue(connectionResourceDisplayName);
    if (isNullOrUndefined(connectionDisplayNameVariableName)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' has API connection with name '${apiConnectionResource.name}' with display name not taken from template variables.`);
    }
    validateTemplateVariableExists(filePath, playbookARMTemplate, apiConnectionResource.name, connectionDisplayNameVariableName as string);
}

function validateTemplateVariableExists(filePath: string, playbookARMTemplate: ArmTemplate<any>, apiConnectionResourceName: string, variableName: string): void {
    let matchingTemplateVariable: string | null = !isNullOrUndefined(playbookARMTemplate.variables) ?
        playbookARMTemplate.variables[variableName] :
        null;
    
    if (isNullOrUndefined(matchingTemplateVariable)) {
        throw new PlaybookValidationError(`Playbook template '${filePath}' has API connection with name '${apiConnectionResourceName}' references variable '${variableName}' that does not exist in template.`);
    }
}

/**
 * Extract the name of the variable from the given playbook template field value that is computed from a variable, or null if field isn't computed from variable
 * @param fieldValue value of a field in an ARM template computed from a variable. Example: "[variables('AzureSentinelConnectionName')]"
 */
function extractVariableNameFromTemplateFieldValue(fieldValue: string): string | null {
    if (!fieldValue.toLowerCase().startsWith(VariableFieldValuePrefix.toLowerCase()) || !fieldValue.toLowerCase().endsWith(VariableFieldValueSuffix.toLowerCase())) {
        return null;
    }

    return fieldValue.substring(VariableFieldValuePrefix.length, fieldValue.indexOf(VariableFieldValueSuffix));
}