import { WorkbookValidationError } from "../validationError";
import { WorkbookMetadata } from "../workbookMetadata";

const invalidDependencyArrayJson: string = JSON.stringify([""]);

// This function checks if the value of the "dataConnectorsDependencies" key is empty, and if so, to be in the correct format ([] and not [""]).
export function isEmptyDataConnectorsDependencyInCorrectFormat(items: Array<WorkbookMetadata>) {
  items.forEach((workbookMetadata: WorkbookMetadata) => {
    let uniqueConnectorsDependencies: string[] = [...new Set(workbookMetadata.dataConnectorsDependencies)]; // Remove duplicates in case of array in the form of: ["", ""]
    if(JSON.stringify(uniqueConnectorsDependencies) === invalidDependencyArrayJson){
      throw new WorkbookValidationError(`Empty connectors dependency array must be defined as [] and not [""]`);
    }
  });
}

// This function checks if the value of the "dataTypesDependencies" key is empty, and if so, to be in the correct format ([] and not [""]).
export function isEmptyDataTypesDependencyInCorrectFormat(items: Array<WorkbookMetadata>) {
  items.forEach((workbookMetadata: WorkbookMetadata) => {
    let uniqueTypesDependencies: string[] = [...new Set(workbookMetadata.dataTypesDependencies)]; // Remove duplicates in case of array in the form of: ["", ""]
    if(JSON.stringify(uniqueTypesDependencies) === invalidDependencyArrayJson){
      throw new WorkbookValidationError(`Empty connectors dependency array must be defined as [] and not [""]`);
    }
  });
}
