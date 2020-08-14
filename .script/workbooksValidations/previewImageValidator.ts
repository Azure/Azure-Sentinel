import { WorkbookValidationError } from "../utils/ValidationError";
import { WorkbookMetadata } from "../utils/WorkbookMetadata";

const previewImageRegex: RegExp = /(black|white|Black|White)(\d*?).png/;
const blackPreviewImageRegex: RegExp = /(black|Black)(\d*?).png/;
const whitePreviewImageRegex: RegExp = /(white|White)(\d*?).png/;

function isAllValidFileNames(previewImagesFileNames: Array<string>): boolean {
    return previewImagesFileNames.every((previewImageFileName: string) => previewImageRegex.test(previewImageFileName));
}

function isMissingImages(previewImagesFileNames: Array<string>): boolean {
    let blackImageCount: number = 0;
    let whiteImageCount: number = 0;
    previewImagesFileNames.forEach((filename) => {
        if (whitePreviewImageRegex.test(filename)) whiteImageCount++;
        if (blackPreviewImageRegex.test(filename)) blackImageCount++;
    });
    return blackImageCount === 0 || whiteImageCount === 0;
}

export function isValidPreviewImageFileNames(items: Array<WorkbookMetadata>) {
  items.forEach((workbookMetadata: WorkbookMetadata) => {
    if (!isAllValidFileNames(workbookMetadata.previewImagesFileNames)) {
      throw new WorkbookValidationError(`Invalid Preview Images for workbook ${workbookMetadata.workbookKey}. Filename must contain either "Black" or "White" and must end with .png`);
    }

    if (isMissingImages(workbookMetadata.previewImagesFileNames)) {
      throw new WorkbookValidationError(`Preview Image Validation failed for ${workbookMetadata.workbookKey}. Preview images must contain at least one white background image and one image black background image.`);
    }
  });
};

