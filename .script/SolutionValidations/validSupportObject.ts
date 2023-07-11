import { MainTemplateSupportObjectValidationError } from "./../utils/validationError";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";

// function to check if the solution has a valid support object
export function IsValidSupportObject(filePath: string): ExitCode {

    // check if the file is a mainTemplate.json file
    if (filePath.endsWith("mainTemplate.json")) {
        // read the content of the file
        let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

        // check if the file has a "resources" field
        if (!jsonFile.hasOwnProperty("resources")) {
            throw new MainTemplateSupportObjectValidationError(`No "resources" field found in the file. File path: ${filePath}`);
        }

        // get the resources from the file
        let resources = jsonFile.resources;

        // filter resources that have type "Microsoft.OperationalInsights/workspaces/providers/metadata"
        const filteredResource = resources.filter(function (resource: { type: string }) {
            return resource.type === "Microsoft.OperationalInsights/workspaces/providers/metadata" ||
                resource.type === "Microsoft.OperationalInsights/workspaces/providers/contentPackages";
        });

        if (filteredResource.length > 0) {
            filteredResource.forEach((element: { hasOwnProperty: (arg0: string) => boolean; properties: { hasOwnProperty: (arg0: string) => boolean; support: { hasOwnProperty: (arg0: string) => boolean; name: any; email: any; link: any; }; }; }) => {
                // check if the resource has a "properties" field
                if (element.hasOwnProperty("properties") === true) {
                    // check if the "properties" field has a "support" field
                    if (element.properties.hasOwnProperty("support") === true) {
                        const support = element.properties.support;

                        if (!support.hasOwnProperty("name")) {
                            throw new MainTemplateSupportObjectValidationError(`The support object must have a "name" field.`);
                        } else if (support.name.trim() === "") {
                            throw new MainTemplateSupportObjectValidationError(`The support object "name" field value cannot be empty.`);
                        } else if ((!support.hasOwnProperty("email") || support.email.trim() === "") && (!support.hasOwnProperty("link") || support.link.trim() === "")) {
                            throw new MainTemplateSupportObjectValidationError(`The support object must have either "email" or "link" field and the value should not be empty.`);
                        } else {
                            // check if the email is valid
                            if (support.hasOwnProperty("email") && support.email.trim() !== "") {
                                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                                if (!emailRegex.test(support.email)) {
                                    throw new MainTemplateSupportObjectValidationError(`Invalid email format for support email: ${support.email}`);
                                }
                            }

                            // check if the link is a valid url
                            if (support.hasOwnProperty("link") && support.link.trim() !== "") {
                                const linkRegex = /^https?:\/\/\S+$/;
                                if (!linkRegex.test(support.link)) {
                                    throw new MainTemplateSupportObjectValidationError(`Invalid url format for support link: ${support.link}`);
                                }
                            }
                        }
                    } else {
                        throw new MainTemplateSupportObjectValidationError(`The "properties" field must have "support" field.`);
                    }
                }
            });
        }
        else {
            throw new MainTemplateSupportObjectValidationError(`There are no metadata resoruces found in the file. File path: ${filePath}`);
        }
        // If the file is not identified as a main template, log a warning message
    } else {
        console.warn(`Could not identify json file as a Main Template. Skipping File path: ${filePath}`);
    }

    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}
