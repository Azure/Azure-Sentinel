interface ValidationError {
  name: string;
}

export class WorkbookValidationError extends Error implements ValidationError {
  public name = "WorkbookValidationError";
  constructor(message?: string) {
    super(message);
  }
}

export class DataConnectorValidationError extends Error implements ValidationError {
  public name = "DataConnectorValidationError";
  constructor(message?: string) {
    super(message);
  }
}
