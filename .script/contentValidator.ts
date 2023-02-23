import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function ValidateFileContent(filePath: string): Promise<ExitCode> 
{
    // WE SHOULD SKIP ANY FILE WHICH IS LISTED BELOW
    const isExcludedFile = (filePath.includes("azure-pipelines")
        || filePath.includes("azureDeploy")
        || filePath.includes("host.json")
        || filePath.includes("proxies.json")
        || filePath.includes("azuredeploy")
        || filePath.includes("function.json"));

    // WE SHOULD CHECK ONLY IN BELOW FOLDERS
    const isIncludedFolderFile = (filePath.includes("/Data/") 
        || filePath.includes("/data/")
        || filePath.includes("/Data Connectors/") 
        || filePath.includes("/DataConnectors/")
        || filePath.includes("createUiDefinition.json"));

    if (!isExcludedFile && isIncludedFolderFile)
    {
        console.log("file name " + filePath);
        const fileContent = fs.readFileSync(filePath, "utf8");
        const searchText = "Azure Sentinel";
        const expectedText = "Microsoft Sentinel";

        // Read skip text from a file
        const skipTextFile = fs.readFileSync('./.script/validate-tag-text.txt', "utf8");
        const validTags = skipTextFile.split("\n").filter(tag => tag.length > 0);
        console.log(fileContent);
        // SEARCH & CHECK IF SKIP TEXT EXIST IN THE FILE
        //var fileContentObj = JSON.parse(fileContent.replace(/\\/g, '\\\\'));
        var fileContentStringify = JSON.stringify(fileContent);
        console.log(fileContentStringify)
        var fileContentObj = JSON.parse(fileContentStringify);

        for (const tagName of validTags) 
        {
            if (filePath.includes("createUiDefinition.json"))
            {
                var tagContent = fileContentObj["parameters"]["config"]["basics"]["description"];
            }
            else
            {
                var tagContent = fileContentObj[tagName];
            }

            if (tagContent)
            {
                let hasAzureSentinelText = tagContent.toLowerCase().includes(searchText.toLowerCase());
                console.log("inside of if");
                if (hasAzureSentinelText) {
                    throw new Error(`Please update text from '${searchText}' to '${expectedText}' in '${tagName}' tag in the file '${filePath}'`);
                }
            }
        }
    }
    return ExitCode.SUCCESS;
}

let fileTypeSuffixes = ["json"];
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