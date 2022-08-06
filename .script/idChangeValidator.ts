import { runCheckOverChangedFiles } from "./utils/changedFilesValidator";
import { GetPRDetails } from "./utils/gitWrapper";
import { ExitCode } from "./utils/exitCode";
import * as logger from "./utils/logger";
import gitP, { SimpleGit } from 'simple-git/promise';
import { readFileSync } from 'fs';

const workingDir: string = process.cwd();
const guidRegex: string = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}";
const templateIdRegex: string = `(id: ${guidRegex}(.|\n)*){2}`;
const git: SimpleGit = gitP(workingDir);

export async function IsIdHasChanged(filePath: string): Promise<ExitCode> {

    var skipValidationCheckFilePath = workingDir + "/.script/tests/idChangeValidatorTest/SkipIdValidationsTemplates.json";
    console.log("skipValidationCheckFilePath: " + skipValidationCheckFilePath);
    var skipIdsFile = JSON.parse(readFileSync(skipValidationCheckFilePath, 'utf8'));
    console.log(skipIdsFile + " " + typeof (skipIdsFile));

    if (filePath.includes("Detections") || filePath.includes("Analytic Rules")) {
        filePath = workingDir + '/' + filePath;
        const pr = await GetPRDetails();
        console.log(filePath);

        if (typeof pr === "undefined") {
            console.log("Azure DevOps CI for a Pull Request wasn't found. If issue persists - please open an issue");
            return ExitCode.ERROR;
        }

        let options = [pr.targetBranch, pr.sourceBranch, filePath];
        let diffSummary = await git.diff(options);
        let idPosition = diffSummary.search(templateIdRegex);
        let idHasChanged = idPosition > 0;

        if (idHasChanged) {

            //const regexp = new RegExp('[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', 'g');
            //console.log(typeof (regexp));

            const regex = RegExp('[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', 'g');
            let array1;
            var oldId: string = "";
            var newId: string = "";

            while ((array1 = regex.exec(diffSummary)) !== null) {
                if (oldId == "") {
                    oldId = array1[0];
                } else {
                    newId = array1[0];
                }
            }
            console.log(`Found ${oldId} and ${newId}.`);

            if (skipIdsFile.indexOf(newId) > -1) {
                console.log(filePath + " is skipped from this validation.");
                return ExitCode.SUCCESS;
            } else {
                throw new Error();
            }
        }
    }
    return ExitCode.SUCCESS;
}

let fileKinds = ["Modified"];
let fileTypeSuffixes = ["yaml", "yml", "json"];
let filePathFolderPrefixes = ["Detections", "Solutions"];
let CheckOptions = {
    onCheckFile: (filePath: string) => {
        return IsIdHasChanged(filePath);
    },
    onExecError: async (e: any, filePath: string) => {
        console.log(`${e}: Id of file - "${filePath}" has changed, please make sure you do not change any file id.`);
    },
    onFinalFailed: async () => {
        logger.logError("An error occurred, please open an issue");
    }
};

runCheckOverChangedFiles(CheckOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
