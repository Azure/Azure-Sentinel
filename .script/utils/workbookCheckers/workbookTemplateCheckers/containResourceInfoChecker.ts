import { WorkbookTemplatesValidationError } from "../../validationError";

const guidRegex: string = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}";
const resourceRegex: string = `subscriptions\/${guidRegex}`;

// This function checks if the template json file contains any information of a resource (for example: /subscriptions/{GUID}}/resourcegroups/my_resource_group/.....).
export function doesContainResourceInfo(workbookTemplate: string) {
  const resourceInfoIndex: number = workbookTemplate.search(resourceRegex);
  if(resourceInfoIndex > 0){
    throw new WorkbookTemplatesValidationError(`Contains info of a resource at offset ${resourceInfoIndex}. A workbook template must not contain any references to resources.`);
  }
}
