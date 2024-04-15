# TimerTrigger - PowerShell

The `TimerTrigger` makes it incredibly easy to have your functions executed on a schedule. This sample demonstrates a simple use case of calling your function every 1 day.

## How it works

For a `TimerTrigger` to work, you provide a schedule in the form of a [cron expression](https://en.wikipedia.org/wiki/Cron#CRON_expression)(See the link for full details). A cron expression is a string with 6 separate expressions which represent a given schedule via patterns. The pattern we used to represent every 1 day is `0 * * */1 * *`. This, in plain text, means: "When seconds is equal to 0, day is divisible by 1, execute it every day of the month".

## Learn more

[Documentation](https://docs.microsoft.com/azure/azure-functions/functions-bindings-timer?tabs=csharp)
