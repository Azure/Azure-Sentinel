import { ExitCode } from "./exitCode";
import { GetDiffFiles } from "./gitWrapper";
import * as logger from "./logger";

export type CheckOptions = {
  onExecError(result: any, filePath: string): Promise<unknown>;
  onCheckFile(filePath: string): Promise<ExitCode>;
  onFinalFailed(): Promise<unknown>;
};

async function changedFilesValidator(checkOptions: CheckOptions, fileKinds: string[], fileTypeSuffixes?: string[], filePathFolderPrefixes?: string[]) {
  const changedFiles = await GetDiffFiles(fileKinds, fileTypeSuffixes, filePathFolderPrefixes);
  if (changedFiles === undefined) {
    return;
  }

  let retCode = ExitCode.SUCCESS;

  for (const filePath of changedFiles) {
    try {
      const validationResultCode = await checkOptions.onCheckFile(filePath);
      if (validationResultCode !== ExitCode.SUCCESS) {
        retCode = ExitCode.ERROR;
      }
    } catch (e) {
      await checkOptions.onExecError(e, filePath);
      retCode = ExitCode.ERROR;
    }
  }

  if (retCode !== ExitCode.SUCCESS) {
    await checkOptions.onFinalFailed();
  }

  process.exit(retCode);
}

export function runCheckOverChangedFiles(options: CheckOptions, fileKinds: string[], fileTypeSuffixes?: string[], filePathFolderPrefixes?: string[]) {
  changedFilesValidator(options, fileKinds, fileTypeSuffixes, filePathFolderPrefixes).catch(e => {
    console.error(e);
    logger.logError(`Error. If issue persists - please open an issue`);
    process.exit(ExitCode.ERROR);
  });
}
