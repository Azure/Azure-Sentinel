import { WorkbookValidationError } from "../validationError";
import { WorkbookMetadata } from "../workbookMetadata";

export function isUniqueKeys(items: Array<WorkbookMetadata>) {
  if (items.length > new Set(items.map((metadata) => metadata.workbookKey)).size) {
    throw new WorkbookValidationError(`WorkbooksMetadata keys must be unique. Remove any duplicate keys.`);
  }
}
