import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function ValidateFileContent(filePath: string): Promise<ExitCode> 
{
    if (!filePath.includes("azure-pipelines"))
    {
        const fileContent = fs.readFileSync(filePath, "utf8");
        const searchText = "Azure Sentinel";

        // DEFINE SKIP TEXT TO BE SEARCHED
        const searchTargetProductAzureSentinelTag = '"targetProduct": "Azure Sentinel"';
        const searchAzureSentinelCommunityGithubText = 'Azure Sentinel Community Github';

        // SEARCH & CHECK IF SKIP TEXT EXIST IN THE FILE
        const hasTargetProductAzureSentinel = fileContent.includes(searchTargetProductAzureSentinelTag);
        const hasAzureSentinelCommunityGithubText = fileContent.includes(searchAzureSentinelCommunityGithubText);

        // REPLACE ALL SKIP TEXT WITH BLANK
        const skipText = [searchAzureSentinelCommunityGithubText, searchTargetProductAzureSentinelTag];
        let replacedFileContent = fileContent.replace(new RegExp(skipText.join('|'), 'gi'), '');

        // FIND IF AZURE SENTINEL TEXT PRESENT
        let hasAzureSentinelText = replacedFileContent.toLowerCase().includes(searchText.toLowerCase());
        if (hasAzureSentinelText)
        {
            // VALIDATE AND THROW ERROR
            CustomizedException(hasTargetProductAzureSentinel, searchTargetProductAzureSentinelTag, searchText);
            CustomizedException(hasAzureSentinelCommunityGithubText, searchAzureSentinelCommunityGithubText, searchText);

            throw new Error(`Please update text from '${searchText}' to 'Microsoft Sentinel' in file '${filePath}'`);
        }
    }
    return ExitCode.SUCCESS;

    function CustomizedException(hasSkipText: any, exceptText: any, searchText: any): void
    {
        if (hasSkipText) {
            throw new Error(`Please update text from '${searchText}' to 'Microsoft Sentinel' except '${exceptText}' text in file '${filePath}'`);
        }
    }
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