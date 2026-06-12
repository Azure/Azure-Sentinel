import { SchemaError, Validator } from "jsonschema";
export function isValidSchema(json, schema) {
    var validationResult = new Validator().validate(json, schema);
    if (!validationResult.valid) {
        let errorMessage = `Invalid Schema. Validation errors: ${validationResult.errors.map((err) => buildErrorMessage(err)).join(", ")}`;
        throw new SchemaError(errorMessage, schema);
    }
}
function buildErrorMessage(err) {
    let errorMessage = err.stack;
    let description = err.schema.description;
    errorMessage += description ? `. Description: ${description}` : "";
    return errorMessage;
}
//# sourceMappingURL=jsonSchemaChecker.js.map