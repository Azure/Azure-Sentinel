import { IsFileContainsLinkWithLocale } from "../../documentsLinkValidator";
import { ExitCode } from "../../utils/exitCode";
import chai from "chai";
import { expect } from "chai";
import chaiAsPromised from "chai-as-promised";

chai.use(chaiAsPromised);

describe("documentsLinkValidator", () => {
  it("should pass when no links", async () => {
    let result = await IsFileContainsLinkWithLocale(".script/tests/documentsLinkValidatorTest/nodoclinks.md");
    expect(result).to.equal(ExitCode.SUCCESS);
  });

  it("should pass when link is valid", async () => {
    let result = await IsFileContainsLinkWithLocale(".script/tests/documentsLinkValidatorTest/validlink.md");
    expect(result).to.equal(ExitCode.SUCCESS);
  });

  it("should fail when link contains locale", async () => {
    let result = await IsFileContainsLinkWithLocale(".script/tests/documentsLinkValidatorTest/badlink.md");
    expect(result).eventually.rejectedWith(Error)
  });
});
