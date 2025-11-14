import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import yaml from "js-yaml";
import fs from "fs";
import * as logger from "./utils/logger.js";
export async function IsValidYamlFile(filePath) {
    yaml.safeLoad(fs.readFileSync(filePath, "utf8"));
    return 0 /* ExitCode.SUCCESS */;
}
let fileTypeSuffixes = ["yaml", "yml"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath) => {
        return IsValidYamlFile(filePath);
    },
    onExecError: async (e, filePath) => {
        console.log(`Incorrect yaml file. File path: ${filePath}. Error message: ${e.message}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    }
};
runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes);
//# sourceMappingURL=yamlFileValidator.js.map