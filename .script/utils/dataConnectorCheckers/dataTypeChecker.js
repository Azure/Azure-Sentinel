import { DataConnectorValidationError } from "../validationError.js";
export function isValidDataType(dataTypes) {
    dataTypes.forEach((dataType) => {
        let name = dataType.name;
        if (name.indexOf(' ') >= 0) {
            if ((name.includes("CommonSecurityLog") || name.includes("Syslog") || name.includes("Event") || name.includes("AzureDiagnostics") || name.includes("AzureDevOpsAuditing"))) {
                return true;
            }
            throw new DataConnectorValidationError(`Data Type should not have spaces.`);
        }
        return true;
    });
    return true;
}
//# sourceMappingURL=dataTypeChecker.js.map