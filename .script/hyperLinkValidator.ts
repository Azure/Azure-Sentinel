import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import { GetPRDetails } from "./utils/gitWrapper";
import gitP, { SimpleGit } from 'simple-git/promise';
import * as logger from "./utils/logger";

const workingDir: string = process.cwd();
const git: SimpleGit = gitP(workingDir);

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

        console.log('===========start=============')
        const pr = await GetPRDetails();

        if (typeof pr === "undefined") {
            console.log("Azure DevOps CI for a Pull Request wasn't found. If issue persists - please open an issue");
            return ExitCode.ERROR;
        }

        const content = fs.readFileSync(filePath, "utf8");

        //get http or https links from the content
        //const links = content.match(/https?:\/\/[^\s]+/g);
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
                    if (link.includes('https://raw.githubusercontent.com'))
                    {
                        console.log("inside of githubusercontent")
                        // REPLACE master IN URL WITH BRANCH NAME AND CHECK IF THE URL IS IN THE PR. IF STILL NOT VALID THROW ERROR.
                        isGithubLink = true;
                    }
                    else if (link.includes('https://github.com'))
                    {
                        console.log("inside of github")
                        // REPLACE master IN URL WITH BRANCH NAME AND CHECK IF THE URL IS IN THE PR. IF STILL NOT VALID THROW ERROR.
                        isGithubLink = true;
                    }

                    if (isGithubLink)
                    {
                        console.log("inside of if condition")
                        var targetBranch: string = pr.targetBranch;
                        var sourceBranch: string = pr.sourceBranch;
                
                        console.log(`Target Branch is ${targetBranch}, Source Branch is ${sourceBranch}`)
                        let options = [pr.targetBranch, pr.sourceBranch, filePath];
                        let changedFiles = await git.diff(options);
                        console.log(`changedFiles is ${changedFiles}`)
                        console.log('===========end=============')
                        const imageIndex = link.lastIndexOf('/')
                        const imageName = link.substring(imageIndex + 1)
                        const filterChangedFiles1 = changedFiles.map(change => change.path).filter(changedFilePath => changedFilePath);
                        console.log(`filtered files1 are ${filterChangedFiles1}`)
                        const filterChangedFiles2 = changedFiles.map(change => change.path).filter(changedFilePath => changedFilePath.indexOf(imageName) > 0);
                        console.log(`filtered files2 are ${filterChangedFiles2}`)
                        invalidLinks.push(link);
                    }
                }
            }

            if (invalidLinks.length > 0)
            {
                //console.log(`Please update below given hyperlink(s) as they seems to be broken:`)
                invalidLinks.forEach(l => {
                    logger.logError(`\n ${l}`);
                });

                throw new Error(`In file '${filePath}', there are total '${invalidLinks.length}' broken links. Please rectify below given hyperlinks: \n ${invalidLinks}`);
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
    onExecError: async () => {
        logger.logError(`HyperLink Validation Failed.`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);