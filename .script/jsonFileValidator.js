import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import fs from "fs";
import * as logger from "./utils/logger.js";
export async function IsValidJsonFile(filePath) {
    JSON.parse(fs.readFileSync(filePath, "utf8"));
    return 0 /* ExitCode.SUCCESS */;
}
let fileTypeSuffixes = ["json"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath) => {
        return IsValidJsonFile(filePath);
    },
    onExecError: async (e, filePath) => {
        console.log(`Incorrect Json file. File path: ${filePath}. Error message: ${e.message}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    }
};
runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes);
//# sourceMappingURL=jsonFileValidator.js.map