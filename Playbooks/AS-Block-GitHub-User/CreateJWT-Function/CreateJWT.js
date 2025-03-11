const { sign } = require('jsonwebtoken');
const { add, getUnixTime } = require('date-fns');

module.exports = async function (context, req) {
    context.log(`Http function processed request for url "${req.url}"`);

    // Get private key from request body
    const privateKey = req.body.private_key;
    // Get GitHub App ID from request body
    const appId = req.body.app_id;

    if (privateKey && appId) {
        // Create payload
        const now = new Date();
        const payload = {
            // Issued at time
            iat: getUnixTime(now),
            // JWT expiration time (5 minutes from now)
            exp: getUnixTime(add(now, { minutes: 5 })),
            // GitHub App ID
            iss: appId
        };

        // Sign the JWT
        const token = sign(payload, privateKey, { algorithm: 'RS256' });
        // Success response body
        context.res = {
            // Status defaults to 200
            body: token
        };
    }
    else {
        // Failure response body
        context.res = {
            status: 400,
            body: "Missing private key and/or GitHub App ID."
        };
    }
};
