const { app } = require('@azure/functions');
const {PCE_FQDN, PORT, ORG_ID, API_KEY, API_SECRET} = require('./constants');

app.http('changeWorkloadEnforcementState', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        context.log('Inside changeWorkloadEnforcementState')
        
        let requestBody = await request.json();

        let workloads = requestBody?.visibility_only_workloads;

        let skipPCEUpdate = requestBody?.skipPCEUpdate;

        if (skipPCEUpdate) {            
            return {
                body: JSON.stringify({
                    response: 'Skipping updating workloads on PCE since skipPCEUpdate flag is set to true'
                })
            }
        }        

        if (workloads.length == 0) {
            context.log("There are no workloads in visibility state for the given port/protocol combination. Hence exiting")
            return {
                body: JSON.stringify({
                    response: "No visibility only workloads for the given port/protocol combination"
                })
            }
        }

        response = await changeEnforcementState(workloads, context);
        return { 
            body: JSON.stringify({              
              response: response
            })
        };                    
    }
});

async function changeEnforcementState(workloads, context) {
    context.log(`Inside changeEnforcementState method`);
    return new Promise((resolve, reject) => {
        let path = `/api/v2/orgs/${ORG_ID}/workloads/update`

        // workloads is an arr of objects where each obj has one key, "href" which points to workload href
        var raw = JSON.stringify({
            "enforcement_mode": "selective",
            "workloads": workloads
        });
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Authorization", 'Basic ' + Buffer.from(`${API_KEY}:${API_SECRET}`).toString('base64'));

        var requestOptions = {
            method: 'PUT',
            body: raw,
            headers: myHeaders,
            redirect: 'follow'
        };

        fetch(`https://${PCE_FQDN}:${PORT}${path}`, requestOptions)
        .then(response => response.json()) // parse the JSON from the response
        .then(data => {
            context.log('Response Body:', data); // log the parsed response body
            resolve(data); // pass the parsed response to the resolve function
        })
        .catch(error => {
            context.log('error', error)
            reject(error) // return an empty error
        });                                
    })    
}

