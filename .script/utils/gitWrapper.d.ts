import { devOps } from "@azure/avocado";
import "./stringExtenssions";
export declare function GetPRDetails(): Promise<devOps.PullRequestProperties | undefined>;
export declare function GetDiffFiles(fileKinds: string[], fileTypeSuffixes?: string[], filePathFolderPreffixes?: string[]): Promise<string[] | undefined>;
//# sourceMappingURL=gitWrapper.d.ts.map