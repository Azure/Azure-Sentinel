import fs from "fs";
import path from "path";
import { DataConnectorValidationError } from "../validationError.js";

const TABLE_RESOURCE_TYPE = "microsoft.operationalinsights/workspaces/tables";
const WORKSPACE_RESOURCE_TYPE = "microsoft.operationalinsights/workspaces";
const DEPLOYMENT_RESOURCE_TYPE = "microsoft.resources/deployments";

const KNOWN_MICROSOFT_STANDARD_TABLES = new Set([
  "aadmanagedidentitysigninlogs",
  "aadnoninteractivesigninlogs",
  "aadprovisioninglogs",
  "aadribuObjects",
  "aadserviceprincipalsigninlogs",
  "aadspncredentialslifecycleevents",
  "aaduseriskevents",
  "aadusersigninlogs",
  "adfssigninlogs",
  "alert",
  "alertevidence",
  "alertinfo",
  "anomalies",
  "appdependencies",
  "appevents",
  "appexceptions",
  "apppageviews",
  "appperformancecounters",
  "apprequests",
  "appsystemevents",
  "apptraces",
  "asimauthenticationeventlogs",
  "asimauditeventlogs",
  "asimdhcpeventlogs",
  "asimdnseventlogs",
  "asimfileeventlogs",
  "asimnetworksessionlogs",
  "asimprocesseventlogs",
  "asimregistryeventlogs",
  "asimusergroupmanagementeventlogs",
  "asimwebessionlogs",
  "asimwebsessionlogs",
  "auditlogs",
  "awscloudtrail",
  "awsguardduty",
  "awss3serveraccess",
  "awsvpcflow",
  "azureactivity",
  "azureassessmentrecommendations",
  "azuredatabricksclusters",
  "azurediagnostics",
  "azuremetrics",
  "behavioranalytics",
  "cloudappevents",
  "commonsecuritylog",
  "computerGroup",
  "configdata",
  "configurationchange",
  "configurationdata",
  "containerimageinventory",
  "containerinventory",
  "containerlog",
  "containerlogv2",
  "containernodeinventory",
  "containerserviceLog",
  "coreazurebackup",
  "deviceevents",
  "devicefilecertificateinfo",
  "devicefileevents",
  "deviceimageloadevents",
  "deviceinfo",
  "devicelogonevents",
  "devicenetworkevents",
  "devicenetworkinfo",
  "deviceprocessevents",
  "deviceregistryevents",
  "devicetvmsecureconfigurationassessment",
  "devicetvmsoftwareinventory",
  "devicetvmsoftwarevulnerabilities",
  "dnsEvents",
  "dnsevents",
  "dnsinventory",
  "dynamics365activity",
  "emailattachmentinfo",
  "emailevents",
  "emailpostdeliveryevents",
  "emailurlinfo",
  "event",
  "functionapplogs",
  "gcpcloudlogging",
  "heartbeat",
  "huntingbookmark",
  "identitydirectoryevents",
  "identityinfo",
  "identitylogonevents",
  "identityqueryevents",
  " insightsmetrics",
  "insightsmetrics",
  "intuneauditlogs",
  "intunedevices",
  "intuneoperationallogs",
  "kubeevents",
  "kubehealth",
  "kubemonitoringevents",
  "kubenodeinventory",
  "kubepodinventory",
  "kubeservices",
  "laquerylogs",
  "linuxauditlog",
  "microsoftazuredatabricks",
  "microsoftgraphactivitylogs",
  "microsoftpurviewinformationprotection",
  "networkaccessconnectionevents",
  "networkaccessalerts",
  "networkaccesstraffic",
  "officeactivity",
  "operation",
  "perf",
  "powerbiactivity",
  "protectionstatus",
  "securityalert",
  "securitybaseline",
  "securitybaselinesummary",
  "securitydetection",
  "securityevent",
  "securityincident",
  "securityIoTRawEvent",
  "securitynestedrecommendation",
  "securityrecommendation",
  "sentinelhealth",
  "serviceprincipalriskEvents",
  "signinlogs",
  "storagebloblogs",
  "storagefilelogs",
  "storagequeuelogs",
  "storagetableslogs",
  "syslog",
  "SYSLOG",
  "threatintelindicators",
  "threatintelligenceindicator",
  "update",
  "updatesummary",
  "usage",
  "useraccessanalytics",
  "userpeeranalytics",
  "usriskEvents",
  "vmboundports",
  "vmcomputer",
  "vmconnection",
  "vmprocess",
  "w3ciislog",
  "windowsEvent",
  "windowsevent",
  "windowsfirewall",
  "wiredata",
].map(s => s.toLowerCase()));

