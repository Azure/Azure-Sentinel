import { DataType } from "../dataConnector";
import { DataConnectorValidationError } from "../validationError";

export function isValidDataType(dataTypes: Array<DataType>,  lineNumber: number): boolean {   
    dataTypes.forEach((dataType) => {
        let name = dataType.name;
        if(name.indexOf(' ') >= 0)
        {
            if ((name.includes("CommonSecurityLog") || name.includes("Syslog")))
            {
                return true;
            }

            throw new DataConnectorValidationError(`Data Type should not have spaces. Error at line number `+ lineNumber)
        }
        return true;
    });

    return true;
}