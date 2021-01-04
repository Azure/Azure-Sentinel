import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { ExitCode } from "../../utils/exitCode";
import { IsValidDataConnectorSchema } from "../../dataConnectorValidator";

chai.use(chaiAsPromised);

describe("dataConnectorValidator", () => {
  it("should pass when dataConnectorSchema.json is valid", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/validDataConnectorSchema.json");
  });

  it("should throw an exception when dataConnectorSchema.json is missing a required property", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/missingRequiredPropertyDataConnectorSchema.json", "SchemaError");
  });

  it("should throw an exception when dataConnectorSchema.json is having space in ID property", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/spaceInDataConnectorId.json", "DataConnectorValidationError");
  });

  it("should throw an exception when dataConnectorSchema.json is having space in Data Type property", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/spaceInDataConnectorDataType.json","DataConnectorValidationError");
  });

  async function checkValid(filePath: string): Promise<Chai.PromisedAssertion> {
    let result = await IsValidDataConnectorSchema(filePath);
    expect(result).to.equal(ExitCode.SUCCESS);
  }

  async function checkInvalid(filePath: string, expectedError: string): Promise<Chai.PromisedAssertion> {
    expect(IsValidDataConnectorSchema(filePath)).eventually.rejectedWith(Error).and.have.property("name", expectedError);
  }
});
