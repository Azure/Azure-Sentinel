import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import * as logger from "./utils/logger";
import { ExitCode } from "./utils/exitCode";
import fs from "fs";
import { MainTemplateValidationError } from "./utils/validationError";

const validDomains = [
    "Application",
    "Cloud Provider",
    "Compliance",
    "DevOps",
    "Identity",
    "Internet of Things (IoT)",
    "IT Operations",
    "Migration",
    "Networking",
    "Platform",
    "Security - Others",
    "Security - Threat Intelligence",
    "Security - Threat Protection",
    "Security – 0-day Vulnerability",
    "Security – Automation (SOAR)",
    "Security – Cloud Security",
    "Security – Information Protection",
    "Security – Insider Threat",
    "Security – Network",
    "Security – Vulnerability Management",
    "Storage",
    "Training and Tutorials",
    "User Behavior (UEBA)",
];

const validVerticals = [
    "Aeronautics",
    "Education",
    "Finance",
    "Healthcare",
    "Manufacturing",
    "Retail",
];

export async function IsValidSolution(filePath: string): Promise<ExitCode> {
    let jsonFile = JSON.parse(fs.readFileSync(filePath, "utf8"));

    if (isPotentialMainTemplate(filePath) && jsonFile.hasOwnProperty("categories")) {
        let categories = jsonFile.categories;

        if (categories.hasOwnProperty("domains")) {
            let domains = categories.domains;
            for (const domain of domains) {
                if (!validDomains.includes(domain)) {
                    throw new MainTemplateValidationError(`Invald Domain ${domain} provided`);
                }
            }
        }

        if (categories.hasOwnProperty("verticals")) {
            let verticals = categories.verticals;
            for (const vertical of verticals) {
                if (!validVerticals.includes(vertical)) {
                    throw new MainTemplateValidationError(`Invald Vertical ${vertical} provided`);
                }
            }
        }
    }
    else {
        console.warn(`Could not identify json file as a Main Template. Skipping File path: ${filePath}`);
    }

    return ExitCode.SUCCESS;
}

function isPotentialMainTemplate(filePath: string) {
    if (filePath.endsWith("mainTemplate.json")) {
        return true;
    }
    return false;
}

let fileTypeSuffixes = ["json"];
let filePathFolderPrefixes = ["Solutions","Package"];
let fileKinds = ["Added", "Modified"];
let CheckOptions = {
    onCheckFile: (filePath: string) => {
        return IsValidSolution(filePath);
    },
    onExecError: async (e: any, filePath: string) => {
        console.log(`Main Template Validation Failed. File path: ${filePath}. Error message: ${e.message}`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    },
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
