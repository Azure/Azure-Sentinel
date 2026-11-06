import { WorkbookMetadata } from "../workbookMetadata.js";
import { ExitCode } from "../exitCode.js";
export declare function isVersionIncrementedOnModification(items: Array<WorkbookMetadata>): Promise<ExitCode>;
export declare function getVersionChangesByWorkbook(baseItems: Array<Pick<WorkbookMetadata, "templateRelativePath" | "version">>, headItems: Array<Pick<WorkbookMetadata, "templateRelativePath" | "version">>): Record<string, {
    newVersion: string;
    oldVersion: string;
}>;
//# sourceMappingURL=isVersionIncrementedOnModification.d.ts.map