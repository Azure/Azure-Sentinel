const fs = require('fs');

const args = process.argv.slice(2);

const loadJson = (filepath) => {
    return JSON.parse(fs.readFileSync(filepath));
}

const help = () => {
    console.log("")
    console.log("NAME");
    console.log("  add-sentinel-realtime-create-ui-definition.js");
    console.log("")
    console.log("PURPOSE");
    console.log("  Outputs a createUiDefinition.json with the Sentinel Realtime UI declarations included.")
    console.log("")
    console.log("USAGE");
    console.log("  node add-sentinel-realtime-create-ui-definition.js TARGET_UI_JSON_FILE_PATH SENTINEL_REALTIME_FILE_PATH");
    console.log("")
    console.log("EXAMPLE")
    console.log("  node add-sentinel-realtime-create-ui-definition.js ./Package/createUiDefinition.json ~/ghe/stephen-ball/microsoft-integrations/sentinel-realtime/createUiDefinition.json")
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

// check that targetFile doesn't have taniumSentinelRealtime already
if (targetFile.parameters.steps.find((step) => {
    return step.name === 'taniumSentinelRealtime';
})) {
    console.error(`${targetFilePath} already has a taniumSentinelRealtime step defined`);
    process.exit(1);
}

// add Sentinel Realtime steps
targetFile.parameters.steps = [...targetFile.parameters.steps, ...sentinelRealtimeFile.parameters.steps];

// add Sentinel Realtime outputs
targetFile.parameters.outputs = {...targetFile.parameters.outputs, ...sentinelRealtimeFile.parameters.outputs};

console.log(JSON.stringify(targetFile, null, 2));