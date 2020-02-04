import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import fs from "fs";
import * as logger from "./utils/logger";

export async function IsValidJsonFile(filePath: string): Promise<ExitCode> {
  JSON.parse(fs.readFileSync(filePath, "utf8"));
  return ExitCode.SUCCESS;
}

let fileTypeSuffixes = ["json"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidJsonFile(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Incorrect Json file. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  }
};

runCheckOverChangedFiles(CheckOptions, fileTypeSuffixes);