const TRIVIAL_DESCRIPTION_TOKENS = new Set([
  "todo",
  "tbd",
  "n/a",
  "na",
  "none",
  "null",
  "nil",
  "unknown",
  "placeholder",
  "description",
  "table",
  "column",
  "field",
  "table description",
  "column description",
  "custom table",
  "custom column",
  "custom log",
  "log table",
]);

interface TemplateContext {
  parameters: Record<string, unknown>;
  variables: Record<string, unknown>;
}

export interface DiscoveredColumnSchema {
  name: string;
  dataType: string;
  description: string | null;
  descriptionValid: boolean;
  descriptionReason: string | null;
  isSystemColumn: boolean;
  sourceList: "columns" | "customColumns";
}

export interface DiscoveredTableSchema {
  tableName: string;
  classification: "custom_log" | "microsoft_standard_config";
  filePath: string;
  isPackaged: boolean;
  tableDescription: string | null;
  tableDescriptionValid: boolean;
  tableDescriptionReason: string | null;
  columns: DiscoveredColumnSchema[];
  customColumns: DiscoveredColumnSchema[];
  unresolvedReason: string | null;
}

function normalizeWhitespace(value: string): string {
  return value.trim().replace(/\s+/g, " ");
}

function normalizeTokenComparison(value: string): string {
  const withoutSuffix = value.replace(/_CL$/i, "");
  const camelSplit = withoutSuffix.replace(/([a-z0-9])([A-Z])/g, "$1 $2");
  return camelSplit
    .replace(/[^a-zA-Z0-9]+/g, " ")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

function isArmExpression(value: string): boolean {
  const trimmed = value.trim();
  return trimmed.startsWith("[") && trimmed.endsWith("]") && !trimmed.startsWith("[[");
}

function resolveSimpleArmExpression(rawValue: string, ctx: TemplateContext, depth = 0): string | null {
  if (depth > 8) {
    return null;
  }
  const trimmed = rawValue.trim();
  if (trimmed.startsWith("[[") && trimmed.endsWith("]")) {
    return trimmed.slice(1);
  }
  if (!isArmExpression(trimmed)) {
    return trimmed;
  }
  const inner = trimmed.slice(1, -1).trim();

  const paramMatch = /^parameters\(\s*'([^']+)'\s*\)$/i.exec(inner);
  if (paramMatch) {
    const paramName = paramMatch[1];
    const paramEntry = Object.entries(ctx.parameters).find(([k]) => k.toLowerCase() === paramName.toLowerCase())?.[1];
    if (paramEntry && typeof paramEntry === "object" && "defaultValue" in (paramEntry as Record<string, unknown>)) {
      const defVal = (paramEntry as Record<string, unknown>).defaultValue;
      if (typeof defVal === "string") {
        return resolveSimpleArmExpression(defVal, ctx, depth + 1);
      }
    }
    return null;
  }

  const varMatch = /^variables\(\s*'([^']+)'\s*\)$/i.exec(inner);
  if (varMatch) {
    const varName = varMatch[1];
    const varVal = Object.entries(ctx.variables).find(([k]) => k.toLowerCase() === varName.toLowerCase())?.[1];
    if (typeof varVal === "string") {
      return resolveSimpleArmExpression(varVal, ctx, depth + 1);
    }
    return null;
  }

  return null;
}

function extractTableNameFromArmName(rawName: unknown, ctx: TemplateContext): string {
  if (typeof rawName !== "string" || !rawName.trim()) {
    return "<unknown_table>";
  }
  const resolved = resolveSimpleArmExpression(rawName, ctx) ?? rawName.trim();
  if (!isArmExpression(resolved)) {
    const parts = resolved.split("/").map(p => p.trim()).filter(Boolean);
    return parts.length > 0 ? parts[parts.length - 1] : resolved;
  }
  const inner = resolved.slice(1, -1).trim();
  const stringLiterals = Array.from(inner.matchAll(/'([^']+)'/g)).map(m => m[1]);
  for (let i = stringLiterals.length - 1; i >= 0; i--) {
    const candidate = stringLiterals[i].replace(/^\/+/, "").trim();
    if (candidate && !candidate.includes("{") && !candidate.includes("}")) {
      const segs = candidate.split("/").filter(Boolean);
      if (segs.length > 0) {
        return segs[segs.length - 1];
      }
    }
  }
  return rawName.trim();
}

