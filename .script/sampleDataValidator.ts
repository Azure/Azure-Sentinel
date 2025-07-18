import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import { ExitCode } from "./utils/exitCode.js";
import * as logger from "./utils/logger.js";
import { isValidSampleData } from "./utils/sampleDataCheckers/sampleDataCheckers.js";
export async function IsValidSampleDataSchema(filePath: string): Promise<ExitCode> {
    let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));
    isValidSampleData(jsonFile);
    return ExitCode.SUCCESS;
    }


let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["Sample Data"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidSampleDataSchema(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Sample Data Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);