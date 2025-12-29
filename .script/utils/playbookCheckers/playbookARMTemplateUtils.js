export const PlaybookNameParameter = "PlaybookName";
export const ResourceLocationFromResourceGroupValue = "[resourceGroup().location]";
export function getTemplatePlaybookResources(armTemplate) {
    return armTemplate?.resources.filter((resource) => resource.type === "Microsoft.Logic/workflows");
}
export function isPlaybookUsingGalleryMetadata(armTemplate) {
    return !isNullOrUndefined(armTemplate?.metadata?.title) && !isNullOrUndefined(armTemplate?.metadata?.description) && !isNullOrUndefined(armTemplate?.metadata?.author);
}
export function isNullOrUndefined(value) {
    return value === undefined || value === null;
}
export function isNullOrWhitespace(value) {
    return isNullOrUndefined(value) || value.trim().length === 0;
}
//# sourceMappingURL=playbookARMTemplateUtils.js.map