function evaluateDescriptionQuality(
  rawDescription: unknown,
  entityName: string,
  ctx: TemplateContext,
): { normalized: string | null; valid: boolean; reason: string | null } {
  if (rawDescription === undefined || rawDescription === null) {
    return { normalized: null, valid: false, reason: "missing_description" };
  }
  if (typeof rawDescription !== "string") {
    return { normalized: null, valid: false, reason: "non_string_description" };
  }
  const trimmed = rawDescription.trim();
  if (!trimmed) {
    return { normalized: "", valid: false, reason: "empty_description" };
  }
  if (isArmExpression(trimmed)) {
    const resolved = resolveSimpleArmExpression(trimmed, ctx);
    if (resolved === null || isArmExpression(resolved)) {
      return { normalized: null, valid: false, reason: "unresolved_schema_expression" };
    }
    return evaluateDescriptionQuality(resolved, entityName, ctx);
  }
  const normalized = normalizeWhitespace(trimmed);
  const lower = normalized.toLowerCase().replace(/[.!?:;,-]+$/g, "").trim();
  if (TRIVIAL_DESCRIPTION_TOKENS.has(lower)) {
    return { normalized, valid: false, reason: "placeholder_description" };
  }
  const normDescTokens = normalizeTokenComparison(normalized);
  const normEntityTokens = normalizeTokenComparison(entityName);
  if (!normDescTokens) {
    return { normalized, valid: false, reason: "no_alphanumeric_content" };
  }
  if (normEntityTokens && normDescTokens === normEntityTokens) {
    return { normalized, valid: false, reason: "repeats_entity_name" };
  }
  return { normalized, valid: true, reason: null };
}

function classifyTableResource(
  tableName: string,
  schemaObj: Record<string, unknown> | null,
): "custom_log" | "microsoft_standard_config" {
  const lowerName = tableName.trim().toLowerCase();
  const hasCustomSuffix = lowerName.endsWith("_cl");
  if (hasCustomSuffix) {
    return "custom_log";
  }
  const hasColumns =
    schemaObj !== null &&
    ((Array.isArray(schemaObj.columns) && schemaObj.columns.length > 0) ||
      (Array.isArray(schemaObj.customColumns) && schemaObj.customColumns.length > 0) ||
      typeof schemaObj.columns === "string" ||
      typeof schemaObj.customColumns === "string");

  if (KNOWN_MICROSOFT_STANDARD_TABLES.has(lowerName) && !hasColumns) {
    return "microsoft_standard_config";
  }
  if (!hasColumns) {
    return "microsoft_standard_config";
  }
  return "custom_log";
}

