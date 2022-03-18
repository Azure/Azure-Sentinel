const synackService = require("./synack-service");
const azureService = require("./azure-service");

exports.runSync = function runSync(context) {

    context.log(`trying to fetch vulnerabilities from Synack`)
    synackService.fetchSynackVulns(context)
        .then((synackVulns) => {

            context.log(`fetched total ${synackVulns.length} vulnerabilities from Synack`)
            azureService.getAzureAuthenticationToken(context)
                .then((accessToken) => {
                    context.log('got azure access token for synchronization')

                    for (let i = 0; i < synackVulns.length; i++) {
                        let vulnJson = synackVulns[i]
                        let title = vulnJson.title
                        let incidentDescription = compileIncidentDescription(vulnJson)
                        let incidentStatus = getIncidentStatus(vulnJson['vulnerability_status'])
                        let severity = getSentinelSeverity(vulnJson);

                        let incidentDto = {
                            title: title,
                            severity: severity,
                            description: incidentDescription,
                            status: incidentStatus
                        }

                        azureService.createOrUpdateIncident(context, vulnJson, incidentDto, accessToken)
                            .then((incidentOperationResult) => {
                                context.log(`${incidentOperationResult.status} incident ${incidentOperationResult.name}`)
                                let incidentId = incidentOperationResult.name

                                synackService.fetchComments(context, vulnJson['id'])
                                    .then((synackCommentsJsonArray) => {
                                        azureService.fetchComments(context, incidentId, accessToken)
                                            .then((incidentCommentsJsonArray) => {
                                                let incidentCommentsIds = []
                                                for (let incidentComment of incidentCommentsJsonArray) {
                                                    incidentCommentsIds.push(incidentComment['name'])
                                                }
                                                for (let synackComment of synackCommentsJsonArray) {
                                                    let sentinelCommentId = `${incidentId}_${synackComment.id}`
                                                    if (!incidentCommentsIds.includes(sentinelCommentId)) {
                                                        let synackAuthorName = synackComment['User']['name']
                                                        let sentinelCommentBody = `**${synackAuthorName}** **(Synack):** ${synackComment.body}`
                                                        azureService.createComment(context, incidentId, sentinelCommentId, sentinelCommentBody, accessToken)
                                                            .then((commentOperationResult) => {
                                                                context.log(`${commentOperationResult.status} comment ${commentOperationResult.name}`)
                                                            })
                                                            .catch((error) => {
                                                                context.error(`Failed to create comment for incident ${incidentId}`)
                                                                context.error(error)
                                                            })
                                                    } else {
                                                        context.log(`comment ${sentinelCommentId} already exists`)
                                                    }
                                                }
                                            })

                                    })
                            })
                            .catch((error) => {
                                context.error('error occurred while trying to create/update a Sentinel incident')
                                context.error(error)
                            })
                    }
                })
                .catch((error) => {
                    context.error(`error occurred while trying to get Azure authentication token \n ${error}`)
                })
        })
        .catch((error) => {
            context.error(`The synchronization failed. Error occurred while trying to fetch vulnerabilities from Synack: ${error}`)
        })
}

function getIncidentStatus(synackStatusJson) {
    // https://docs.microsoft.com/rest/api/securityinsights/stable/incidents/create-or-update#incidentstatus
    let synackFlowType = synackStatusJson['flow_type']
    let synackStatusName = synackStatusJson['text']
    switch (synackFlowType) {
        case 2:
            let classification = 'Undetermined'
            let classificationReason = null
            if (synackStatusName.toLowerCase() === 'Fixed'.toLowerCase()) {
                classification = 'TruePositive'
                classificationReason = 'SuspiciousActivity'
            } else if (synackStatusName.toLowerCase().includes('not valid')) {
                classification = 'FalsePositive'
                classificationReason = 'InaccurateData'
            }
            return {name: 'Closed', classification: classification, classificationReason: classificationReason}
        case 0:
            return {name: 'New'}
        case 1:
            return {name: 'Active'}
    }
}

