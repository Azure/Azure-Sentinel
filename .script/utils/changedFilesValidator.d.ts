import { ExitCode } from "./exitCode.js";
export type CheckOptions = {
    onExecError(result: any, filePath: string): Promise<unknown>;
    onCheckFile(filePath: string): Promise<ExitCode>;
    onFinalFailed(): Promise<unknown>;
};
export declare function runCheckOverChangedFiles(options: CheckOptions, fileKinds: string[], fileTypeSuffixes?: string[], filePathFolderPrefixes?: string[]): void;
//# sourceMappingURL=changedFilesValidator.d.ts.map