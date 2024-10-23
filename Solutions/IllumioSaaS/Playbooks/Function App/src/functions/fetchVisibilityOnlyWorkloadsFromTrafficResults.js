const { app } = require('@azure/functions');
const {PCE_FQDN, PORT, ORG_ID, API_KEY, API_SECRET, MAX_WORKLOADS} = require('./constants');

app.http('fetchVisibilityOnlyWorkloadsFromTrafficResults', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        context.log(`Http function processed request for url "${request.url}"`);

        requestBody = await request.json()

        let traffic_results = requestBody?.traffic_results;
        let port = requestBody?.port;
        let protocol = requestBody?.protocol;        
        let skipPCEUpdate = requestBody?.skipPCEUpdate;

        traffic_results = JSON.stringify(traffic_results)
        let visibility_only_workloads = await getInboundWorkloadNames(traffic_results, context)

        return {             
            body: JSON.stringify({
                visibility_only_workloads: visibility_only_workloads,
                port: port,
                protocol: protocol,
                skipPCEUpdate: skipPCEUpdate
            })
        };
    }
});

async function getInboundWorkloadNames(traffic_results, context) {
    let dst_workloads = new Set();
    let visibility_only_workloads = new Set();
    let workload_map = new Map();
    let results = [];
    traffic_results = JSON.parse(traffic_results)    

    traffic_results.forEach(function (traffic_hash) {
        if (traffic_hash?.dst?.workload?.href != undefined) {
            dst_workloads.add(traffic_hash.dst.workload.hostname)
            workload_map.set(traffic_hash.dst.workload.hostname, traffic_hash.dst.workload.href)
        }        
    });
    
    context.log(`Count of dst workloads in traffic result is ${dst_workloads.size}`);
    visibility_only_workloads = await getVisibilityOnlyWorkloads(context);
    context.log(`Count of visibility_only_workloads for org is ${visibility_only_workloads.size}`);
    if (visibility_only_workloads.size > 0 && dst_workloads.size > 0) {
        dst_workloads = visibility_only_workloads.intersection(dst_workloads)
    }
    // return an array of objects such that each object is a map of hostname to href
    dst_workloads.forEach(function (workload) {
        href = workload_map.get(workload)
        context.log(`Workload: ${workload}`)
        results.push({ href: href })
    })

    return results;
}

async function getVisibilityOnlyWorkloads(context) {
    context.log(`Inside filterVisibilityOnlyWorkloads method`);
    return new Promise((resolve, reject) => {
        let path = `/api/v2/orgs/${ORG_ID}/workloads/?max_results=${MAX_WORKLOADS}&enforcement_modes=["visibility_only"]`

        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Authorization", 'Basic ' + Buffer.from(`${API_KEY}:${API_SECRET}`).toString('base64'));

        var requestOptions = {
            method: 'GET',
            headers: myHeaders,
            redirect: 'follow'
        };

        fetch(`https://${PCE_FQDN}:${PORT}${path}`, requestOptions)
        .then(response => response.text())
        .then(result => {
            let responseJson = JSON.parse(result);
            let workload_hostnames = new Set()
            // Loop through the workloads and extract hostnames
            responseJson.forEach(function (workload) {
                let hostname = workload['hostname'];
                workload_hostnames.add(hostname);  // Collect hostnames
            });            

            //context.log(`Response from getVisibilityOnlyWorkloads is ${workload_hostnames}`);            
            resolve(workload_hostnames)
        })
        .catch(error => {
            context.log('error', error)
            reject([]) // return an empty error
        });                                
    })
}