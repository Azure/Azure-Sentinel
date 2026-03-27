import { IsValidYamlFile } from "../../yamlFileValidator";
import chai from "chai";
import { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
chai.use(chaiAsPromised);
describe("yamlFileValidator", () => {
    it("should pass when yaml file is valid", async () => {
        let result = await IsValidYamlFile(".script/tests/yamlFileValidatorTest/validFile.yaml");
        expect(result).to.equal(0 /* ExitCode.SUCCESS */);
    });
    it("should throw exception when yaml file is invalid", async () => {
        let filePath = ".script/tests/yamlFileValidatorTest/invalidFile.yaml";
        await expect(IsValidYamlFile(filePath))
            .eventually.rejectedWith(Error)
            .and.have.property("name", "YAMLException");
    });
});
//# sourceMappingURL=yamlFileValidator.test.js.map