# Masking at ingestion time

Masking and obfuscation can be very useful to hide specific content.

In the JSON file in this folder, you can find a Data Collection Rule that contains a *transformationKql* which performs two different kinds of masking. Below we break the query down into the two different kinds.

## Masking last 4 digits of Social Security Number

The first masking is done on a field called *SSN* which is supposed to contain a Social Security Number. The goal is to replace the first 5 numbers in the SSN with Xs, but only when the SSN is valid. If the SSN is invalid, then we should have an *Invalid SSN* message. This is the part of the transformation that does that:

```kusto
source 
| extend parsedSSN = split(SSN,'-') 
| extend SSN = iif(SSN matches regex @'^\\d{3}-\\d{2}-\\d{4}$' 
and not( SSN matches regex @'^(000|666|9)-\\d{2}-\\d{4}$') 
and not( SSN matches regex @'^\\d{3}-00-\\d{4}$') 
and not (SSN matches regex @'^\\d{3}-\\d{2}-0000$' ),strcat('XXX','-', 'XX','-',parsedSSN[2]), 'Invalid SSN') 
```

As you can see, first we use ```split``` to separate the SSN field using ```-``` as a separator and we store it in a temporary field. We then use ```iif``` to do the replacement, only if the field matches a valid SSN. Inside the ```iif```, we use ```matches regex``` to find the pattern of a Social Security Number (including exclusions). If the SSN is valid, we use ```strcat``` to leave the last 4 digits but replace the first 5 digits with Xs. If it's not valid, we replace with *Invalid SSN*. Finally, we remove the intermediary field.

## Removing Personal Identifiable Information

This second masking will completely replace a field that contains an email address. If it's not a valid email address, we leave it as is. Here is the transformation:

```kusto
source
| extend Email = iif(Email matches regex @'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$','PII data removed', Email)
```

This one is easier, because we want to replace the whole field if it matches the regex, if not, we leave the field content as is.

Deploy this DCR (includes both SSN and email maskings):

[![Deploy this DCR to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FTransformations-Library%2FMasking%2FMaskingDCR.json)