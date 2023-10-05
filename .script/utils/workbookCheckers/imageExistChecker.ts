import fs from "fs";
import { WorkbookValidationError } from "../validationError";
import { WorkbookMetadata } from "../workbookMetadata";

const logoImagesFolderPath: string = "Workbooks/Images/Logos";
const previewImagesFolderPath: string = "Workbooks/Images/Preview";

// Load the skip list from the JSON file
const skipListFile = "./.script/utils/workbookCheckers/WorkbookPreviewImageValidationSkipList.json";
const WorkbookPreviewImageValidationSkipList = fs.existsSync(skipListFile) ? JSON.parse(fs.readFileSync(skipListFile, "utf8")).skipList : [];


// This function checks if the defined logo image files exist
export function doDefinedLogoImageFilesExist(items: Array<WorkbookMetadata>) {
  items.forEach((workbookMetadata: WorkbookMetadata) => {
    if(workbookMetadata.logoFileName !== ""){
      if(!fs.existsSync(`${logoImagesFolderPath}/${workbookMetadata.logoFileName}`)){
        throw new WorkbookValidationError(`Can't locate logo image file ${workbookMetadata.logoFileName} under the ${logoImagesFolderPath} directory`);
      }
    }
  });
}

// This function checks if the defined preview image files exist
export function doDefinedPreviewImageFilesExist(items: Array<WorkbookMetadata>) {
    items.forEach((workbookMetadata: WorkbookMetadata) => {
        // Check if the workbook key is in the skip list
        if (WorkbookPreviewImageValidationSkipList.includes(workbookMetadata.workbookKey)) {
            return; // Skip validation for this workbook
        }

        if (workbookMetadata.previewImagesFileNames.length > 0) {
            workbookMetadata.previewImagesFileNames.forEach((previewImageFileName: string) => {
                if (previewImageFileName !== "" && !fs.existsSync(`${previewImagesFolderPath}/${previewImageFileName}`)) {
                    throw new WorkbookValidationError(`Can't locate preview image file ${previewImageFileName} under the ${previewImagesFolderPath} directory`);
                }
            });
        }
    });
}