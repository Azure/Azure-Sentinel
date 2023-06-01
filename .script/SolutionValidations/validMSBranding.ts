import { InvalidFileContentError } from "./../utils/validationError";
import { ExitCode } from "../utils/exitCode";
import fs from "fs";

type AttributeConfig = {
    mainTemplateAttributes: string[];
    createUIDefinitionAttributes: string[];
};

const attributeConfig: AttributeConfig = {
    mainTemplateAttributes: ["descriptionMarkdown", "description"],
    createUIDefinitionAttributes: ["text", "description"],
};

export function IsValidBrandingContent(filePath: string): ExitCode {
    // Skip validation if file path contains "SentinelOne"
    if (filePath.includes("SentinelOne")) {
        return ExitCode.SUCCESS;
    }

    const errors: string[] = [];

    // check if the file is mainTemplate.json or createUiDefinition.json
    if (filePath.endsWith("mainTemplate.json")) {
        validateFileContent(filePath, attributeConfig.mainTemplateAttributes, errors);
    } else if (filePath.endsWith("createUiDefinition.json")) {
        validateFileContent(filePath, attributeConfig.createUIDefinitionAttributes, errors);
    } else {
        console.warn(
            `Could not identify JSON file as mainTemplate.json or createUiDefinition.json. Skipping. File path: ${filePath}`
        );
    }

    // Throw a single error with all the error messages concatenated
    if (errors.length > 0) {
        throw new InvalidFileContentError(errors.join("\n"));
    }

    // Return success code after completion of the check
    return ExitCode.SUCCESS;
}

function validateFileContent(filePath: string, attributeNames: string[], errors: string[]): void {
    const fileContent = fs.readFileSync(filePath, "utf8");
    const jsonContent = JSON.parse(fileContent);

    traverseAttributes(jsonContent, attributeNames, "", errors);
}

function traverseAttributes(jsonContent: any, attributeNames: string[], currentPath: string, errors: string[]): void {
    for (const key in jsonContent) {
        if (jsonContent.hasOwnProperty(key)) {
            const attributeValue = jsonContent[key];
            const attributePath = currentPath ? `${currentPath}.${key}` : key;

            if (attributeNames.includes(key) && typeof attributeValue === "string") {
                validateAttribute(attributeValue, attributePath, errors);
            }
            if (typeof attributeValue === "object" && attributeValue !== null) {
                traverseAttributes(attributeValue, attributeNames, attributePath, errors);
            }
        }
    }
}

function validateAttribute(attributeValue: string, attributePath: string, errors: string[]): void {
    console.log(`Validating text in '${attributePath}': ${attributeValue}`);

    const sentinelRegex = /(?<!Microsoft\s)(?<!-)\bSentinel\b/g;
    let match;
    while ((match = sentinelRegex.exec(attributeValue))) {
        const word = match[0];
        const error = `Inaccurate product branding used in '${attributePath}'. Use "Microsoft Sentinel" instead of "${word}"`;
        errors.push(error);
    }
}
