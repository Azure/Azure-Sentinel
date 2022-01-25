const syncService = require('./sync-service')

module.exports = async function (context, timer) {
    let timeStamp = new Date().toISOString();
    context.log(`scheduled synack synchronization is starting in background at ${timeStamp}`)
    await syncService.runSync()
    context.done()
}
