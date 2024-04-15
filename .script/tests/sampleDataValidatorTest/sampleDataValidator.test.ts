import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { IsValidSampleDataSchema } from "../../sampleDataValidator";
import { ExitCode } from "../../utils/exitCode";

chai.use(chaiAsPromised);

describe("dataConnectorValidator", () => {
    it("should pass when sampleDataWithArray.json is valid", async () => {
        await checkValid(".script/tests/sampleDataValidatorTest/testFiles/sampleDataWithArray.json");
      });
    it("should throw an exception when sampleDataStartWithBracket.json is missing a required property", async () => {
        await checkInvalid(".script/tests/sampleDataValidatorTest/testFiles/sampleDataStartWithBracket.json", "SampleDataValidationError");
      }); 
      it("should pass when sampleDataWithValidEmail.json contains valid email.", async () => {
        await checkValid(".script/tests/sampleDataValidatorTest/testFiles/sampleDataWithValidEmail.json");
    });
   it("should throw an exception when sampleDataWithInvalidEmail.json contains invalid email.  ", async () => {
       await checkInvalid(".script/tests/sampleDataValidatorTest/testFiles/sampleDataWithInvalidEmail.json", "SampleDataValidationError");
     }); 

  async function checkValid(filePath: string): Promise<Chai.PromisedAssertion> {
    let result = await IsValidSampleDataSchema(filePath);
    expect(result).to.equal(ExitCode.SUCCESS);
  }

  async function checkInvalid(filePath: string, expectedError: string): Promise<Chai.PromisedAssertion> {
    expect(IsValidSampleDataSchema(filePath)).eventually.rejectedWith(Error).and.have.property("name", expectedError);
  }
});