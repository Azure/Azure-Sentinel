import { SchemaError, Validator } from "jsonschema";

export function isValidSchema(json: object, schema: object) {
  var validationResult = new Validator().validate(json, schema);
  if (!validationResult.valid) {
    let errorMsg = `Invalid Schema. Validation errors: ${validationResult.errors.map((err) => err.message).join(", ")}`;
    throw new SchemaError(errorMsg, schema);
  }
}
