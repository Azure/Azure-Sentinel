const { app } = require('@azure/functions');
const {PCE_FQDN, PORT, ORG_ID, API_KEY, API_SECRET} = require('./constants');


app.http('createAndProvisionDenyRule', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        let requestBody = await request.json();
        let port = requestBody?.port;
        let protocol = requestBody?.protocol;
        let visibility_only_workloads = requestBody.visibility_only_workloads;
        let skipPCEUpdate = requestBody?.skipPCEUpdate;

        if (skipPCEUpdate) {            
            return {
                body: JSON.stringify({
                    response: 'Skipping updating PCE with deny rule since skipPCEUpdate flag is set to true'
                })
            };
        }

        let response = ''
        context.log(`visibility only workloads are ${JSON.stringify(visibility_only_workloads)}`);

        let anyIPListHref = await getIPListHref(context);
        
        context.log(`Iplist href is ${anyIPListHref}`);
        
        let ebHref = await createEnforcementBoundary(port, protocol, anyIPListHref, context);
        
        
        if (ebHref.includes("input_validation_error")) {
            context.log("Deny rule creation ran into input validation error, retry with proper payload");
            return { 
                body: JSON.stringify({              
                  response: 'Deny Rule Input Validation Error',
                  visibility_only_workloads: visibility_only_workloads
                })
            };
        }

        else if (ebHref.includes("rule_name_in_use")) {
            context.log("Deny rule creation ran into rule name in use error, the rule name already exists");
            return { 
                body: JSON.stringify({              
                  response: 'Deny rule already exists, unable to create with same name',
                  visibility_only_workloads: visibility_only_workloads
                })
            };            
        }

        context.log(`enforcement boundary href is ${ebHref}`);

        response = await provisionPolicyObject(ebHref, context);
        
        return { 
            body: JSON.stringify({              
              response: response,
              visibility_only_workloads: visibility_only_workloads,
              skipPCEUpdate: skipPCEUpdate
            })
        };
    }
});

async function getIPListHref(context) {
    return new Promise((resolve, reject) => {
        const name = encodeURIComponent("Any (0.0.0.0/0 and ::/0)");
        let path = `/api/v2/orgs/${ORG_ID}/sec_policy/active/ip_lists?name=${name}`

        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Authorization", 'Basic ' + Buffer.from(`${API_KEY}:${API_SECRET}`).toString('base64'));

        var requestOptions = {
            method: 'GET',
            headers: myHeaders,
            redirect: 'follow'
        };

        fetch(`https://${PCE_FQDN}:${PORT}${path}`, requestOptions)
        .then(response => response.json())
        .then(data => {
            context.log('Response Body:', data); // log the parsed response body
            let iplistHref = data[0].href
            resolve(iplistHref); // pass the parsed response to the resolve function
        })
        .catch(error => {
            context.log('error', error)
            reject(error) // return an empty error
        });  
    })
}

// Create enforcement boundary from all ips to all workloads on provided port/protocol
async function createEnforcementBoundary(port, protocol, anyIPListHref, context) {
    return new Promise((resolve, reject) => {
        let path = `/api/v2/orgs/${ORG_ID}/sec_policy/draft/enforcement_boundaries`

        // workloads is an arr of objects where each obj has one key, "href" which points to workload href
        var raw = JSON.stringify({
            "name":`Sentinel Playbook Enforcement Boundary for port - ${port} and protocol - ${protocol}`,
            "enabled":true,
            "providers":[{"actors":"ams"}],
            "consumers":[{"ip_list":{"href": anyIPListHref}}],
            "network_type":"brn",
            "ingress_services":[{"proto": protocol,"port": port}]
        });
        
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Authorization", 'Basic ' + Buffer.from(`${API_KEY}:${API_SECRET}`).toString('base64'));

        var requestOptions = {
            method: 'POST',
            body: raw,
            headers: myHeaders,
            redirect: 'follow'
        };

        fetch(`https://${PCE_FQDN}:${PORT}${path}`, requestOptions)
        .then(response => response.json()) // parse the JSON from the response
        .then(data => {
            context.log('Response Body:', data); // log the parsed response body
            let ebHref = data.href
            // handle error cases
            if (data[0]?.token == 'input_validation_error') {
                resolve("input_validation_error");
            }
            else if (data[0]?.token == 'rule_name_in_use') {
                resolve("rule_name_in_use");
            }
            resolve(ebHref); // pass the parsed response to the resolve function
        })
        .catch(error => {
            context.log('error', error);
            reject(error); // return an empty error
        });                              
    })   

}

async function provisionPolicyObject(ebHref, context) {
    return new Promise((resolve, reject) => {
        let path = `/api/v2/orgs/${ORG_ID}/sec_policy`

        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Authorization", 'Basic ' + Buffer.from(`${API_KEY}:${API_SECRET}`).toString('base64'));

        var raw = JSON.stringify({
            "update_description":`Provisioning changes from Sentinel Playbook for ${ebHref}`,
            "change_subset":{"enforcement_boundaries":[{"href": ebHref}]}
        })

        var requestOptions = {
            method: 'POST',
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