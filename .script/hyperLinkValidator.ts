import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";




export async function ValidateHyperlinks(filePath: string): Promise<ExitCode> {

  const content = fs.readFileSync(filePath, "utf8");
  console.log(content)
  //get http or https links from the content
  //const links = content.match(/https?:\/\/[^\s]+/g);
  const links = content.match(/(http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])/);
  if (links) {
    var invalidLinks = new Array();
    for (var link of links) {
      link = link.replace(/["']/g, "")

      //check if the link is valid
      const isValid = await isValidLink(link);
      if (!isValid) {
        //logger.logError(`Invalid link: ${link}`);
        //throw new Error();
        invalidLinks.push(link)
      }
    }

    if (invalidLinks.length > 0) {
      logger.logError(`List of Invalid link: ${invalidLinks}`);
      throw new Error();
    }
  }

  //create a function to check if the link is valid
  async function isValidLink(link: string): Promise<boolean> {
    try {
      //import XMLHttpRequest from "xmlhttprequest"
      console.log("link to valid is ", link)
      const XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
      const request = new XMLHttpRequest();
      request.open("GET", link, false);
      request.send();
      console.log(request.status);
      console.log(`Request is ${request}`);
      return request.status !== 404;
    } catch (error) {
      console.log('invalid link')
      console.log(error);
      return false;
    }
  }    
  return ExitCode.SUCCESS;
  }



let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["DataConnectors","Solutions"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
  onCheckFile: (filePath: string) => {
    return ValidateHyperlinks(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`HyperLink Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);