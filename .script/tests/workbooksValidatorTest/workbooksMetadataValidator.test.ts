import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { ExitCode } from "../../utils/exitCode";
import { IsValidWorkbookMetadata } from "../../workbooksMetadataValidator";

chai.use(chaiAsPromised);

describe("workbooksValidator", () => {
  it("should pass when WorkbooksMetadata.json is valid", async () => {
    await checkValid(".script/tests/workbooksValidatorTest/testFiles/validWorkbooksMetadata.json");
  });

  it("should throw an exception when WorkbooksMetadata contains an illegal property", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/testFiles/illegalPropertyWorkbooksMetadata.json", "SchemaError");
  });

  it("should throw an exception when WorkbooksMetadata is missing a required property", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/testFiles/missingRequiredPropertyWorkbooksMetadata.json", "SchemaError");
  });

  it("should throw an exception when WorkbooksMetadata has a duplicate Key", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/testFiles/duplicateKeyWorkbooksMetadata.json", "WorkbookValidationError");
  });

  it("should throw an exception when preview image file names are not png files", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/testFiles/nonPngPreviewImagesWorkbooksMetadata.json", "WorkbookValidationError");
  });

  it("should throw an exception when preview image file names do not include 'white' or 'black' keywords", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/testFiles/noColorPreviewImagesWorkbooksMetadata.json", "WorkbookValidationError");
  });

  it("should throw an exception when preview image file names are missing White images", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/testFiles/missingWhitePreviewImageWorkbooksMetadata.json", "WorkbookValidationError");
  });

  it("should throw an exception when preview image file names are missing Black images", async () => {
    await checkInvalid(".script/tests/workbooksValidatorTest/testFiles/missingBlackPreviewImageWorkbooksMetadata.json", "WorkbookValidationError");
  });

  async function checkInvalid(filePath: string, expectedError: string): Promise<Chai.PromisedAssertion> {
    expect(IsValidWorkbookMetadata(filePath)).eventually.rejectedWith(Error).and.have.property("name", expectedError);
  }

  async function checkValid(filePath: string): Promise<Chai.PromisedAssertion> {
    let result = await IsValidWorkbookMetadata(filePath);
    expect(result).to.equal(ExitCode.SUCCESS);
  }
});
