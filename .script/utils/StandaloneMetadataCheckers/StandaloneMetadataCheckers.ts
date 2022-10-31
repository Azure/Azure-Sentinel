import { MetadataValidationError } from "../../validationError";
import { StandaloneMetadata } from "../standaloneMetadata";

// This function checks if the value of the "kind" key has the value "Community".
export function isValidMetadata(kind: string) {
  if(StandaloneMetadata.kind !== "Community"){
    throw new MetadataValidationError(`Value for "source.kind" must be "Community".`);
  }
}
