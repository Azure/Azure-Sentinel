![logo](https://raw.githubusercontent.com/SecureHats/SecureHacks/main/media/sh-banners.png)
=========
[![Maintenance](https://img.shields.io/maintenance/yes/2022.svg?style=flat-square)]()
# Microsoft Sentinel - Analytics Rules Validator

This GitHub action can be used to validate Microsoft Sentinel Analytics rules in both JSON and YML format.
>Add the following code block to your Github workflow:

```yaml
name: Analytics
on: push

jobs:
  pester-test:
    name: validate detections
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository code
        uses: actions/checkout@v3
      - name: Validate Sentinel Analytics Rules
        uses: SecureHats/validate-detections@v1.3.0
        with:
          filesPath: templates
          logLevel: Minimal
```

### Inputs

This Action defines the following formal inputs.

| Name | Req | Description
|-|-|-|
| **`filesPath`**  | false | Path to the directory that contain the files to be tested, relative to the root of the project. This path is optional and defaults to the project root, in which case all files across the entire project tree will be discovered.
| **`logLevel`** | false | This indicates the verbosity of the testing engine. The default is set to `Normal` which shows all the passed and failed tests in the output. Optional values are `None, Minimal, Normal, Detailed, Diagnostic` When using `Minimal` only non-passed test results will be shown. The available verbosity options are based on the [pester](https://pester-docs.netlify.app/docs/commands/Invoke-Pester#-show) documentation. 

## Current incuded tests

![image](https://user-images.githubusercontent.com/40334679/170026369-fa0fa7b8-e580-42d4-9c2d-c36edb506094.png)

## Current limitations / Under Development

- No support for Hunting Queries
- No support for Fusion rules
