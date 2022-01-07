interface ValidationError {
  name: string;
}

export class WorkbookValidationError extends Error implements ValidationError {
  public name = "WorkbookValidationError";
  constructor(message?: string) {
    super(message);
  }
}

export class LogoValidationError extends Error implements ValidationError {
  public name = "LogoValidationError";
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

export class WorkbookTemplatesValidationError extends Error implements ValidationError {
  public name = "WorkbookTemplatesValidationError";

  constructor(message?: string) {
    super(message);
  }
}

export class PlaybookValidationError extends Error implements ValidationError {
  public name = "PlaybookValidationError";

  constructor(message?: string) {
    super(message);
  }
}
export class SampleDataValidationError extends Error implements ValidationError {
  public name = "SampleDataValidationError";
  constructor(message?: string) {
    super(message);
  }
}