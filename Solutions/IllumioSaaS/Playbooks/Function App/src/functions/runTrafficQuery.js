const { app } = require('@azure/functions');
const {PCE_FQDN, PORT, ORG_ID, API_KEY, API_SECRET, MAX_WORKLOADS} = require('./constants');

app.http('runTrafficQuery', {
    methods: ['POST'],
    authLevel: 'anonymous',
    handler: async (request, context) => {
        context.log(`Http function processed request for url "${request.url}"`);
        context.log(`request is "${JSON.stringify(request)}"`);

        // Parse the request body as JSON (assuming JSON body)
        let requestBody = await request.json();

        let port = requestBody?.port;
        let protocol = requestBody?.protocol;
        
        // use this flag when enduser doesnt want to update PCE, default value is false
        let skipPCEUpdate = requestBody?.skipPCEUpdate || false; 

        let async_href = await runTrafficQuery(port, protocol, context);
        context.log(`Async href returned is ${async_href}`);
        
        let traffic_results = ''; // list of all inbound traffic workloads
        let retries = 10; // when an explorer query is queued/POSTed for first time, keep trying until query has completed
        let result = '';
        if (async_href != '') {

            while(retries > 0) {
                result = await waitForTrafficJobToComplete(async_href, context);
                context.log(`Result from waitForTrafficToComplete is ${result}`);
                if (result == 'completed') {
                    // download traffic results as json                                                                            
                    traffic_results = await downloadTrafficQueryResults(async_href, context);
                    //context.log(`Results of traffic query are ${JSON.stringify(workloads)}`);
                    break
                }
                else {
                    retries -= 1;
                    await sleep(10*1000); // wait before issuing another query
                }
                if (retries === 0) {
                    context.log('Retries exhausted, traffic query did not complete.');
                }                
            }
        }
        return { 
            body: JSON.stringify({
              async_href: async_href, 
              traffic_results: traffic_results,
              port: port,
              protocol: protocol,
              result: result,
              skipPCEUpdate: skipPCEUpdate
            })
        };
    }
});

async function runTrafficQuery(port, protocol, context) {
    context.log(`Inside runTrafficQuery method, port is ${port}, protocol is ${protocol}`);

    let currentDate = new Date();
    let end_date = currentDate.toISOString();

    let oneWeekAgo = new Date(currentDate.getTime() - 7 * 24 * 60 * 60 * 1000);
    let start_date = oneWeekAgo.toISOString();

    context.log(`start date is ${start_date}; end date is ${end_date}`);

    return new Promise((resolve, reject) => {
        let path = `/api/v2/orgs/${ORG_ID}/traffic_flows/async_queries`

        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Authorization", 'Basic ' + Buffer.from(`${API_KEY}:${API_SECRET}`).toString('base64'));

        var raw = JSON.stringify({
            "sources": {
              "include": [
                []
              ],
              "exclude": []
            },
            "destinations": {
              "include": [
                []
              ],
              "exclude": []
            },
            "services": {
              "include": [{"proto":protocol,"port":port}],
              "exclude": []
            },
            "sources_destinations_query_op": "and",
            "start_date": start_date,
            "end_date": end_date,
            "policy_decisions": [
              "potentially_blocked",
              "unknown"
            ],
            "boundary_decisions": [],
            "query_name": "MAP_QUERY_Time: Last week potentially blocked and unknown traffic",
            "exclude_workloads_from_ip_list_query": true,
            "aggregate_flows_across_days": true,
            "max_results": 100000
        });

        var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
        };

        fetch(`https://${PCE_FQDN}:${PORT}${path}`, requestOptions)
        .then(response => response.text())
        .then(result => {
            let responseJson = JSON.parse(result);
            context.log(`Response from runTrafficQuery is ${JSON.stringify(responseJson)}`);
            let href = responseJson['href'];
            context.log(`[DEBUG] Href from runTrafficQuery is ${href}`);
            if (href.includes('/')) {
                href = href.split('/').pop();
                resolve(href)
            }
        })
        .catch(error => {
            context.log('error', error)
            reject(error)

        });
    })
}

async function waitForTrafficJobToComplete(async_href, context) {
    context.log(`Inside waitForTrafficJobToComplete method`);
    return new Promise((resolve, reject) => {
        let path = `/api/v2/orgs/${ORG_ID}/traffic_flows/async_queries/${async_href}`

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
            context.log(`Response from waitForTrafficJobToComplete is ${JSON.stringify(responseJson)}`);
            let status = responseJson['status'];
            resolve(status)
        })
        .catch(error => {
            context.log('error', error)
            reject(error)
        });
    })
}

async function downloadTrafficQueryResults(async_href, context) {
    context.log(`Inside downloadTrafficQueryResults method`);
    return new Promise((resolve, reject) => {
        let path = `/api/v2/orgs/${ORG_ID}/traffic_flows/async_queries/${async_href}/download?offset=0&limit=5000`

        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Accept", "application/json"); // else server sends text/csv
        myHeaders.append("Authorization", 'Basic ' + Buffer.from(`${API_KEY}:${API_SECRET}`).toString('base64'));

        var requestOptions = {
            method: 'GET',            
            headers: myHeaders,
            redirect: 'follow'
            };

        fetch(`https://${PCE_FQDN}:${PORT}${path}`, requestOptions)
        .then(response => response.text())
        .then(data => {
            //workloads = getInboundWorkloadNames(result, context)
            // send entire traffic results back to caller
            resolve(JSON.parse(data))
        })
        .catch(error => {
            context.log('error', error)
            reject(error)
        });
    })
}

// Define a sleep function
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}