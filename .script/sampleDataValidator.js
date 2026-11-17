import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import * as logger from "./utils/logger.js";
import { isAllowedCatalogEmail, isTableCatalogSampleDataPath, isValidSampleData, isValidTableCatalogSampleData, } from "./utils/sampleDataCheckers/sampleDataCheckers.js";
export { isAllowedCatalogEmail, isTableCatalogSampleDataPath, isValidTableCatalogSampleData, };
export async function IsValidSampleDataSchema(filePath) {
    const jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));
    if (isTableCatalogSampleDataPath(filePath)) {
        isValidTableCatalogSampleData(jsonFile, filePath);
    }
    else {
        isValidSampleData(jsonFile);
    }
    return 0 /* ExitCode.SUCCESS */;
}
let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["Sample Data"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath) => {
        return IsValidSampleDataSchema(filePath);
    },
    onExecError: async (e, filePath) => {
        console.log(`Sample Data Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};
runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
//# sourceMappingURL=sampleDataValidator.js.map