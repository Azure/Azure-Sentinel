import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { IsValidWorkbookTemplate } from "../../workbooksTemplateValidator";
chai.use(chaiAsPromised);
describe("Workbooks template validator", () => {
    it(`Should pass when workbook template is valid`, async () => {
        await checkValid(".script/tests/workbooksValidatorTest/testFiles/workbooksTemplateFiles/validWorkbooksTemplate.json");
    });
    it(`Should throw an exception when workbook template "fromTemplateId" value is "sentinel-UserWorkbook"`, async () => {
        await checkInvalid(".script/tests/workbooksValidatorTest/testFiles/workbooksTemplateFiles/invalidValueForFromTemplateId.json", "WorkbookTemplatesValidationError");
    });
    it(`Should throw an exception when workbook template contains info of a resource"`, async () => {
        await checkInvalid(".script/tests/workbooksValidatorTest/testFiles/workbooksTemplateFiles/containsResourceInfoTemplate.json", "WorkbookTemplatesValidationError");
    });
    async function checkInvalid(filePath, expectedError) {
        await expect(IsValidWorkbookTemplate(filePath)).eventually.rejectedWith(Error).and.have.property("name", expectedError);
    }
    async function checkValid(filePath) {
        let result = await IsValidWorkbookTemplate(filePath);
        expect(result).to.equal(0 /* ExitCode.SUCCESS */);
    }
});
//# sourceMappingURL=workbooksTemplateValidator.test.js.map