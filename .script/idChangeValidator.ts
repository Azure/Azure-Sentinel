import { runCheckOverChangedFiles } from "./utils/changedFilesValidator.js";
import { GetPRDetails } from "./utils/gitHubWrapper.js";
import { ExitCode } from "./utils/exitCode.js";
import * as logger from "./utils/logger.js";
import gitP, { SimpleGit } from 'simple-git';
import { readFileSync } from 'fs';

const workingDir: string = process.cwd();
const guidRegex: string = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}";
const templateIdRegex: string = `(id: ${guidRegex}(.|\n)*){2}`;
const git: SimpleGit = gitP(workingDir);

export async function IsIdHasChanged(filePath: string): Promise<ExitCode> {

    const skipValidationCheckFilePath = workingDir + "/.script/tests/idChangeValidatorTest/SkipIdValidationsTemplates.json";
    console.log("skipValidationCheckFilePath: " + skipValidationCheckFilePath);
    const skipIdsFile = JSON.parse(readFileSync(skipValidationCheckFilePath, 'utf8'));
    console.log(skipIdsFile + " " + typeof (skipIdsFile));

    if (filePath.includes("Detections") || filePath.includes("Analytic Rules")) {
        filePath = workingDir + '/' + filePath;
        const pr = await GetPRDetails();
        console.log(filePath);

        if (typeof pr === "undefined") {
            console.log("Pull Request couldn't be fetched. If issue persists - please open an issue");
            return ExitCode.ERROR;
        }

        // Fetch the base and head branches before running the diff
        const branches = await git.branch();
        if (!branches.all.includes(pr.base.ref)) {
            try {
                await git.fetch(['origin', pr.base.ref + ':' + pr.base.ref]);
            } catch (e) {
                console.error(`Error fetching branch ${pr.base.ref} from git:`, e);
                return ExitCode.ERROR;
            }
        }
        if (!branches.all.includes(pr.head.ref)) {
            try {
                    await git.fetch(['origin', pr.head.ref + ':' + pr.head.ref]);
            } catch (e) {
                console.error(`Error fetching branch ${pr.head.ref} from git:`, e);
                return ExitCode.ERROR;
            }
        }

        const options = [pr.base.ref, pr.head.ref, filePath];
        const diffSummary = await git.diff(options);
        const idPosition = diffSummary.search(templateIdRegex);
        const idHasChanged = idPosition > 0;

        if (idHasChanged) {

            //const regexp = new RegExp('[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', 'g');
            //console.log(typeof (regexp));

            const regex = RegExp('[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', 'g');
            let array1;
            let oldId: string = "";
            let newId: string = "";

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
                if (oldId !== newId) {
                    throw new Error();
                }
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