function compileIncidentDescription(vulnJson) {

    let description = vulnJson['description']
    let impact = vulnJson['impact']
    let categoryJson = vulnJson['category']
    let category = `${categoryJson['parent']} > ${categoryJson['display']}`
    let recommendedFix = vulnJson['recommended_fix']
    let link = vulnJson['link']
    let cvssScore = vulnJson['cvss_final']
    let cvssVector = vulnJson['cvss_vector']
    let exploitableLocationsArray = vulnJson['exploitable_locations']
    let listingJson = vulnJson['listing']
    let validationStepsJsonArray = vulnJson['validation_steps']
    let updated = vulnJson['updated_at']
    let resolved = vulnJson['resolved_at']
    let closed = vulnJson['closed_at']

    let exploitableLocationsHtml = '<ol>'
    for (let i = 0; i < exploitableLocationsArray.length; i++) {
        let exploitableLocationJson = exploitableLocationsArray[i]
        let keys = Object.keys(exploitableLocationJson)
        exploitableLocationsHtml += `<li>`
        for (let key of keys) {
            let value = exploitableLocationJson[key]
            exploitableLocationsHtml += `${key}:${value} `
        }
        exploitableLocationsHtml += `</li>`
    }
    exploitableLocationsHtml += '</ol>'
    exploitableLocationsHtml = `<h4>Vulnerability Locations</h4>${exploitableLocationsHtml}`

    let listingHtml = `<h4>Assessment</h4>Name: ${listingJson['codename']}<br>Link: ${listingJson['link']}<br>Category: ${listingJson['category']}`
    let cvssHtml = `<h4>CVSS</h4>Score ${cvssScore}<br>Vector ${cvssVector}`
    let linkHtml = `<a href=\"${link}\">${link}</a>`

    let validationStepsHtml = '<h4>Steps to Reproduce</h4>'
    for (let stepNumber = 1; stepNumber <= validationStepsJsonArray.length; stepNumber++) {
        let validationStep = getValidationStep(stepNumber, validationStepsJsonArray);
        let url = validationStep['url'] ? `<br>${validationStep['url']}` : ''
        let ip = validationStep['ip_address'] ? `<br>IP Address: ${validationStep['ip_address']}` : ''
        let port = validationStep['port'] ? `<br>Port: ${validationStep['port']}` : ''
        let portType = validationStep['port_type'] ? `<br>Port Type: ${validationStep['port_type']}` : ''
        let detail = `${validationStep['detail']}`
        validationStepsHtml += `<h5>${stepNumber}</h5>${detail}${url}${ip}${port}${portType}`
    }

    let closedHtmlPart = closed ? `closed&nbsp;&nbsp;&nbsp;&nbsp;${getDateFromIso8601UTC(closed)}` : ''
    let updatedHtmlPart = updated ? `updated ${getDateFromIso8601UTC(updated)}` : ''
    let resolvedHtmlPart = resolved ? `resolved ${getDateFromIso8601UTC(resolved)}` : ''
    let datesHtml = `<h4>Dates</h4>${updatedHtmlPart}<br>${resolvedHtmlPart}<br>${closedHtmlPart}`
    let categoryHtml = `<h4>Category</h4>${category}`
    let descriptionHtml = `<h4>Description</h4>${description}`
    let impactHtml = `<h4>Impact</h4>\n${impact}`
    let recommendedFixHtml = `<h4>Recommended Fix</h4>\n${recommendedFix}`

    let incidentDescription = `<br>${linkHtml}<br>${categoryHtml}${listingHtml}${descriptionHtml}${impactHtml}\n${exploitableLocationsHtml}${validationStepsHtml}${recommendedFixHtml}${cvssHtml}${datesHtml}`
    return incidentDescription
}

function getValidationStep(stepNumber, validationSteps) {
    for (let validationStep of validationSteps) {
        if (validationStep['number'] === stepNumber) {
            return validationStep
        }
    }
}

function getDateFromIso8601UTC(iso8601UTCString) {
    return iso8601UTCString ? iso8601UTCString.split('T')[0].replace(/-+/g, '/') : ''
}

function getSentinelSeverity(vulnJson) {
    let cvssScore = vulnJson['cvss_final']
    let severity = 'Medium'
    if (cvssScore >= 7) {
        severity = 'High'
    } else if (cvssScore >= 4) {
        severity = 'Medium'
    } else if (cvssScore > 0) {
        severity = 'Low'
    } else if (cvssScore === 0){
        severity = 'Informational'
    }
    return severity
}
