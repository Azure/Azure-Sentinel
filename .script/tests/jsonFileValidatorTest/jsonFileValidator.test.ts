import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { IsValidJsonFile } from "../../jsonFileValidator";
import { ExitCode } from "../../utils/exitCode";

chai.use(chaiAsPromised);

describe("jsonFileValidator", () => {
  it("should pass when json file is valid", async () => {
    checkValid(".script/tests/jsonFileValidatorTest/validFile.json");
  });

  it("should throw exception when json file is invalid", async () => {
    await checkInvalid(".script/tests/jsonFileValidatorTest/invalidFile.json", "SyntaxError");
  });

  it("should pass when workbooks metadata is valid", async () => {
    checkValid(".script/tests/jsonFileValidatorTest/validWorkbooksMetadata.json");
  });

  it("should throw an exception when WorkbooksMetadata contains an illegal property", async () => {
    await checkInvalid(".script/tests/jsonFileValidatorTest/illegalPropertyWorkbooksMetadata.json", "SchemaError")
  });

  it("should throw an exception when WorkbooksMetadata is missing a required property", async () => {
    await checkInvalid(".script/tests/jsonFileValidatorTest/missingRequiredPropertyWorkbooksMetadata.json", "SchemaError")
  });

  async function checkInvalid(filePath: string, expectedError: string): Promise<Chai.PromisedAssertion> {
    expect(IsValidJsonFile(filePath))
    .eventually.rejectedWith(Error)
    .and.have.property("name", expectedError);
  }

  async function checkValid(filePath: string): Promise<Chai.PromisedAssertion> {
    let result = await IsValidJsonFile(filePath);
    expect(result).to.equal(ExitCode.SUCCESS);
  }
});
