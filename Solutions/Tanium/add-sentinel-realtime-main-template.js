const fs = require('fs');

const args = process.argv.slice(2);

const loadJson = (filepath) => {
    return JSON.parse(fs.readFileSync(filepath));
}

const help = () => {
    console.log("")
    console.log("NAME");
    console.log("  add-sentinel-realtime-main-template.js");
    console.log("")
    console.log("PURPOSE");
    console.log("  Outputs a createUiDefinition.json with the Sentinel Realtime UI declarations included.")
    console.log("")
    console.log("USAGE");
    console.log("  node add-sentinel-realtime-main-template.js TARGET_MAIN_TEMPLATE_FILE_PATH SENTINEL_REALTIME_FILE_PATH");
    console.log("")
    console.log("EXAMPLE")
    console.log("  node add-sentinel-realtime-main-template.js ./Package/mainTemplate.json ~/ghe/stephen-ball/microsoft-integrations/sentinel-realtime/mainTemplate.json")
    console.log("")
}

if (args.length !== 2) {
    help();
    process.exit(1);
}

const sentinelRealtimeFilePath = args[0];
const targetFilePath = args[1];

const targetFile = loadJson(targetFilePath);
const sentinelRealtimeFile = loadJson(sentinelRealtimeFilePath);

// add Sentinel Realtime parameters
targetFile.parameters = {...targetFile.parameters, ...sentinelRealtimeFile.parameters};

// add Sentinel Realtime resources
targetFile.resources = [...targetFile.resources, ...sentinelRealtimeFile.resources]

console.log(JSON.stringify(targetFile, null, 2));