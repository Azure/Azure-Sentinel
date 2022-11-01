import fs from "fs";
import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";

export async function IsValidDataConnectorSchema(filePath: string): Promise<ExitCode> {

  const content = fs.readFileSync(filePath, "utf8");

  //get http or https links from the content
  const links = content.match(/https?:\/\/[^\s]+/g);

  if (links) {
    for (const link of links) {
      console.log(link);
      //check if the link is valid
      const isValid = await isValidLink(link);
      if (!isValid) {
        logger.logError(`Invalid link: ${link}`);
        throw new Error();
      }
    }
 
  }

  //create a function to check if the link is valid
  async function isValidLink(link: string): Promise<boolean> {
    try {
            var xhr = new XMLHttpRequest();
            xhr.open('HEAD', link, false);
            xhr.send();
            console.log(xhr.status);
            return xhr.status==200;
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
    return IsValidDataConnectorSchema(filePath);
  },
  onExecError: async (e: any, filePath: string) => {
    console.log(`HyperLink Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
  },
  onFinalFailed: async () => {
    logger.logError("An error occurred, please open an issue");
  },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);