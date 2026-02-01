import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import * as logger from "./utils/logger.js";
import { doesNotContainResourceInfo } from "./utils/workbookCheckers/workbookTemplateCheckers/containResourceInfoChecker.js";
import { isFromTemplateIdNotSentinelUserWorkbook } from "./utils/workbookCheckers/workbookTemplateCheckers/fromTemplateIdChecker.js";
const workbooksMetadataFilePath = "Workbooks/WorkbooksMetadata.json";
export async function IsValidWorkbookTemplate(filePath) {
    const workbookTemplateString = fs.readFileSync(filePath, "utf8");
    const parsedWorkbookTemplate = JSON.parse(workbookTemplateString);
    // WorkbooksMetadata.json file is not a workbook template file but is still under the same folder of the templates. Therefore we want to exclude it from this test.
    if (filePath === workbooksMetadataFilePath) {
        return 0 /* ExitCode.SUCCESS */;
    }
    if (isValidWorkbookJson(parsedWorkbookTemplate)) {
        isFromTemplateIdNotSentinelUserWorkbook(parsedWorkbookTemplate);
        doesNotContainResourceInfo(workbookTemplateString); // Pass the json file as string so we can perform a regex search on the content
    }
    return 0 /* ExitCode.SUCCESS */;
}
function isValidWorkbookJson(jsonFile) {
    if (typeof jsonFile.$schema != "undefined" && typeof jsonFile.$schema.includes("schema/workbook.json") && typeof jsonFile.version != "undefined" && jsonFile.version === "Notebook/1.0") {
        return true;
    }
    return false;
}
let fileTypeSuffixes = [".json"];
let filePathFolderPrefixes = ["Workbooks", "Solutions"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath) => {
        return IsValidWorkbookTemplate(filePath);
    },
    onExecError: async (e, filePath) => {
        console.log(`WorkbooksTemplate Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};
runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
//# sourceMappingURL=workbooksTemplateValidator.js.map