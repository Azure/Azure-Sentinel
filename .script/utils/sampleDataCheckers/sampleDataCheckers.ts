import { SampleDataValidationError } from "../validationError";

export function isValidSampleData(sampleDataContent: string) {
   console.log(sampleDataContent.length);

    if(sampleDataContent.length<0 || sampleDataContent.length==undefined)
    {
        throw new SampleDataValidationError(`Sample data file data must be in the form of array.`);
    }
   return true;
  };