function parseTableResource(
  resource: Record<string, unknown>,
  filePath: string,
  isPackaged: boolean,
  ctx: TemplateContext,
): DiscoveredTableSchema {
  const props = resource.properties;
  if (typeof props === "string" && isArmExpression(props)) {
    const fallbackName = extractTableNameFromArmName(resource.name, ctx);
    return {
      tableName: fallbackName,
      classification: "custom_log",
      filePath,
      isPackaged,
      tableDescription: null,
      tableDescriptionValid: false,
      tableDescriptionReason: "unresolved_schema_expression",
      columns: [],
      customColumns: [],
      unresolvedReason: "properties_is_arm_expression",
    };
  }
  const propsObj = props && typeof props === "object" && !Array.isArray(props)
    ? (props as Record<string, unknown>)
    : {};
  const rawSchema = propsObj.schema;
  if (typeof rawSchema === "string" && isArmExpression(rawSchema)) {
    const fallbackName = extractTableNameFromArmName(resource.name, ctx);
    return {
      tableName: fallbackName,
      classification: "custom_log",
      filePath,
      isPackaged,
      tableDescription: null,
      tableDescriptionValid: false,
      tableDescriptionReason: "unresolved_schema_expression",
      columns: [],
      customColumns: [],
      unresolvedReason: "schema_is_arm_expression",
    };
  }
  const schemaObj = rawSchema && typeof rawSchema === "object" && !Array.isArray(rawSchema)
    ? (rawSchema as Record<string, unknown>)
    : null;

  let tableName = extractTableNameFromArmName(resource.name, ctx);
  if (schemaObj && typeof schemaObj.name === "string" && schemaObj.name.trim()) {
    const resolvedSchemaName = resolveSimpleArmExpression(schemaObj.name, ctx);
    if (resolvedSchemaName && !isArmExpression(resolvedSchemaName)) {
      tableName = resolvedSchemaName.trim();
    } else if (isArmExpression(schemaObj.name)) {
      return {
        tableName,
        classification: "custom_log",
        filePath,
        isPackaged,
        tableDescription: null,
        tableDescriptionValid: false,
        tableDescriptionReason: "unresolved_schema_expression",
        columns: [],
        customColumns: [],
        unresolvedReason: "schema_name_is_arm_expression",
      };
    }
  }

  const classification = classifyTableResource(tableName, schemaObj);
  if (classification === "microsoft_standard_config") {
    return {
      tableName,
      classification,
      filePath,
      isPackaged,
      tableDescription: null,
      tableDescriptionValid: true,
      tableDescriptionReason: null,
      columns: [],
      customColumns: [],
      unresolvedReason: null,
    };
  }

  if (!schemaObj) {
    return {
      tableName,
      classification: "custom_log",
      filePath,
      isPackaged,
      tableDescription: null,
      tableDescriptionValid: false,
      tableDescriptionReason: "missing_schema_object",
      columns: [],
      customColumns: [],
      unresolvedReason: "missing_schema_object",
    };
  }

  const tableDescEval = evaluateDescriptionQuality(schemaObj.description, tableName, ctx);
  const allColumns: DiscoveredColumnSchema[] = [];
  let unresolvedReason: string | null =
    isArmExpression(tableName) || /\b(parameters|variables)\s*\(/i.test(tableName) || tableName.startsWith("<")
      ? "unresolved_table_name_expression"
      : null;

  for (const listKey of ["columns", "customColumns"] as const) {
    const rawCols = schemaObj[listKey];
    if (rawCols === undefined || rawCols === null) {
      continue;
    }
    if (typeof rawCols === "string" && isArmExpression(rawCols)) {
      unresolvedReason = `${listKey}_is_arm_expression`;
      continue;
    }
    if (!Array.isArray(rawCols)) {
      unresolvedReason = `${listKey}_not_array`;
      continue;
    }
    for (let idx = 0; idx < rawCols.length; idx++) {
      const colItem = rawCols[idx];
      if (!colItem || typeof colItem !== "object" || Array.isArray(colItem)) {
        unresolvedReason = `${listKey}[${idx}]_not_object`;
        continue;
      }
      const colObj = colItem as Record<string, unknown>;
      const rawColName = colObj.name;
      const colName = typeof rawColName === "string" ? (resolveSimpleArmExpression(rawColName, ctx) ?? rawColName.trim()) : "";
      if (!colName || isArmExpression(colName)) {
        unresolvedReason = `${listKey}[${idx}]_unresolved_column_name`;
        continue;
      }
      const rawColType = colObj.type ?? colObj.dataType ?? "string";
      const colType = typeof rawColType === "string" ? rawColType.trim() : "string";
      // Any column explicitly declared in schema.columns or schema.customColumns of an authored
      // custom-log table declaration must have a valid description (even if named TimeGenerated,
      // Computer, or RawData). Only provider-injected standardColumns are system-exempt.
      const isSystemColumn = false;
      const descEval = evaluateDescriptionQuality(colObj.description, colName, ctx);
      allColumns.push({
        name: colName,
        dataType: colType,
        description: descEval.normalized,
        descriptionValid: descEval.valid,
        descriptionReason: descEval.reason,
        isSystemColumn,
        sourceList: listKey,
      });
    }
  }

  const customColumns = allColumns.filter(c => !c.isSystemColumn);
  if (!unresolvedReason && customColumns.length === 0) {
    unresolvedReason = "no_custom_columns_defined";
  }

  return {
    tableName,
    classification: "custom_log",
    filePath,
    isPackaged,
    tableDescription: tableDescEval.normalized,
    tableDescriptionValid: tableDescEval.valid,
    tableDescriptionReason: tableDescEval.reason,
    columns: allColumns,
    customColumns,
    unresolvedReason,
  };
}

function walkArmNodeForTables(
  node: unknown,
  filePath: string,
  isPackaged: boolean,
  ctx: TemplateContext,
  results: DiscoveredTableSchema[],
  parentType?: string,
): void {
  if (!node || typeof node !== "object") {
    return;
  }
  if (Array.isArray(node)) {
    for (const item of node) {
      walkArmNodeForTables(item, filePath, isPackaged, ctx, results, parentType);
    }
    return;
  }

  const obj = node as Record<string, unknown>;
  const nextCtx: TemplateContext = {
    parameters:
      obj.parameters && typeof obj.parameters === "object" && !Array.isArray(obj.parameters)
        ? { ...ctx.parameters, ...(obj.parameters as Record<string, unknown>) }
        : ctx.parameters,
    variables:
      obj.variables && typeof obj.variables === "object" && !Array.isArray(obj.variables)
        ? { ...ctx.variables, ...(obj.variables as Record<string, unknown>) }
        : ctx.variables,
  };

  const rawType = typeof obj.type === "string" ? obj.type.trim().toLowerCase() : "";
  const isChildTableResource =
    rawType === "tables" && parentType === WORKSPACE_RESOURCE_TYPE;

  if (rawType === TABLE_RESOURCE_TYPE || isChildTableResource) {
    results.push(parseTableResource(obj, filePath, isPackaged, nextCtx));
  }

  if (Array.isArray(obj.resources)) {
    walkArmNodeForTables(obj.resources, filePath, isPackaged, nextCtx, results, rawType || parentType);
  }

  const props = obj.properties && typeof obj.properties === "object" && !Array.isArray(obj.properties)
    ? (obj.properties as Record<string, unknown>)
    : null;
  if (props) {
    if (rawType === DEPLOYMENT_RESOURCE_TYPE && props.template && typeof props.template === "object") {
      walkArmNodeForTables(props.template, filePath, isPackaged, nextCtx, results, rawType);
    }
    if (props.mainTemplate && typeof props.mainTemplate === "object") {
      walkArmNodeForTables(props.mainTemplate, filePath, isPackaged, nextCtx, results, rawType);
    }
  }
}

export function discoverTablesInJsonObject(
  jsonObj: unknown,
  filePath: string,
): DiscoveredTableSchema[] {
  const normalizedPath = filePath.replace(/\\/g, "/");
  const isPackaged = /(^|\/)Package\/mainTemplate\.json$/i.test(normalizedPath);
  const results: DiscoveredTableSchema[] = [];
  walkArmNodeForTables(
    jsonObj,
    normalizedPath,
    isPackaged,
    { parameters: {}, variables: {} },
    results,
  );
  return results;
}

function findSolutionDirForFile(filePath: string): string | null {
  const normalized = path.resolve(filePath);
  const parts = normalized.split(path.sep);
  const solIdx = parts.findIndex(p => p.toLowerCase() === "solutions");
  if (solIdx >= 0 && solIdx + 1 < parts.length) {
    return parts.slice(0, solIdx + 2).join(path.sep);
  }
  return null;
}

function collectSolutionSourceTableSchemas(solutionDir: string): DiscoveredTableSchema[] {
  const results: DiscoveredTableSchema[] = [];
  const skipDirs = new Set(["package", "logs", "reports", "evidence", ".git", "node_modules"]);

  function walk(dir: string): void {
    if (!fs.existsSync(dir)) {
      return;
    }
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (skipDirs.has(entry.name.toLowerCase())) {
          continue;
        }
        walk(fullPath);
      } else if (entry.isFile() && entry.name.toLowerCase().endsWith(".json")) {
        try {
          const parsed = JSON.parse(fs.readFileSync(fullPath, "utf8"));
          const relPath = path.relative(process.cwd(), fullPath).replace(/\\/g, "/");
          results.push(...discoverTablesInJsonObject(parsed, relPath));
        } catch {
          // Syntax errors are handled by JSON Syntax validator
        }
      }
    }
  }

  walk(solutionDir);
  return results;
}

