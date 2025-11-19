interface ValidationError {
    name: string;
}
export declare class WorkbookValidationError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export declare class LogoValidationError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export declare class DataConnectorValidationError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export declare class WorkbookTemplatesValidationError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export declare class PlaybookValidationError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export declare class SampleDataValidationError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export declare class MainTemplateDomainVerticalValidationError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export declare class MainTemplateSupportObjectValidationError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export declare class InvalidFileContentError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export declare class InvalidSolutionIDValidationError extends Error implements ValidationError {
    name: string;
    constructor(message?: string);
}
export {};
//# sourceMappingURL=validationError.d.ts.map