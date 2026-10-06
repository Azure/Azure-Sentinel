import { expect } from "chai";
import fs from "fs";
import { isValidSchema } from "../../utils/jsonSchemaChecker.js";
import { isValidPreviewImageFileNames } from "../../utils/workbookCheckers/previewImageChecker.js";
import { doDefinedLogoImageFilesExist, doDefinedPreviewImageFilesExist } from "../../utils/workbookCheckers/imageExistChecker.js";
import { doesNotContainResourceInfo } from "../../utils/workbookCheckers/workbookTemplateCheckers/containResourceInfoChecker.js";
import { isFromTemplateIdNotSentinelUserWorkbook } from "../../utils/workbookCheckers/workbookTemplateCheckers/fromTemplateIdChecker.js";

describe("RedRays workbook registration", () => {
  const read = (path: string) => JSON.parse(fs.readFileSync(path, "utf8"));
  const entry = read("Workbooks/WorkbooksMetadata.json").find((item: any) => item.workbookKey === "RedRaysSAPSecurityFindings");
  const workbook = read("Workbooks/RedRaysSAPSecurityFindings.json");

  it("matches the shared registry schema", () => {
    expect(entry).not.to.equal(undefined);
    expect(() => isValidSchema([entry], read(".script/utils/schemas/workbooksMetadataSchema.json"))).not.to.throw();
  });

  it("provides both real preview images and the workbook logo at registered paths", () => {
    expect(() => isValidPreviewImageFileNames([entry])).not.to.throw();
    expect(() => doDefinedLogoImageFilesExist([entry])).not.to.throw();
    expect(() => doDefinedPreviewImageFilesExist([entry])).not.to.throw();
    expect(entry.previewImagesFileNames.length).to.equal(2);
  });

  it("keeps the root workbook identical to the solution template", () => {
    expect(workbook).to.deep.equal(read("Solutions/RedRays SAP Security Findings/Workbooks/RedRaysSAPSecurityFindings.json"));
    expect(entry.templateRelativePath).to.equal("RedRaysSAPSecurityFindings.json");
  });

  it("has a portable template identity without deployment resource IDs", () => {
    expect(workbook.fromTemplateId).to.equal("sentinel-RedRaysSAPSecurityFindings");
    expect(workbook.$schema).to.equal("https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json");
    expect(() => isFromTemplateIdNotSentinelUserWorkbook(workbook)).not.to.throw();
    expect(() => doesNotContainResourceInfo(JSON.stringify(workbook))).not.to.throw();
    expect(workbook.fallbackResourceIds).to.deep.equal([]);
  });

  it("applies the required global time range to findings, heartbeat and scan panels", () => {
    const parameters = workbook.items.filter((item: any) => item.type === 9).flatMap((item: any) => item.content.parameters);
    const timeRange = parameters.find((parameter: any) => parameter.name === "TimeRange");
    expect(timeRange).to.include({ type: 4, isRequired: true, isGlobal: true });
    const panels = workbook.items.filter((item: any) => item.type === 3);
    expect(panels).to.have.length(3);
    for (const panel of panels) {
      expect(panel.content.timeContextFromParameter).to.equal(timeRange.name);
      expect(panel.content.query).not.to.include("ago(30d)");
    }
  });
});
