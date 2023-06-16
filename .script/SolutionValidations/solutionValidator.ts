import { runCheckOverChangedFiles } from "./../utils/changedFilesValidator";
import * as logger from "./../utils/logger";
import { ExitCode } from "./../utils/exitCode";
import { IsValidSolutionDomainsVerticals } from "./validDomainsVerticals";
import { IsValidSupportObject } from "./validSupportObject";
import { IsValidBrandingContent } from "./validMSBranding";
import { IsValidSolutionID } from "./validSolutionID";
import { MainTemplateDomainVerticalValidationError, MainTemplateSupportObjectValidationError, InvalidFileContentError, InvalidSolutionIDValidationError } from "../utils/validationError";



// function to check if the solution is valid
export async function IsValidSolution(filePath: string): Promise<ExitCode> {
    IsValidSolutionDomainsVerticals(filePath);
    IsValidSupportObject(filePath);
    IsValidBrandingContent(filePath);
    IsValidSolutionID(filePath);
    return ExitCode.SUCCESS;
}


// Array to store file type suffixes for the check
let fileTypeSuffixes = ["json"];

// Array to store file path folder prefixes for the check
let filePathFolderPrefixes = ["Solutions"];

// Array to store file kinds for the check
let fileKinds = ["Added", "Modified"];

// Options object to pass to the runCheckOverChangedFiles function
let CheckOptions = {
    // Callback function to check if a file is valid
    onCheckFile: (filePath: string) => {
        return IsValidSolution(filePath);
    },
    // Callback function to handle errors during execution
    onExecError: async (e: any, filePath: string) => {
        console.log(`Solution Validation Failed. File path: ${filePath} \nError message: ${e.message}`);
        if (e instanceof MainTemplateDomainVerticalValidationError) {
            logger.logError("Please refer link https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/sentinel/sentinel-solutions.md?msclkid=9a240b52b11411ec99ae6736bd089c4a#categories-for-microsoft-sentinel-out-of-the-box-content-and-solutions for valid Domains and Verticals.");
        } else if (e instanceof MainTemplateSupportObjectValidationError) {
            logger.logError("Validation for Support object failed in Main Template.");
        }
        else if (e instanceof InvalidFileContentError) {
            logger.logError("Validation for Microsoft Sentinel Branding Failed.");
        }
        else if (e instanceof InvalidSolutionIDValidationError) {
            logger.logError("Validation for Solution ID Failed.");
        }
    },
    // Callback function to handle final failure
    onFinalFailed: async () => {
        logger.logError("Validation failed, please fix the errors.");
    },

};

// Function call to start the check process
runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);


