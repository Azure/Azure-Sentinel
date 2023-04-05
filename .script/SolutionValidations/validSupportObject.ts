import { MainTemplateValidationError } from "./../utils/validationError";
import * as logger from "./../utils/logger";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";

// function to check if the support object in the mainTemplate.json file is valid
export function IsValidSupportObject(filePath: string): ExitCode {

    // check if the file is a mainTemplate.json file
    if (filePath.endsWith("mainTemplate.json")) {
        // read the content of the file
        let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

        // check if the file has a "resources" field
        if (!jsonFile.hasOwnProperty("resources")) {
            console.warn(`No "resources" field found in the file. Skipping file path: ${filePath}`);
            return ExitCode.SUCCESS;
        }

        // get the resources from the file
        let resources = jsonFile.resources;

        // filter resources that have type "Microsoft.OperationalInsights/workspaces/providers/metadata"
        const filteredResource = resources.filter(function (resource: { type: string; }) {
            return resource.type === "Microsoft.OperationalInsights/workspaces/providers/metadata";
        });
        if (filteredResource.length > 0) {
            filteredResource.forEach((element: { hasOwnProperty: (arg0: string) => boolean; properties: { hasOwnProperty: (arg0: string) => boolean; support: any; }; }) => {
                // check if the resource has a "properties" field
                if (element.hasOwnProperty("properties") === true) {
                    // check if the "properties" field has a "support" field
                    if (element.properties.hasOwnProperty("support") === true) {
                        const support = element.properties.support;

                        // check if the support object has a "name" field
                        if (!support.hasOwnProperty("name")) {
                            throw new MainTemplateValidationError("The support object must include a 'name' field.");
                        }
                        // check if the support object has an "email" field
                        if (!support.hasOwnProperty("email")) {
                            throw new MainTemplateValidationError("The support object must include an 'email' field.");
                        }
                        // check if the support object has a "link" field
                        if (!support.hasOwnProperty("link")) {
                            throw new MainTemplateValidationError("The support object must include a 'link' field.");
                        }
                    } else {
                        throw new MainTemplateValidationError("The support object must be included in the mainTemplate.json file.");
                    }
                }
            });
        }

        // If the file is not identified as a main template, log a warning message
    } else {
        console.warn(`Could not identify json file as a Main Template. Skipping File path: ${filePath}`);
    }

    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}
