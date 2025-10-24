import fs from "fs";
import { WorkbookValidationError } from "../validationError.js";
const logoImagesFolderPath = "Workbooks/Images/Logos";
const previewImagesFolderPath = "Workbooks/Images/Preview";
// Load the skip list from the JSON file
const skipListFile = "./.script/utils/workbookCheckers/WorkbookPreviewImageValidationSkipList.json";
const WorkbookPreviewImageValidationSkipList = fs.existsSync(skipListFile) ? JSON.parse(fs.readFileSync(skipListFile, "utf8")).skipList : [];
// This function checks if the defined logo image files exist
export function doDefinedLogoImageFilesExist(items) {
    items.forEach((workbookMetadata) => {
        if (workbookMetadata.logoFileName !== "") {
            if (!fs.existsSync(`${logoImagesFolderPath}/${workbookMetadata.logoFileName}`)) {
                throw new WorkbookValidationError(`Can't locate logo image file ${workbookMetadata.logoFileName} under the ${logoImagesFolderPath} directory`);
            }
        }
    });
}
// This function checks if the defined preview image files exist
export function doDefinedPreviewImageFilesExist(items) {
    items.forEach((workbookMetadata) => {
        // Check if the workbook key is in the skip list
        if (WorkbookPreviewImageValidationSkipList.includes(workbookMetadata.workbookKey)) {
            return; // Skip validation for this workbook
        }
        if (workbookMetadata.previewImagesFileNames.length > 0) {
            workbookMetadata.previewImagesFileNames.forEach((previewImageFileName) => {
                if (previewImageFileName !== "" && !fs.existsSync(`${previewImagesFolderPath}/${previewImageFileName}`)) {
                    throw new WorkbookValidationError(`Can't locate preview image file ${previewImageFileName} under the ${previewImagesFolderPath} directory`);
                }
            });
        }
    });
}
//# sourceMappingURL=imageExistChecker.js.map