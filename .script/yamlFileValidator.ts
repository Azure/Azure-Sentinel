import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import yaml from "js-yaml";
import fs from "fs";
import * as logger from "./utils/logger";

export async function IsValidYamlFile(filePath: string): Promise<ExitCode> {
  yaml.safeLoad(fs.readFileSync(filePath, "utf8"));
  return ExitCode.SUCCESS;
}

let fileTypeSuffixes = ["yaml", "yml"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsValidYamlFile(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Incorrect yaml file. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  }
};

runCheckOverChangedFiles(CheckOptions, fileTypeSuffixes);
