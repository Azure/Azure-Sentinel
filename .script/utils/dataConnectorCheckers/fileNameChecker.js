import { DataConnectorValidationError } from "../validationError.js";
export function isValidFileName(filePath) {
    let fileName = filePath.replace(/^.*[\\\/]/, '');
    if (fileName.indexOf(' ') != -1) {
        throw new DataConnectorValidationError(`File name should not have spaces.`);
    }
}
//# sourceMappingURL=fileNameChecker.js.map