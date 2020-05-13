import { IsValidJsonFile } from "../../jsonFileValidator";
import { ExitCode } from "../../utils/exitCode";
import chai from "chai";
import { expect } from "chai";
import chaiAsPromised from "chai-as-promised";

chai.use(chaiAsPromised);

describe("documentsLinkValidator", () => {
  it("should pass when no links", async () => {
    let result = await IsValidJsonFile(".script/tests/documentsLinkValidatorTest/nodoclinks.md");
    expect(result).to.equal(ExitCode.SUCCESS);
  });

  it("should pass when link is valid", async () => {
    let result = await IsValidJsonFile(".script/tests/documentsLinkValidatorTest/validlink.md");
    expect(result).to.equal(ExitCode.ERROR);
  });

  it("should fail when link conains locale", async () => {
    let result = await IsValidJsonFile(".script/tests/documentsLinkValidatorTest/badlink.md");
    expect(result).to.equal(ExitCode.ERROR);
  });
});
