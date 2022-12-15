import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function ValidateFileContent(filePath: string): Promise<ExitCode> 
{
    // CHECK IF FILE CONTAINS "Azure Sentinel". IF YES THEN ERROR ELSE SUCCESS. THIS IS BECAUSE WE NOW WORK ON
    if (!filePath.includes("azure-pipelines"))
    {
        console.log(`Current File ${filePath}`)
        const fileContent = fs.readFileSync(filePath, "utf8");
        const searchText = "Azure Sentinel"
        const replaceWithText = "Microsoft Sentinel"
        const hasAzureSentinelText = fileContent.toLowerCase().includes(searchText.toLowerCase());
        
        if (hasAzureSentinelText)
        {
            throw new Error(`'${searchText}' text is not allowed. Please replace '${searchText}' text with '${replaceWithText}' in file '${filePath}'`);
        }
    }
    return ExitCode.SUCCESS;
}

let fileTypeSuffixes = ["json", "txt", "md", "yaml", "yml"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath: string) => {
        return ValidateFileContent(filePath)
    },
    onExecError: async (e: any) => {
        logger.logError(`Content Validation check Failed: ${e.message}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes);