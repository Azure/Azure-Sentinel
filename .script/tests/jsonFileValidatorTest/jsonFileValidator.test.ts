import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { IsValidJsonFile } from "../../jsonFileValidator";
import { ExitCode } from "../../utils/exitCode";

chai.use(chaiAsPromised);

describe("jsonFileValidator", () => {
  it("should pass when json file is valid", async () => {
    let result = await IsValidJsonFile(".script/tests/jsonFileValidatorTest/validFile.json");

    expect(result).to.equal(ExitCode.SUCCESS);
  });

  it("should throw exception when json file is invalid", async () => {
    let filePath = ".script/tests/jsonFileValidatorTest/invalidFile.json";

    await expect(IsValidJsonFile(filePath)).eventually.rejectedWith(Error).and.have.property("name", "SyntaxError");
  });
});
