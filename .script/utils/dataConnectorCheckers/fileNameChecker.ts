import { DataConnectorValidationError } from "../validationError";

export function isValidFileName(filePath: string) {
  let fileName = filePath.replace(/^.*[\\\/]/,'');
  if (fileName.indexOf(' ') != -1 ) {
    throw new DataConnectorValidationError(`File name should not have spaces.`);
  }
}
