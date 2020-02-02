import { GetDiffFiles } from "./gitWrapper";
import { ExitCode } from "./exitCode";
import * as logger from "./logger";

export type CheckOptions = {
  onExecError(result: any, filePath: string): Promise<unknown>;
  onCheckFile(filePath: string): Promise<ExitCode>;
  onFinalFailed(): Promise<unknown>;
};

async function changedFilesValidator(checkOptions: CheckOptions, fileTypeSuffixes?: string[], filePathFolderPreffixes?: string[]) {
  const changedFiles = await GetDiffFiles(fileTypeSuffixes, filePathFolderPreffixes);
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

export function runCheckOverChangedFiles(options: CheckOptions, fileTypeSuffixes?: string[], filePathFolderPreffixes?: string[]) {
  changedFilesValidator(options, fileTypeSuffixes, filePathFolderPreffixes).catch(e => {
    console.error(e);
    logger.logError(`Error. If issue persists - please open an issue`);
    process.exit(ExitCode.ERROR);
  });
}
