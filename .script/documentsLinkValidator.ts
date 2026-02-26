import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import { ExitCode } from "./utils/exitCode.js";
import fs from "fs";
import * as logger from "./utils/logger.js";

export async function IsFileContainsLinkWithLocale(filePath: string): Promise<ExitCode> {
  const content = fs.readFileSync(filePath, "utf8");
  if (/(https:\/\/docs.microsoft.com|https:\/\/azure.microsoft.com)(\/[a-z]{2}-[a-z]{2})/i.test(content)) {
      throw new Error();
  }
  return ExitCode.SUCCESS;
}

let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsFileContainsLinkWithLocale(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Documentation links should not include locale: ${filePath}, ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  }
};

runCheckOverChangedFiles(CheckOptions, fileKinds);
