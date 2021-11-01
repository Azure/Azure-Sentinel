import { DataConnectorValidationError } from "../validationError";

export function isValidId(dataConnectorId: string) {
  if (/\s/.test(dataConnectorId)) {
    throw new DataConnectorValidationError(`Id should not have spaces.`);
  }
}