function validateSingleFileTableSchemas(tables: DiscoveredTableSchema[], filePath: string): string[] {
  const errors: string[] = [];
  const customTables = tables.filter(t => t.classification === "custom_log");

  for (const tbl of customTables) {
    if (tbl.unresolvedReason) {
      errors.push(
        `[VAL-TBL-01/02] Custom table '${tbl.tableName}' in '${filePath}' has an unresolved or invalid schema definition (${tbl.unresolvedReason}).`,
      );
    }
    if (!tbl.tableDescriptionValid) {
      errors.push(
        `[VAL-TBL-01] Custom table '${tbl.tableName}' in '${filePath}' is missing a valid properties.schema.description (${tbl.tableDescriptionReason || "invalid"}).`,
      );
    }
    const invalidCols = tbl.customColumns.filter(c => !c.descriptionValid);
    if (invalidCols.length > 0) {
      const colSummary = invalidCols
        .map(c => `${c.name} (${c.descriptionReason || "missing_description"})`)
        .join(", ");
      errors.push(
        `[VAL-TBL-02] Custom table '${tbl.tableName}' in '${filePath}' has ${invalidCols.length}/${tbl.customColumns.length} custom column(s) without valid descriptions: ${colSummary}.`,
      );
    }
  }

  return errors;
}

