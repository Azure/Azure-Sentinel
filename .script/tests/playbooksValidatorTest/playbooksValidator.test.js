import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { IsValidTemplate } from "../../playbooksValidator";
chai.use(chaiAsPromised);
describe("Playbooks validator", () => {
    it(`Should pass when playbook template is valid`, async () => {
        await checkValid(".script/tests/playbooksValidatorTest/testFiles/validPlaybookTemplate.json");
    });
    it(`Should pass when playbook template doesn't belong to the gallery`, async () => {
        await checkValid(".script/tests/playbooksValidatorTest/testFiles/validPlaybookTemplateNotForGallery.json");
    });
    it(`Should pass when playbook template is using using capitalized parameter types`, async () => {
        await checkValid(".script/tests/playbooksValidatorTest/testFiles/playbookTemplateWithCapitalizedParameterType.json");
    });
    it(`Should throw an exception when template is missing 'PlaybookName' parameter`, async () => {
        await checkInvalid(".script/tests/playbooksValidatorTest/testFiles/playbookTemplateWithNoPlaybookNameParameter.json");
    });
    it(`Should throw an exception when playbook resource location isn't taken from resource group location`, async () => {
        await checkInvalid(".script/tests/playbooksValidatorTest/testFiles/playbookTemplateWithHardcodedPlaybookLocation.json");
    });
    it(`Should throw an exception when playbook metadata has invalid entity types`, async () => {
        await checkInvalid(".script/tests/playbooksValidatorTest/testFiles/playbookTemplateWithInvalidEntityTypes.json");
    });
    async function checkInvalid(filePath) {
        await expect(IsValidTemplate(filePath)).eventually.rejectedWith(Error).and.have.property("name", "PlaybookValidationError");
    }
    async function checkValid(filePath) {
        let result = await IsValidTemplate(filePath);
        expect(result).to.equal(0 /* ExitCode.SUCCESS */);
    }
});
//# sourceMappingURL=playbooksValidator.test.js.map