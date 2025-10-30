# TimerTrigger - Python

The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. This sample demonstrates a simple use case of calling your function every 5 minutes.

## How it works

For a `TimerTrigger` to work, you provide a schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)(See the link for full details). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we use to represent every 5 minutes is `0 */5 * * * *`. This, in plain text, means: "When seconds is equal to 0, minutes is divisible by 5, for any hour, day of the month, month, day of the week, or year".

## Learn more

SearchEvents function app is designed to provide customers the ability to extract audit information from one or more of their IdentityNow tenants.

Using IdentityNow's AuditEvents API, we can solve a number of problems. Some examples include:

--> Surface and gain insights into the brute force password attempts IdentityNow has blocked --> Correlate IdentityNow user activity with other system events to identify coordinated attacks --> Evaluate the timing of login attempts from different geographies to identify problems

NOTE: This function app is intended to make it even easier to bring IdentityNow user activity and governance events into Microsoft Sentinel to improve insights from your security incident and event monitoring solution.