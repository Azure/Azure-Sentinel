import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function ValidateFileContent(filePath: string): Promise<ExitCode> 
{
    // CHECK IF FILE CONTAINS "Azure Sentinel". IF YES THEN ERROR ELSE SUCCESS. THIS IS BECAUSE WE NOW WORK ON
    const fileContent = fs.readFileSync(filePath, "utf8");
    const searchText = "Azure Sentinel"
    const replaceWithText = "Microsoft Sentinel"
    const hasAzureSentinelText = fileContent.toLowerCase().includes(searchText.toLowerCase());
    console.log("result ${result}")
    if (hasAzureSentinelText)
    {
        logger.logError(`'${searchText}' text is not allowed. Please replace '${searchText}' text with '${replaceWithText}' in file '${filePath}'`)
        return ExitCode.ERROR;
    }

    return ExitCode.SUCCESS;
}

let fileTypeSuffixes = ["json", "txt", "md", "yaml", "yml"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath: string) => {
        return ValidateFileContent(filePath)
    },
    onExecError: async () => {
        logger.logError(`Content Validation Failed.`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes);