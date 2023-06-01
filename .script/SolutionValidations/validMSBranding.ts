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
        console.warn(`Could not identify JSON file as mainTemplate.json or createUiDefinition.json. Skipping. File path: ${filePath}`);
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

    traverseAttributes(jsonContent, attributeNames, filePath, errors);
}

function traverseAttributes(jsonContent: any, attributeNames: string[], filePath: string, errors: string[]): void {
    for (const key in jsonContent) {
        if (jsonContent.hasOwnProperty(key)) {
            const attributeValue = jsonContent[key];
            if (attributeNames.includes(key) && typeof attributeValue === "string") {
                validateAttribute(attributeValue, key, filePath, errors);
            }
            if (typeof attributeValue === "object" && attributeValue !== null) {
                traverseAttributes(attributeValue, attributeNames, filePath, errors);
            }
        }
    }
}

function validateAttribute(attributeValue: string, attributeName: string, filePath: string, errors: string[]): void {
    console.log(`Validating text in '${attributeName}': ${attributeValue}`);

    const sentinelRegex = /(?<!Microsoft\s)(?<!-)\bSentinel\b/g;
    let match;
    while ((match = sentinelRegex.exec(attributeValue))) {
        const word = match[0];
        const index = match.index;
        const errorIndex = getIndexInOriginalFile(attributeValue, index, filePath);
        errors.push(`Inaccurate product branding used in '${attributeName}' at index ${errorIndex + 1}. Use "Microsoft Sentinel" instead of "${word}"`);
    }
}

function getIndexInOriginalFile(attributeValue: string, index: number, filePath: string): number {
    const fileContent = fs.readFileSync(filePath, "utf8");
    const startIndex = fileContent.indexOf(attributeValue);
    const substringBeforeMatch = attributeValue.slice(0, index);
    const substringBeforeMatchIndex = attributeValue.indexOf(substringBeforeMatch);
    const wordIndexInFile = startIndex + substringBeforeMatchIndex;
    return wordIndexInFile + 1;
}
