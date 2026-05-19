function logToAzureDevops(msg, type) {
    const lines = msg.split("\n");
    for (const line of lines) {
        console.log(`##vso[task.logissue type=${type}]${line}`);
    }
}
export const logError = (msg) => logToAzureDevops(msg, "error");
export const logWarning = (msg) => logToAzureDevops(msg, "warning");
//# sourceMappingURL=logger.js.map