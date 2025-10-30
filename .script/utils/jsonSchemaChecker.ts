import { Schema, SchemaError, ValidationError, Validator } from "jsonschema";

export function isValidSchema(json: object, schema: object) {
  var validationResult = new Validator().validate(json, schema);
  if (!validationResult.valid) {
    let errorMessage = `Invalid Schema. Validation errors: ${validationResult.errors.map((err) => buildErrorMessage(err)).join(", ")}`;
    throw new SchemaError(errorMessage, schema);
  }
}

function buildErrorMessage(err: ValidationError){
  let errorMessage = err.stack;
  let description = (<Schema>err.schema).description;
  errorMessage += description ? `. Description: ${description}` : "";
  return errorMessage;
}