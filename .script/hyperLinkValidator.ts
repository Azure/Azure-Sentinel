import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import { GetPRDetails } from "./utils/gitWrapper";
import * as logger from "./utils/logger";

export async function ValidateHyperlinks(filePath: string): Promise<ExitCode> 
{
    let splitPath = filePath.split("/")
    if (splitPath[0] === "Solutions")
    {
        let dataFolderName = splitPath[2] === "Data" || splitPath[2] === "data" ? splitPath[2] : null
        let dataConnectorFolderName = splitPath[2] === "DataConnectors" || splitPath[2] === "Data Connectors" ? splitPath[2] : null
        if (dataFolderName == null && dataConnectorFolderName == null) 
        {
            console.log(`Skipping Hyperlink validation for file path : '${filePath}' as change is not in 'Data' and/or 'Data Connectors' folder`)
            return ExitCode.SUCCESS;
        }

        //IGNORE BELOW FILES
        if (filePath.includes("azuredeploy") || filePath.includes("host.json") || filePath.includes("proxies.json") || filePath.includes("function.json") || filePath.includes("requirements.txt") || filePath.includes(".py") || filePath.includes(".ps1"))
        {
            console.log(`Skipping Hyperlink validation for file path : '${filePath}'`)
            return ExitCode.SUCCESS;
        }

        const content = fs.readFileSync(filePath, "utf8");
        const links = content.match(/(http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])+/g);
        if (links) 
        {
            var invalidLinks = new Array();
            for (var link of links) 
            {
                link = link.replace(/["']/g, "")

                //check if the link is valid
                const isValid = await isValidLink(link);
                if (!isValid) 
                {
                    // CHECK IF LINK IS A GITHUB LINK
                    var isGithubLink = false;
                    if (link.includes('https://raw.githubusercontent.com') || link.includes('https://github.com'))
                    {
                        isGithubLink = true;
                    }

                    if (link.includes('&&sudo'))
                    {
                        //IGNORE HYPERLINKS WHICH HAS &&SUDO IN IT
                        isGithubLink = false;
                    }

                    if (isGithubLink)
                    {
                        const pr = await GetPRDetails();
                        if (typeof pr === "undefined") 
                        {
                            console.log("Azure DevOps CI for a Pull Request wasn't found. If issue persists - please open an issue");
                            return ExitCode.ERROR;
                        }

                        const changedFiles = await pr.diff();
                        const imageIndex = link.lastIndexOf('/');
                        const imageName = link.substring(imageIndex + 1);                        
                        const searchedFiles = changedFiles.map(change => change.path).filter(changedFilePath => changedFilePath.indexOf(imageName) > 0);
                        var searchedFilesLength = searchedFiles.length;
                        if (searchedFilesLength <= 0)
                        {
                            invalidLinks.push(link);
                        }
                        else
                        {
                            console.log(`Skipping Hyperlink validation for '${link}' in file path : '${filePath}'`);
                        }
                    }
                    else
                    {
                        console.log(`Skipping Hyperlink validation for '${link}' in file path : '${filePath}'`);
                    }
                }
            }

            if (invalidLinks.length > 0)
            {
                var errorMessage= `File '${filePath}' has a total of '${invalidLinks.length}' broken hyperlinks. Please review and rectify the following hyperlinks: \n ${invalidLinks}`
                throw new Error(errorMessage.replace(",", "\n"));
            }
        }

        return ExitCode.SUCCESS
    }
    else
    {
        console.log(`Skipping Hyperlink validation for file path : '${filePath}' as change is not in 'Solutions' folder`)
        return ExitCode.SUCCESS
    }

  //create a function to check if the link is valid
    async function isValidLink(link: string): Promise<boolean> 
    {
        try 
        {
            //import XMLHttpRequest from "xmlhttprequest"
            const XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
            const request = new XMLHttpRequest();
            request.open("GET", link, false);
            request.setRequestHeader("X-Requested-With", "XMLHttpRequest");
            request.timeout = 5000;
            request.ontimeout = function () { return false; }
            request.send();

            if (request.status == 404)
            {
                return false;
            }
            else if(request.status == 302)
            {
                var redirectResponse = request.getResponseHeader("Location")
                return (redirectResponse.includes("www.google.com") || redirectResponse.includes("www.bing.com") || redirectResponse.includes("404 - Page not found")) ? false : true;
            }
            else if (request.status == 0)
            {
                // TIMEOUT STATUS IS 0
                return false;
            }
            else 
            {
                var responseContent = request.responseText

                if (responseContent != null && (responseContent.includes("404! Not Found!") || responseContent.includes("404 Not Found") || responseContent.includes("404 error") || responseContent.includes("404 - Page not found"))) {
                    return false;
                }
            }

            return true;
        } catch (error) 
        {
            console.log(error);
            return false;
        }
    }
}

let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["DataConnectors", "Data Connectors", "Solutions"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath: string) => {
        return ValidateHyperlinks(filePath)
    },
    onExecError: async (e: any) => {
        logger.logError(`${e}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);