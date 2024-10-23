// constants.js
const PCE_FQDN = process.env.PCE_FQDN;
const PORT = process.env.PORT;
const ORG_ID = process.env.ORG_ID;
const API_KEY = process.env.API_KEY;
const API_SECRET = process.env.API_SECRET;
const MAX_WORKLOADS = process.env.MAX_WORKLOADS || 100;  // Default to 100 if undefined

module.exports = {
    PCE_FQDN,
    ORG_ID,
    PORT,
    API_KEY,
    API_SECRET,
    MAX_WORKLOADS
};
