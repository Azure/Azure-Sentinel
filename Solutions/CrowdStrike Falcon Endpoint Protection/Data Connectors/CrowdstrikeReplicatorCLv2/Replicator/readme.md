# Timer Trigger Function App for CrowdStrike

The `Replicator` makes it incredibly easy to have your functions executed on a schedule. This function gets executed every minute by default.

## How it works

For `Replicator` to work, suitable schedule is provided in function configuration as a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we use to represent every 5 minutes is `0 */5 * * * *`. This, in plain text, means: "When seconds is equal to 0, minutes is divisible by 5, for any hour, day of the month, month, day of the week, or year".

## Learn more

This function runs every 1 minute and read the SQS Message. For every bucket in the SQS message, a new entry is created in Azure Storage Queue with required path and file details.
