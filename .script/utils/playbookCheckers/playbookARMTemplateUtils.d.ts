import { ArmTemplate, ArmTemplateResource } from "./Models/armTemplateModels.js";
import { PlaybookTemplateMetadata } from "./Models/playbookTemplateMetadata.js";
export type PlaybookArmTemplate = ArmTemplate<PlaybookTemplateMetadata>;
export type StringMap<T> = {
    [key: string]: T;
};
export declare const PlaybookNameParameter = "PlaybookName";
export declare const ResourceLocationFromResourceGroupValue = "[resourceGroup().location]";
export declare function getTemplatePlaybookResources(armTemplate: ArmTemplate<any>): ArmTemplateResource[];
export declare function isPlaybookUsingGalleryMetadata(armTemplate: ArmTemplate<any>): boolean;
export declare function isNullOrUndefined(value: any): boolean;
export declare function isNullOrWhitespace(value: string): boolean;
//# sourceMappingURL=playbookARMTemplateUtils.d.ts.map