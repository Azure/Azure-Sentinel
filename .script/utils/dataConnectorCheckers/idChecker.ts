import { DataConnectorValidationError } from "../validationError";

export function isValidId(dataConnectorId: string, lineNumber: number) {
  
  if (/\s/.test(dataConnectorId)) {
    throw new DataConnectorValidationError(`Id should not have spaces. error at line number` +  lineNumber );
  }


}