function validatePackagePreservation(
  sourceTables: DiscoveredTableSchema[],
  packagedTables: DiscoveredTableSchema[],
  packageRelPath: string,
): string[] {
  const errors: string[] = [];
  const customSource = sourceTables.filter(t => t.classification === "custom_log");
  if (customSource.length === 0) {
    return errors;
  }

  const sourceByLower = new Map<string, DiscoveredTableSchema[]>();
  for (const tbl of customSource) {
    const key = tbl.tableName.toLowerCase();
    const list = sourceByLower.get(key) || [];
    list.push(tbl);
    sourceByLower.set(key, list);
  }

  const packagedByLower = new Map<string, DiscoveredTableSchema>();
  for (const tbl of packagedTables.filter(t => t.classification === "custom_log")) {
    packagedByLower.set(tbl.tableName.toLowerCase(), tbl);
  }

  for (const [key, srcList] of sourceByLower.entries()) {
    const canonical = srcList[0];
    if (srcList.length > 1) {
      const refDesc = canonical.tableDescriptionValid ? canonical.tableDescription : null;
      const refCols = new Map(
        canonical.customColumns.map(c => [c.name.toLowerCase(), c.descriptionValid ? c.description : null]),
      );
      for (const dup of srcList.slice(1)) {
        const dupDesc = dup.tableDescriptionValid ? dup.tableDescription : null;
        const dupCols = new Map(
          dup.customColumns.map(c => [c.name.toLowerCase(), c.descriptionValid ? c.description : null]),
        );
        let conflict = refDesc === null || dupDesc === null || refDesc !== dupDesc || refCols.size !== dupCols.size;
        if (!conflict) {
          for (const [cName, cDesc] of refCols.entries()) {
            if (!dupCols.has(cName) || dupCols.get(cName) === null || cDesc === null || dupCols.get(cName) !== cDesc) {
              conflict = true;
              break;
            }
          }
        }
        if (conflict) {
          errors.push(
            `[VAL-TBL-03] Conflicting duplicate custom table definitions for '${canonical.tableName}' across source files (${srcList.map(s => s.filePath).join(", ")}).`,
          );
          break;
        }
      }
    }

    const pkgTbl = packagedByLower.get(key);
    if (!pkgTbl) {
      errors.push(
        `[VAL-TBL-03] Custom table '${canonical.tableName}' defined in '${canonical.filePath}' is missing from '${packageRelPath}'.`,
      );
      continue;
    }

    if (
      !canonical.tableDescriptionValid ||
      !pkgTbl.tableDescriptionValid ||
      !canonical.tableDescription ||
      !pkgTbl.tableDescription ||
      canonical.tableDescription !== pkgTbl.tableDescription
    ) {
      errors.push(
        `[VAL-TBL-03] Custom table '${canonical.tableName}' table description in '${packageRelPath}' does not preserve the authored description in '${canonical.filePath}'.`,
      );
    }

    const pkgCols = new Map(pkgTbl.customColumns.map(c => [c.name.toLowerCase(), c]));
    for (const srcCol of canonical.customColumns) {
      const pkgCol = pkgCols.get(srcCol.name.toLowerCase());
      if (!pkgCol) {
        errors.push(
          `[VAL-TBL-03] Custom column '${canonical.tableName}.${srcCol.name}' from '${canonical.filePath}' is missing in '${packageRelPath}'.`,
        );
      } else if (
        !srcCol.descriptionValid ||
        !pkgCol.descriptionValid ||
        !srcCol.description ||
        !pkgCol.description ||
        srcCol.description !== pkgCol.description
      ) {
        errors.push(
          `[VAL-TBL-03] Custom column '${canonical.tableName}.${srcCol.name}' description in '${packageRelPath}' does not preserve the authored description in '${canonical.filePath}'.`,
        );
      }
    }
  }

  return errors;
}

