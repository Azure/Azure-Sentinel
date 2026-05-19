import { DataConnectorValidationError } from "../validationError.js";
export function isValidId(dataConnectorId) {
    if (/\s/.test(dataConnectorId)) {
        throw new DataConnectorValidationError(`Id should not have spaces.`);
    }
}
//# sourceMappingURL=idChecker.js.map