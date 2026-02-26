import { GetDiffFiles } from "./gitHubWrapper.js";
import * as logger from "./logger.js";
async function changedFilesValidator(checkOptions, fileKinds, fileTypeSuffixes, filePathFolderPrefixes) {
    const changedFiles = await GetDiffFiles(fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
    if (changedFiles === undefined) {
        return;
    }
    let retCode = 0 /* ExitCode.SUCCESS */;
    for (const filePath of changedFiles) {
        try {
            const validationResultCode = await checkOptions.onCheckFile(filePath);
            if (validationResultCode !== 0 /* ExitCode.SUCCESS */) {
                retCode = -1 /* ExitCode.ERROR */;
            }
        }
        catch (e) {
            await checkOptions.onExecError(e, filePath);
            retCode = -1 /* ExitCode.ERROR */;
        }
    }
    if (retCode !== 0 /* ExitCode.SUCCESS */) {
        await checkOptions.onFinalFailed();
    }
    process.exit(retCode);
}
export function runCheckOverChangedFiles(options, fileKinds, fileTypeSuffixes, filePathFolderPrefixes) {
    changedFilesValidator(options, fileKinds, fileTypeSuffixes, filePathFolderPrefixes).catch(e => {
        console.error(e);
        logger.logError(`Error. If issue persists - please open an issue`);
        process.exit(-1 /* ExitCode.ERROR */);
    });
}
//# sourceMappingURL=changedFilesValidator.js.map