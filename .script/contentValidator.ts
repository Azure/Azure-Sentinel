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
        const expectedText = "Microsoft Sentinel";

        // Read skip text from a file
        const skipTextFile = fs.readFileSync('./.script/skip-text.txt', "utf8");
        const skipTexts = skipTextFile.split("\n").filter(text => text.length > 0);

        // SEARCH & CHECK IF SKIP TEXT EXIST IN THE FILE
        let hasSkipText = false;
        let skipTextValue = '';
        for (const skipText of skipTexts) 
        {
            if (fileContent.includes(skipText)) 
            {
                hasSkipText = true;
                skipTextValue = skipText;
                break;
            }
        }

        // REPLACE ALL SKIP TEXT WITH BLANK
        let replacedFileContent = fileContent.replace(new RegExp(skipTexts.join('|'), 'gi'), '');

        // FIND IF AZURE SENTINEL TEXT PRESENT
        let hasAzureSentinelText = replacedFileContent.toLowerCase().includes(searchText.toLowerCase());
        if (hasAzureSentinelText) 
        {
            // VALIDATE AND THROW ERROR
            if (hasSkipText) 
            {
                throw new Error(`Please update text from '${searchText}' to '${expectedText}' except '${skipTextValue}' text in file '${filePath}'`);
            } 
            else 
            {
                throw new Error(`Please update text from '${searchText}' to '${expectedText}' in file '${filePath}'`);
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