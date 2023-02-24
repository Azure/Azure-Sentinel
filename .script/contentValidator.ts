import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function ValidateFileContent(filePath: string): Promise<ExitCode> 
{
    const ignoreFiles = ["azure-pipelines", "azureDeploy", "host.json", "proxies.json", "azuredeploy", "function.json"]
    const requiredFolderFiles = ["/Data/", "/data/", "/DataConnectors/", "/Data Connectors/", "createUiDefinition.json"]

    const hasIgnoredFile = ignoreFiles.filter(item => { return filePath.includes(item)}).length > 0
    const hasRequiredFolderFiles = requiredFolderFiles.filter(item => { return filePath.includes(item)}).length > 0

    if (!hasIgnoredFile && hasRequiredFolderFiles) 
    {
        const searchText = "Azure Sentinel";
        const expectedText = "Microsoft Sentinel";

        const tagsList = fs.readFileSync('./.script/validate-tag-text.txt', "utf8");
        const validTags = tagsList.split("\n").filter(tag => tag.length > 0);

        const fileContent = fs.readFileSync(filePath, "utf8");
        var fileContentObj = JSON.parse(fileContent);

        for (const tagName of validTags) 
        {
            if (filePath.includes("createUiDefinition.json"))
            {
                var tagContent = fileContentObj["parameters"]["config"]["basics"][tagName];
            }
            else
            {
                var tagContent = fileContentObj[tagName];
            }

            if (tagContent)
            {
                let hasAzureSentinelText = tagContent.toLowerCase().includes(searchText.toLowerCase());
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