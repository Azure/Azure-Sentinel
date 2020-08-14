import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { ExitCode } from "../../utils/exitCode";
import { IsValidWorkbook } from "../../workbooksValidator";

chai.use(chaiAsPromised);

describe("workbooksValidator", () => {
  it("should pass when WorkbooksMetadata.json is valid", async () => {
    await checkValid(".script/tests/workbooksValidatorTest/validWorkbooksMetadata.json");
  });

  it("should throw an exception when WorkbooksMetadata contains an illegal property", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/illegalPropertyWorkbooksMetadata.json", "SchemaError");
  });

  it("should throw an exception when WorkbooksMetadata is missing a required property", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/missingRequiredPropertyWorkbooksMetadata.json", "SchemaError");
  });

  it("should throw an exception when WorkbooksMetadata has a duplicate Key", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/duplicateKeyWorkbooksMetadata.json", "WorkbookValidationError");
  });

  it("should throw an exception when previewImagesFileNames are inconsistent with naming convention ", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/badPreviewImagesFileNamesWorkbooksMetadata.json", "WorkbookValidationError");
  });

  it("should throw an exception when previewImagesFileNames is missing White filenames ", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/missingWhitePreviewImageWorkbooksMetadata.json", "WorkbookValidationError");
  });

  it("should throw an exception when previewImagesFileNames is missing Black filenames ", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/missingBlackPreviewImageWorkbooksMetadata.json", "WorkbookValidationError");
  });

  async function checkInvalid(filePath: string, expectedError: string): Promise<Chai.PromisedAssertion> {
    expect(IsValidWorkbook(filePath)).eventually.rejectedWith(Error).and.have.property("name", expectedError);
  }

  async function checkValid(filePath: string): Promise<Chai.PromisedAssertion> {
    let result = await IsValidWorkbook(filePath);
    expect(result).to.equal(ExitCode.SUCCESS);
  }
});