export function isValidCustomTableSchemas(
  filePath: string,
  parsedJson?: unknown,
): { hasCustomTables: boolean; hasAnyTables: boolean } {
  if (filePath.includes("Templates")) {
    return { hasCustomTables: false, hasAnyTables: false };
  }

  const jsonObj = parsedJson !== undefined ? parsedJson : JSON.parse(fs.readFileSync(filePath, "utf8"));
  const discovered = discoverTablesInJsonObject(jsonObj, filePath);
  const solutionDir = findSolutionDirForFile(filePath);
  const packagePath = solutionDir ? path.join(solutionDir, "Package", "mainTemplate.json") : "";
  const isMainTemplate = Boolean(
    packagePath &&
      fs.existsSync(packagePath) &&
      path.resolve(filePath).toLowerCase() === path.resolve(packagePath).toLowerCase(),
  );
  const allSolutionSourceTables = isMainTemplate && solutionDir ? collectSolutionSourceTableSchemas(solutionDir) : [];
  const sourceCustomTables = allSolutionSourceTables.filter(t => t.classification === "custom_log");

  if (discovered.length === 0 && sourceCustomTables.length === 0) {
    return { hasCustomTables: false, hasAnyTables: false };
  }

  const customTables = discovered.filter(t => t.classification === "custom_log");
  if (customTables.length === 0 && sourceCustomTables.length === 0) {
    return { hasCustomTables: false, hasAnyTables: discovered.length > 0 };
  }

  const errors = validateSingleFileTableSchemas(discovered, filePath);
  if (isMainTemplate && allSolutionSourceTables.length > 0) {
    for (const srcTable of sourceCustomTables) {
      errors.push(...validateSingleFileTableSchemas([srcTable], srcTable.filePath));
    }
  }

  if (solutionDir && packagePath) {
    const packageRelPath = path.relative(process.cwd(), packagePath).replace(/\\/g, "/");
    if (!fs.existsSync(packagePath)) {
      errors.push(
        `[VAL-TBL-03] Custom table(s) (${customTables.map(t => t.tableName).join(", ")}) in '${filePath}' cannot verify package preservation because '${packageRelPath}' is missing.`,
      );
    } else {
      try {
        const pkgJson = isMainTemplate ? jsonObj : JSON.parse(fs.readFileSync(packagePath, "utf8"));
        const packagedTables = isMainTemplate ? discovered : discoverTablesInJsonObject(pkgJson, packageRelPath);
        const solutionSources = isMainTemplate ? allSolutionSourceTables : collectSolutionSourceTableSchemas(solutionDir);
        const targetTableNames = new Set(customTables.map(t => t.tableName.toLowerCase()));
        const sourceTables = isMainTemplate
          ? solutionSources
          : solutionSources.filter(t => targetTableNames.has(t.tableName.toLowerCase()));
        errors.push(
          ...validatePackagePreservation(
            sourceTables.length > 0 ? sourceTables : discovered,
            packagedTables,
            packageRelPath,
          ),
        );
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : String(e);
        errors.push(`[VAL-TBL-03] Failed to inspect '${packageRelPath}' for table schema preservation: ${msg}`);
      }
    }
  }

  if (errors.length > 0) {
    throw new DataConnectorValidationError(Array.from(new Set(errors)).join(" | "));
  }

  return { hasCustomTables: true, hasAnyTables: true };
}
