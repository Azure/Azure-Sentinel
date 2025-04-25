import { WorkbookTemplatesValidationError } from "../../validationError.js";
import { WorkbookTemplate } from "../../workbookTemplate.js";

// This function checks if the value of the "fromTemplateId" key is not "sentinel-UserWorkbook" (which is the default given value).
export function isFromTemplateIdNotSentinelUserWorkbook(workbookTemplate: WorkbookTemplate) {
  if(workbookTemplate.fromTemplateId === "sentinel-UserWorkbook"){
    throw new WorkbookTemplatesValidationError(`Value for "fromTemplateId" must be other than "sentinel-UserWorkbook".`);
  }
}
