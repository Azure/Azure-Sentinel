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
        const searchTargetProductAzureSentinelTag = '"targetProduct": "Azure Sentinel"';
        const replaceTextTargetProductTag = /"targetProduct": "Azure Sentinel"/gi

        const hasTargetProductAzureSentinel = fileContent.includes(searchTargetProductAzureSentinelTag);
        const replacedFileContent = fileContent.replace(replaceTextTargetProductTag, "");
        const hasAzureSentinelText = replacedFileContent.toLowerCase().includes(searchText.toLowerCase());

        if (hasAzureSentinelText)
        {
            if (hasTargetProductAzureSentinel)
            {
                throw new Error(`Please update text from 'Azure Sentinel' to 'Microsoft Sentinel' except 'targetProduct' key-value pair in file '${filePath}'`);
            }
            else
            {
                throw new Error(`Please update text from 'Azure Sentinel' to 'Microsoft Sentinel' in file '${filePath}'`);
            }
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
