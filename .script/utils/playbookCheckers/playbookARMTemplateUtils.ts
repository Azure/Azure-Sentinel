import { ArmTemplate, ArmTemplateResource } from "./Models/armTemplateModels";
import { PlaybookTemplateMetadata } from "./Models/playbookTemplateMetadata";

export type PlaybookArmTemplate = ArmTemplate<PlaybookTemplateMetadata>;

export type StringMap<T> = { [key: string]: T; };

export const PlaybookNameParameter = "PlaybookName";
export const ResourceLocationFromResourceGroupValue = "[resourceGroup().location]";

export function getTemplatePlaybookResources(armTemplate: ArmTemplate<any>): ArmTemplateResource[] {
    return armTemplate?.resources.filter((resource: ArmTemplateResource) => resource.type === "Microsoft.Logic/workflows");
}

export function isPlaybookUsingGalleryMetadata(armTemplate: ArmTemplate<any>): boolean {
    return !isNullOrUndefined(armTemplate?.metadata?.title) && !isNullOrUndefined(armTemplate?.metadata?.description) && !isNullOrUndefined(armTemplate?.metadata?.author);
}

export function isNullOrUndefined(value: any): boolean {
    return value === undefined || value === null; 
}

export function isNullOrWhitespace(value: string): boolean {
    return isNullOrUndefined(value) || value.trim().length === 0;
}