import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { IsValidLogo } from "../../logoValidator";
import { ExitCode } from "../../utils/exitCode";

chai.use(chaiAsPromised);

describe("logoValidator", () => {
  it("Should pass when logo file is in svg format", async () => {
    await checkValid(".script/tests/logoValidatorTest/testFiles/Morphisec_Logo.svg");
  });

  it("Should throw an exception as logo file should be in svg format", async () => {
    await checkInvalid(".script/tests/logoValidatorTest/testFiles/ForgeRock_Logo_Vert_75x75.png","logoValidationError");
  });

  it("Should throw an exception as logo file should not have style tag", async () => {
    await checkInvalid(".script/tests/logoValidatorTest/testFiles/Filewithstyletag.svg","logoValidationError");
  });

  it("Should throw an exception as logo file should not have embed png", async () => {
    await checkInvalid(".script/tests/logoValidatorTest/testFiles/FileWithPNGEmbed.svg","logoValidationError");
  });

  it("Should throw an exception as logo file should not have xmlns:xlink tag", async () => {
    await checkInvalid(".script/tests/logoValidatorTest/testFiles/filewithxmlnsxlink.svg","logoValidationError");
  });

  it("Should throw an exception as logo file should not have xmlns:herf tag", async () => {
    await checkInvalid(".script/tests/logoValidatorTest/testFiles/fileWithxmlnsHERF.svg","logoValidationError");
  });
  
  it("Should throw an exception as logo file should have id as guid", async () => {
    await checkInvalid(".script/tests/logoValidatorTest/testFiles/FileWithInvalidGuidId.svg","logoValidationError");
  });

  it("Should pass when there is same id for two tag ", async () => {
    await checkInvalid(".script/tests/logoValidatorTest/testFiles/FileWithSameGuidID.svg","logoValidationError");
  });

  it("Should pass when logo file has embed png", async () => {
    await checkValid(".script/tests/logoValidatorTest/testFiles/filewithoutpngembed.svg");
  });
  it("Should throw an exception as logo file should be of less then or equal to 5 kb", async () => {
    await checkInvalid(".script/tests/logoValidatorTest/testFiles/MoreThen5KB.svg","logoValidationError");
  });
  
  async function checkValid(filePath: string): Promise<Chai.PromisedAssertion> {
    let result = await IsValidLogo(filePath);
    expect(result).to.equal(ExitCode.SUCCESS);
  }

  async function checkInvalid(filePath: string, expectedError: string): Promise<Chai.PromisedAssertion> {
    expect(IsValidLogo(filePath)).eventually.rejectedWith(Error).and.have.property("name", expectedError);
  }
});
