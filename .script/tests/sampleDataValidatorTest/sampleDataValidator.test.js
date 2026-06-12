import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { IsValidSampleDataSchema } from "../../sampleDataValidator";
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
    async function checkValid(filePath) {
        let result = await IsValidSampleDataSchema(filePath);
        expect(result).to.equal(0 /* ExitCode.SUCCESS */);
    }
    async function checkInvalid(filePath, expectedError) {
        expect(IsValidSampleDataSchema(filePath)).eventually.rejectedWith(Error).and.have.property("name", expectedError);
    }
});
//# sourceMappingURL=sampleDataValidator.test.js.map