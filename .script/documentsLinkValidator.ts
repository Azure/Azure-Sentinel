import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import fs from "fs";
import * as logger from "./utils/logger";

export async function IsFileContainsLinkWithLocale(filePath: string): Promise<ExitCode> {
  const content = fs.readFileSync(filePath, "utf8");
  if (content.test(/(https:\/\/docs.microsoft.com|https:\/\/azure.microsoft.com)(\/[a-z]{2}-[a-z]{2})/i)) {
      return ExitCode.SUCCESS;
  }
  return ExitCode.ERROR;
}

let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return IsFileContainsLinkWithLocale(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`Documentation links should not include locale: ${filePath}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  }
};

runCheckOverChangedFiles(CheckOptions, fileKinds);
