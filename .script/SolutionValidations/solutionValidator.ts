import { runCheckOverChangedFiles } from "./../utils/changedFilesValidator";
import * as logger from "./../utils/logger";
import { ExitCode } from "./../utils/exitCode";
import fs from "fs";
import { IsValidSolutionDomainsVerticals } from "./validDomainsVerticals";



// function to check if the solution is valid
export async function IsValidSolution(filePath: string): Promise<ExitCode> {
    IsValidSolutionDomainsVerticals(filePath);
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
        console.log(`Solution Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
    },
    // Callback function to handle final failure
    onFinalFailed: async () => {
        logger.logError("Please refer link https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/sentinel/sentinel-solutions.md?msclkid=9a240b52b11411ec99ae6736bd089c4a#categories-for-microsoft-sentinel-out-of-the-box-content-and-solutions for valid Domains and Verticals.");
    },
};

// Function call to start the check process
runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);


