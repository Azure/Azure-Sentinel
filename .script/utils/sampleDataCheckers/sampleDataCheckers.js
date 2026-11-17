import { SampleDataValidationError } from "../validationError.js";
const regEmail = "sanitized@sanitized.com";
const tableCatalogPathRegex = /(?:^|[\\/])Sample Data[\\/]Tables[\\/](?:([^\\/]+)[\\/])?([^\\/]+\.json)$/i;
const ALLOWED_CATALOG_EMAILS = new Set([
    "sanitized@sanitized.com",
    "user@example.com",
    "admin@contoso.com",
    "synthetic-user@example.invalid",
]);
const ALLOWED_CATALOG_DOMAINS = new Set([
    "sanitized.com",
    "example.com",
    "example.org",
    "example.net",
    "example.edu",
    "contoso.com",
    "fabrikam.com",
]);
const RFC_2606_RESERVED_TLDS = [".example", ".invalid", ".test", ".localhost"];
export function isTableCatalogSampleDataPath(filePath) {
    return tableCatalogPathRegex.test(filePath);
}
export function isAllowedCatalogEmail(email) {
    const normalized = email.trim().toLowerCase();
    if (ALLOWED_CATALOG_EMAILS.has(normalized)) {
        return true;
    }
    const atIndex = normalized.lastIndexOf("@");
    if (atIndex <= 0 || atIndex === normalized.length - 1) {
        return false;
    }
    const domain = normalized.slice(atIndex + 1);
    if (ALLOWED_CATALOG_DOMAINS.has(domain)) {
        return true;
    }
    for (const allowedDomain of ALLOWED_CATALOG_DOMAINS) {
        if (domain.endsWith(`.${allowedDomain}`)) {
            return true;
        }
    }
    for (const reservedTld of RFC_2606_RESERVED_TLDS) {
        if (domain === reservedTld.slice(1) || domain.endsWith(reservedTld)) {
            return true;
        }
    }
    return false;
}
function isPlainNonEmptyObject(value) {
    return (typeof value === "object" &&
        value !== null &&
        !Array.isArray(value) &&
        Object.keys(value).length > 0);
}
export function isValidTableCatalogSampleData(sampleDataContent, filePath = "") {
    if (!isPlainNonEmptyObject(sampleDataContent)) {
        throw new SampleDataValidationError(`Sample Data/Tables catalog file must be a non-empty JSON object.`);
    }
    const normalizedPath = filePath.replace(/\\/g, "/").toLowerCase();
    const isMetadataFile = normalizedPath.endsWith("/metadata.json") || normalizedPath === "metadata.json";
    if (isMetadataFile) {
        const tableField = sampleDataContent.table ??
            sampleDataContent.tableName ??
            sampleDataContent.name;
        const hasTableField = typeof tableField === "string" && tableField.trim().length > 0;
        const columnsField = sampleDataContent.columns ??
            sampleDataContent.schema ??
            sampleDataContent.fields;
        const hasColumnsMetadata = isPlainNonEmptyObject(columnsField) ||
            (Array.isArray(columnsField) && columnsField.length > 0);
        if (!hasTableField || !hasColumnsMetadata) {
            throw new SampleDataValidationError(`Sample Data/Tables metadata.json must contain required table and columns/schema metadata fields.`);
        }
    }
    const emails = extractEmails(JSON.stringify(sampleDataContent)) || [];
    const invalidEmails = emails.filter(email => !isAllowedCatalogEmail(email));
    if (invalidEmails.length > 0) {
        throw new SampleDataValidationError(`Catalog sample data email must use sanitized@sanitized.com, user@example.com, admin@contoso.com, or an RFC 2606 example domain.`);
    }
    return true;
}
export function isValidSampleData(sampleDataContent) {
    console.log(sampleDataContent.length);
    if (!Array.isArray(sampleDataContent) ||
        sampleDataContent.length <= 0 ||
        sampleDataContent.length == undefined) {
        throw new SampleDataValidationError(`Sample data file data must be in the form of array.`);
    }
    let email = extractEmails(JSON.stringify(sampleDataContent));
    let varEmail = email?.filter(e => e != regEmail);
    if (varEmail !== undefined && varEmail.length > 0) {
        throw new SampleDataValidationError(`Email must be sanitized@sanitized.com`);
    }
    return true;
}
function extractEmails(sampleDataContent) {
    return sampleDataContent.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/gi);
}
//# sourceMappingURL=sampleDataCheckers.js.map