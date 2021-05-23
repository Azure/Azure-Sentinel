import { ArmTemplate, ArmTemplateResource } from "./Models/armTemplateModels";
import { PlaybookTemplateMetadata } from "./Models/playbookTemplateMetadata";

export type PlaybookArmTemplate = ArmTemplate<PlaybookTemplateMetadata>;

export type StringMap<T> = { [key: string]: T; };

export const PlaybookNameParameter = "PlaybookName";
export const ResourceLocationFromResourceGroupValue = "[resourceGroup().location]";

export function getTemplatePlaybookResources(armTemplate: ArmTemplate<any>): ArmTemplateResource[] {
    return armTemplate?.resources.filter((resource: ArmTemplateResource) => resource.type === "Microsoft.Logic/workflows");
}

export function isNullOrUndefined(value: any): boolean {
    return value === undefined || value === null; 
}