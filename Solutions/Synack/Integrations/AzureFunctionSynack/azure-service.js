const https = require('https')

const SUBSCRIPTION_ID = process.env.AZURE_SUBSCRIPTION_ID
const RESOURCE_GROUP_NAME = process.env.AZURE_RESOURCE_GROUP_NAME
const WORKSPACE_ID = process.env.AZURE_WORKSPACE_ID
const CLIENT_ID = process.env.AZURE_CLIENT_ID
const CLIENT_SECRET = process.env.AZURE_CLIENT_SECRET
const TENANT_ID = process.env.AZURE_TENANT_ID
const MAX_DESCRIPTION_LENGTH = 5000

exports.getAzureAuthenticationToken = function getAzureAuthenticationToken(context) {

    let secretForLog = CLIENT_SECRET == null ? '' : CLIENT_SECRET.replace(/./g, '*')
    context.log(`trying to get access token for: \n >>Subscription ID: ${SUBSCRIPTION_ID}\n >>Resource Group: ${RESOURCE_GROUP_NAME}\n >>Application (client) ID: ${CLIENT_ID}\n >>Client Secret\: ${secretForLog}\n`)
    return new Promise(((resolve, reject) => {

        let requestBody = `grant_type=client_credentials&client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}&resource=https://management.azure.com/`
        let options = {
            hostname: 'login.microsoftonline.com',
            path: `/${TENANT_ID}/oauth2/token`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': requestBody.length
            },
        }

        let request = https.request(options, function (response) {
                let responseContent = ''
                response.on('data', function (chunk) {
                    responseContent += chunk
                })
                response.on('error', function (error) {
                    context.log.error(`ERROR: ${error}`)
                    reject(error)
                })
                response.on('end', function () {
                    let responseJson = JSON.parse(responseContent)
                    if (response.statusCode === 200) {
                        resolve(responseJson.access_token)
                    } else {
                        reject(responseContent)
                    }
                })
            }
        )
        request.write(requestBody)
        request.end()
    }))

}

exports.createOrUpdateIncident = function createOrUpdateIncident(vulnJson, accessToken, incidentDto, context) {

    return new Promise((resolve, reject) => {
        let vulnId = vulnJson.id
        let path = `/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP_NAME}/providers/Microsoft.OperationalInsights/workspaces/${WORKSPACE_ID}/providers/Microsoft.SecurityInsights/incidents/${vulnId}?api-version=2021-04-01`
        let options = {
            hostname: 'management.azure.com',
            path: path,
            method: 'PUT',
            headers: {
                'Authorization': 'Bearer ' + accessToken,
                'Content-Type': 'application/json'
            },
        }

        let description = incidentDto.description !== null && incidentDto.description.length >= MAX_DESCRIPTION_LENGTH ?
            incidentDto.description.substring(0, MAX_DESCRIPTION_LENGTH - 16) + " ...(truncated)" : incidentDto.description
        let requestBody = JSON.stringify(
            {
                "properties": {
                    "severity": incidentDto.severity,
                    "description": description,
                    "status": incidentDto.status.name,
                    "classification": incidentDto.status.classification,
                    "classificationReason": incidentDto.status.classificationReason,
                    "title": incidentDto.title
                }
            }
        )
        let request = https.request(options, function (response) {
            let responseContent = ''
            response.on('data', function (chunk) {
                responseContent += chunk
            })
            response.on('error', function (error) {
                context.log.error(`ERROR: ${error}`)
                reject(error)
            })
            response.on('end', function () {
                let statusCode = response.statusCode
                if (statusCode === 200 || statusCode === 201) {
                    let responseJson = JSON.parse(responseContent)
                    let status = statusCode === 201 ? 'created' : 'updated'
                    resolve({status: status, name: responseJson.name})
                } else {
                    reject(responseContent)
                }
            })
        })
        request.write(requestBody)
        request.end()
    })
}

exports.createComment = function createComment(context, incidentId, commentId, commentBody, accessToken) {

    return new Promise(((resolve, reject) => {

        let path = `/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP_NAME}/providers/Microsoft.OperationalInsights/workspaces/${WORKSPACE_ID}/providers/Microsoft.SecurityInsights/incidents/${incidentId}/comments/${commentId}?api-version=2021-04-01`
        let options = {
            hostname: 'management.azure.com',
            path: path,
            method: 'PUT',
            headers: {
                'Authorization': 'Bearer ' + accessToken,
                'Content-Type': 'application/json'
            },
        }

        let requestBody = JSON.stringify(
            {
                "properties": {
                    "message": commentBody,
                }
            }
        )

        let request = https.request(options, function (response) {
            let responseContent = ''
            response.on('data', function (chunk) {
                responseContent += chunk
            })
            response.on('error', function (error) {
                context.log.error(`ERROR: ${error}`)
                reject(error)
            })
            response.on('end', function () {
                let statusCode = response.statusCode
                if (statusCode === 201 || statusCode === 200) {
                    let responseJson = JSON.parse(responseContent)
                    let status = statusCode === 201 ? 'created' : 'updated'
                    resolve({status: status, name: responseJson.name})
                } else {
                    reject(responseContent)
                }
            })
        })
        request.write(requestBody)
        request.end()
    }))
}

exports.fetchComments = function fetchComments(context, incidentId, accessToken) {

    return new Promise(((resolve, reject) => {

        let path = `/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP_NAME}/providers/Microsoft.OperationalInsights/workspaces/${WORKSPACE_ID}/providers/Microsoft.SecurityInsights/incidents/${incidentId}/comments?api-version=2021-04-01`
        let options = {
            hostname: 'management.azure.com',
            path: path,
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + accessToken,
                'Content-Type': 'application/json'
            },
        }

        let request = https.request(options, function (response) {
            let responseContent = ''
            response.on('data', function (chunk) {
                responseContent += chunk
            })
            response.on('error', function (error) {
                context.log.error(`ERROR: ${error}`)
                reject(error)
            })
            response.on('end', function () {
                let statusCode = response.statusCode
                if (statusCode === 200) {
                    let responseJson = JSON.parse(responseContent)
                    resolve(responseJson['value'])
                } else {
                    reject(responseContent)
                }
            })
        })
        request.end()
    }))
}
