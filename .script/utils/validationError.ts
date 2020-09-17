interface ValidationError {
  name: string;
}

export class WorkbookValidationError extends Error implements ValidationError {
  public name = "WorkbookValidationError";
  constructor(message?: string) {
    super(message);
  }
}
