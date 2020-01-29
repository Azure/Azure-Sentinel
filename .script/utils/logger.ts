function logToAzureDevops(msg: string, type: string) {
  const lines = msg.split("\n");
  for (const line of lines) {
    console.log(`##vso[task.logissue type=${type}]${line}`);
  }
}

export const logError = (msg: string) => logToAzureDevops(msg, "error");

export const logWarning = (msg: string) => logToAzureDevops(msg, "warning");
