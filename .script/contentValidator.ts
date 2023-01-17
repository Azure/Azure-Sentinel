import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function ValidateFileContent(filePath: string): Promise<ExitCode> 
{
    if (!filePath.includes("azure-pipelines"))
    {
        const fileContent = fs.readFileSync(filePath, "utf8");
        const searchText = "Azure Sentinel"
        const replaceText = '"targetProduct": "Azure Sentinel"';

        const hasTargetProductAzureSentinel = fileContent.includes(replaceText);
        const replacedFileContent = fileContent.replace(replaceText, "");
        const hasAzureSentinelText = replacedFileContent.toLowerCase().includes(searchText.toLowerCase());

        console.log(`hasAzureSentinelText is ${hasAzureSentinelText}`)
        if (hasAzureSentinelText)
        {
            if (hasTargetProductAzureSentinel)
            {
                console.log(`Inside of if condition - has tag`);
                throw new Error(`Please update text from 'Azure Sentinel' to 'Microsoft Sentinel' except targetProduct key-value pair in file '${filePath}'`);
            }
            else
            {
                console.log(`Inside of if condition - no tag`);
                throw new Error(`Please update text from 'Azure Sentinel' to 'Microsoft Sentinel' in file '${filePath}'`);
            }
        }
        else
        {
            console.log(`Inside of else condition`)
        }
    }
    return ExitCode.SUCCESS;
}

let fileTypeSuffixes = ["json", "txt", "md", "yaml", "yml", "py"];
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