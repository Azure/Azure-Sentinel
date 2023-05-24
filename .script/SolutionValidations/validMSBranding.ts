import { InvalidFileContentError } from "./../utils/validationError";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";

export function IsValidBrandingContent(filePath: string): ExitCode {

    // check if the file is mainTemplate.json or createUiDefinition.json
    if (filePath.endsWith("mainTemplate.json") || filePath.endsWith("createUiDefinition.json")) {
        // read the content of the file
        let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

        // check if the file content contains the word "Sentinel" without "Microsoft" preceding it
        const fileContent = JSON.stringify(jsonFile);
        const sentinelRegex = /(?<!Microsoft )Sentinel\b/g;
        const sentinelMatches = fileContent.match(sentinelRegex);

        if (sentinelMatches && sentinelMatches.length > 0) {
            for (const match of sentinelMatches) {
                if (match !== 'Microsoft Sentinel') {
                    throw new InvalidFileContentError(`The string "${match}" is invalid. It should be "Microsoft Sentinel". File path: ${filePath}`);
                }
            }
        }

        // If the file is not identified correctly, log a warning message
    } else {
        console.warn(`Could not identify JSON file as mainTemplate.json or createUiDefinition.json. Skipping. File path: ${filePath}`);
    }

    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}
