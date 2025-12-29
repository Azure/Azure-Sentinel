import { WorkbookValidationError } from "../validationError.js";
export function isUniqueKeys(items) {
    if (items.length > new Set(items.map((metadata) => metadata.workbookKey)).size) {
        throw new WorkbookValidationError(`WorkbooksMetadata keys must be unique. Remove any duplicate keys.`);
    }
}
//# sourceMappingURL=uniqueWorkbookKeyChecker.js.map