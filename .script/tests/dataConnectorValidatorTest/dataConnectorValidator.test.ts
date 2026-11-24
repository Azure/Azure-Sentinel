import chai, { expect } from "chai";
import chaiAsPromised from "chai-as-promised";
import { ExitCode } from "../../utils/exitCode";
import { IsValidDataConnectorSchema } from "../../dataConnectorValidator";
import {
  discoverTablesInJsonObject,
  isValidCustomTableSchemas,
} from "../../utils/dataConnectorCheckers/customTableSchemaChecker";

chai.use(chaiAsPromised);

describe("dataConnectorValidator", () => {
  it("should pass when validSyslogDataConnector.json is valid", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/validSyslogDataConnector.json");
  });

  it("should pass when validCEFDataConnector.json is valid", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/validCEFDataConnector.json");
  });

  it("should pass when validRestApiDataConnector.json is valid", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/validRestApiDataConnector.json");
  });

  it("should pass when validAzureFunctionDataConnector.json is valid", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/Agari/validAzureFunctionDataConnector.json");
  });

  // To identify data connector json file with ID and connectivityCriterias,skipping other json files.
  it("should skip .json file when missing ID or connectivityCriterias attributes", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/missingIdAndConnectivityCriteria.json");
  });

    // Skipping json files if exists in Template folder.
    it("should skip .json file if exist under Templates folder", async () => {
      await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/Templates/Connector_REST_API_template.json");
    });

  it("should throw an exception when dataConnectorSchema.json is missing a required property", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/missingPublisherProperty.json", "SchemaError");
  });

  // Skipping as additional banner is no more mandatory.
  // it("should throw an exception when Syslog Data connector is missing a additional requirement banner property", async () => {
  //   await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/missingAdditionalRequirementBanner.json", "SchemaError");
  // });

  it("should throw an exception when DataConnector FileName is having space in file name", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/spaceIn DataConnector FileName.json", "DataConnectorValidationError");
  });

  it("should throw an exception when dataConnectorSchema.json is having space in ID property", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/spaceInDataConnectorId.json", "DataConnectorValidationError");
  });

  it("should throw an exception when dataConnectorSchema.json is having space in Data Type property", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/spaceInDataConnectorDataType.json","DataConnectorValidationError");
  });

  it("should pass when CEF data connector have valid set of permissions", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/validCEFConnectorPermissions.json");
  });

  it("should throw an exception when CEF data connector have Invalid set of permissions", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/invalidCEFConnectorPermissions.json","DataConnectorValidationError");
  });

  it("should pass when Syslog data connector have valid set of permissions", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/validSyslogConnectorPermissions.json") || await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/validSyslogConnectorDataSourcesPermissions.json");
  });

  it("should throw an exception when Syslog data connector have Invalid set of permissions", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/invalidSyslogConnectorPermissions.json","DataConnectorValidationError");
  });

  it("should pass when Azure Function data connector have valid set of permissions", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/Agari/validAzureFunctionConnectorPermissions.json");
  });

  it("should throw an exception when Azure Function data connector have Invalid set of permissions", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/Agari/invalidAzureFunctionConnectorPermissions.json","DataConnectorValidationError");
  });

  it("should pass when validSyslogDataConnector.json is valid", async () => {
    await checkValid(".script/tests/dataConnectorValidatorTest/testFiles/validAzureDiagnosticsDataConnector.json");
  });

  it("should throw an exception when Syslog data connector have Invalid set of permissions", async () => {
    await checkInvalid(".script/tests/dataConnectorValidatorTest/testFiles/invalidAzureDiagnosticsDataConnector.json","DataConnectorValidationError");
  });

  it("should pass customTableSchemaChecker when custom table and columns have meaningful descriptions", () => {
    const doc = {
      name: "VendorAudit_CL",
      type: "Microsoft.OperationalInsights/workspaces/tables",
      apiVersion: "2022-10-01",
      properties: {
        schema: {
          name: "VendorAudit_CL",
          description: "Vendor audit and sign-in events collected via the polling CCP connector.",
          columns: [
            { name: "TimeGenerated", type: "datetime" },
            { name: "EventId", type: "string", description: "Unique identifier for the vendor audit event." },
            { name: "ActorUpn", type: "string", description: "User principal name of the actor." },
          ],
        },
      },
    };
    const res = isValidCustomTableSchemas("Solutions/Vendor/Data Connectors/Vendor_tables.json", doc);
    expect(res.hasCustomTables).to.equal(true);
    expect(res.hasAnyTables).to.equal(true);
  });

  it("should fail customTableSchemaChecker when table or column descriptions are blank, placeholder, or unresolved ARM expressions", () => {
    const doc = {
      name: "VendorAudit_CL",
      type: "Microsoft.OperationalInsights/workspaces/tables",
      apiVersion: "2022-10-01",
      properties: {
        schema: {
          name: "VendorAudit_CL",
          description: "   ",
          columns: [
            { name: "TimeGenerated", type: "datetime" },
            { name: "EventId", type: "string", description: "TODO" },
            { name: "ActorUpn", type: "string", description: "[parameters('actorDesc')]" },
          ],
        },
      },
    };
    expect(() =>
      isValidCustomTableSchemas("Solutions/Vendor/Data Connectors/Vendor_tables.json", doc),
    ).to.throw(Error, /\[VAL-TBL-01\].*\[VAL-TBL-02\]/);
  });

  it("should exempt Microsoft-standard table configuration from customTableSchemaChecker", () => {
    const doc = {
      name: "[concat(parameters('workspace'), '/SecurityEvent')]",
      type: "Microsoft.OperationalInsights/workspaces/tables",
      apiVersion: "2022-10-01",
      properties: {
        plan: "Analytics",
        retentionInDays: 90,
      },
    };
    const discovered = discoverTablesInJsonObject(doc, "Solutions/Standard/Data Connectors/Retention.json");
    expect(discovered.filter(t => t.classification === "custom_log")).to.be.empty;
    expect(discovered.filter(t => t.classification === "microsoft_standard_config").length).to.equal(1);

    const res = isValidCustomTableSchemas("Solutions/Standard/Data Connectors/Retention.json", doc);
    expect(res.hasCustomTables).to.equal(false);
    expect(res.hasAnyTables).to.equal(true);
  });

  async function checkValid(filePath: string): Promise<Chai.PromisedAssertion> {
    let result = await IsValidDataConnectorSchema(filePath);
    expect(result).to.equal(ExitCode.SUCCESS);
  }

  async function checkInvalid(filePath: string, expectedError: string): Promise<Chai.PromisedAssertion> {
    expect(IsValidDataConnectorSchema(filePath)).eventually.rejectedWith(Error).and.have.property("name", expectedError);
  }
});
