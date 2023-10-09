import { SampleDataValidationError } from "../validationError";
const regEmail = 'sanitized@sanitized.com';
export function isValidSampleData(sampleDataContent: string) {
   console.log(sampleDataContent.length);

    if(sampleDataContent.length<0 || sampleDataContent.length==undefined)
    {
        throw new SampleDataValidationError(`Sample data file data must be in the form of array.`);
    }
    let email  = extractEmails(JSON.stringify(sampleDataContent) );
    let varEmail = email?.filter(e=>e!=regEmail)
    if(varEmail !== undefined && varEmail.length >0)
    {
     throw new SampleDataValidationError(`Email must be sanitized@sanitized.com`);
    }
   return true;
  }
  function extractEmails (sampleDataContent: string)

 {
     return sampleDataContent.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/gi);
 };