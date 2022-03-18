const syncService = require('./sync-service')

module.exports = async function (context, timer) {
    let timeStamp = new Date().toISOString();
    context.log(`scheduled synack synchronization is starting in the background at ${timeStamp}`)
    await syncService.runSync(context)
    context.done()
}
