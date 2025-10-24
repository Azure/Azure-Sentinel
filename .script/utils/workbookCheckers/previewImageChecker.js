import fs from "fs";
import { WorkbookValidationError } from "../validationError.js";
// Load the skip list from the JSON file
const skipListFile = "./.script/utils/workbookCheckers/WorkbookPreviewImageValidationSkipList.json";
const WorkbookPreviewImageValidationSkipList = fs.existsSync(skipListFile) ? JSON.parse(fs.readFileSync(skipListFile, "utf8")).skipList : [];
function isAllPng(previewImagesFileNames) {
    return previewImagesFileNames.every((previewImageFileName) => previewImageFileName.toLowerCase().endsWith('.png'));
}
function isAllIncludeBlackOrWhite(previewImagesFileNames) {
    return previewImagesFileNames.every((previewImageFileName) => ["Black", "black", "white", "White"].some(color => previewImageFileName.includes(color)));
}
function isMissingImages(previewImagesFileNames) {
    let blackImageCount = 0;
    let whiteImageCount = 0;
    previewImagesFileNames.forEach((filename) => {
        if (filename.includes("black") || filename.includes("Black"))
            blackImageCount++;
        if (filename.includes("white") || filename.includes("White"))
            whiteImageCount++;
    });
    return blackImageCount === 0 || whiteImageCount === 0;
}
export function isValidPreviewImageFileNames(items) {
    items.forEach((workbookMetadata) => {
        // Check if the workbook key is in the skip list
        if (WorkbookPreviewImageValidationSkipList.includes(workbookMetadata.workbookKey)) {
            return; // Skip this validation for this workbook
        }
        if (!isAllPng(workbookMetadata.previewImagesFileNames)) {
            throw new WorkbookValidationError(`Invalid Preview Images for workbook ${workbookMetadata.workbookKey}. All preview images must be png files`);
        }
        if (!isAllIncludeBlackOrWhite(workbookMetadata.previewImagesFileNames)) {
            throw new WorkbookValidationError(`Invalid Preview Images for workbook ${workbookMetadata.workbookKey}. All preview image file names must include either "Black" or "White"`);
        }
        if (isMissingImages(workbookMetadata.previewImagesFileNames)) {
            throw new WorkbookValidationError(`Preview Image Validation failed for ${workbookMetadata.workbookKey}. Preview images must contain at least one white background image and one image black background image.`);
        }
    });
}
;
//# sourceMappingURL=previewImageChecker.js.map