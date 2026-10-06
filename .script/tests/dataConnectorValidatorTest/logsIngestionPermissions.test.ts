import { expect } from "chai";
import fs from "fs";
import { ConnectorCategory, RequiredConnectorPermissions } from "../../utils/dataConnector.js";
import { isValidPermissions } from "../../utils/dataConnectorCheckers/permissionsChecker.js";
import { isValidSchema } from "../../utils/jsonSchemaChecker.js";

describe("Logs Ingestion API permissions", () => {
  function connector() {
    return JSON.parse(fs.readFileSync("Solutions/RedRays SAP Security Findings/Data Connectors/RedRaysSAPSecurityFindings.json", "utf8"));
  }

  function permissions(): RequiredConnectorPermissions {
    return connector().permissions;
  }

  it("validates the complete DCR connector against the REST API schema", () => {
    const schema = JSON.parse(fs.readFileSync(".script/utils/schemas/REST_API_ConnectorSchema.json", "utf8"));
    expect(() => isValidSchema(connector(), schema)).not.to.throw();
    expect(isValidPermissions(permissions(), ConnectorCategory.RestAPI)).to.equal(true);
  });

  it("does not apply the DCR profile to CEF, Event or Azure Functions", () => {
    for (const category of [ConnectorCategory.CEF, ConnectorCategory.Event, ConnectorCategory.AzureFunction]) {
      expect(() => isValidPermissions(permissions(), category)).to.throw();
    }
  });

  it("requires the DCR role prerequisite", () => {
    const p = permissions();
    p.customs = p.customs?.filter(c => c.name !== "Azure Monitor Logs Ingestion API");
    expect(() => isValidPermissions(p, ConnectorCategory.RestAPI)).to.throw();
  });

  it("rejects incomplete or altered DCR role guidance", () => {
    const p = permissions();
    p.customs![0].description = "Any workspace reader can send data.";
    expect(() => isValidPermissions(p, ConnectorCategory.RestAPI)).to.throw();
  });

  it("rejects missing workspace write permission and unexpected resource access", () => {
    const p = permissions();
    delete p.resourceProvider![0].requiredPermissions.write;
    expect(() => isValidPermissions(p, ConnectorCategory.RestAPI)).to.throw();
    const extra = permissions();
    extra.resourceProvider!.push({ ...extra.resourceProvider![0], provider: "Microsoft.Authorization/roleAssignments" });
    expect(() => isValidPermissions(extra, ConnectorCategory.RestAPI)).to.throw();
  });

  it("continues to accept the legacy REST API shared-key template", () => {
    const legacy = JSON.parse(fs.readFileSync(".script/tests/dataConnectorValidatorTest/testFiles/validRestApiDataConnector.json", "utf8"));
    expect(isValidPermissions(legacy.permissions, ConnectorCategory.RestAPI)).to.equal(true);
    legacy.permissions.resourceProvider.pop();
    expect(() => isValidPermissions(legacy.permissions, ConnectorCategory.RestAPI)).to.throw();
  });
});
