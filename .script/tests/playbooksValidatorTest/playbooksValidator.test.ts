import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { ExitCode } from "../../utils/exitCode";
import { IsValidTemplate } from "../../playbooksValidator";

chai.use(chaiAsPromised);

describe("Playbooks validator", () => {
  it(`Should pass when playbook template is valid`, async () => {
    await checkValid(".script/tests/playbooksValidatorTest/testFiles/validPlaybookTemplate.json");
  });

  it(`Should throw an exception when template is missing 'PlaybookName' parameter`, async () => {
    await checkInvalid(".script/tests/playbooksValidatorTest/testFiles/playbookTemplateWithNoPlaybookNameParameter.json");
  });

  async function checkInvalid(filePath: string): Promise<Chai.PromisedAssertion> {
    await expect(IsValidTemplate(filePath)).eventually.rejectedWith(Error).and.have.property("name", "PlaybookValidationError");
  }

  async function checkValid(filePath: string): Promise<Chai.PromisedAssertion> {
    let result = await IsValidTemplate(filePath);
    expect(result).to.equal(ExitCode.SUCCESS);
  }
});
