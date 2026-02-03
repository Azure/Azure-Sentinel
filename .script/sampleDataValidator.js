import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import * as logger from "./utils/logger.js";
import { isValidSampleData } from "./utils/sampleDataCheckers/sampleDataCheckers.js";
export async function IsValidSampleDataSchema(filePath) {
    let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));
    isValidSampleData(jsonFile);
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