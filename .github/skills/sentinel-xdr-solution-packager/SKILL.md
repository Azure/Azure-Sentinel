---
name: sentinel-xdr-solution-packager
description: Package a complete Microsoft Sentinel solution with optional Defender XDR Custom Detections by using the shared V3/V4 packaging implementation.
---

# Package a Sentinel and Defender XDR solution

Use this skill after solution content and any `XDR Detections/*.yaml` files are
complete and structurally validated.

Run V4 for any solution that contains `XDR Detections`. V3 remains the legacy
Sentinel-only packager and intentionally ignores XDR Detections. Never run both
merely to create the same package.

The generated package remains a full Microsoft Sentinel solution. When XDR
Detections are declared, it also supports hybrid installation:

- `E5Flavor=false` installs Sentinel Analytic Rules.
- `E5Flavor=true` installs their matched Defender XDR Custom Detections.
- Custom Detections are always packaged disabled.

## Scope

This skill:

- validates the solution-data packaging contract;
- selects and applies one semantic version increment;
- runs the supported local packaging entry point;
- verifies the generated template, parameter file, and ZIP;
- checks AR-to-CD matching and hybrid deployment conditions; and
- reports validation failures without hiding or weakening them.

It does not convert Analytic Rules, create mock data, deploy the generated
template, enable detections, or validate alert parity.

## Inputs

- A solution folder under `Solutions\`.
- The solution data folder, normally `Solutions\<solution>\Data`.
- The version action: `none`, `patch`, `minor`, or `major`.

Use `none` for repeat local validation. Before producing a package intended for
submission, ask which release increment to apply. Never bump the version more
than once for the same package attempt.

## XDR packaging contract

When the solution contains Custom Detections, confirm its solution-data JSON
contains:

```json
{
  "Analytic Rules": [],
  "XDR Detections": [],
  "XDR Detection Version": "1.0.0",
  "Include XDR Content Registration": false
}
```

For every XDR Detection YAML, require:

- `kind: CustomDetection`;
- `resourceType: Microsoft.Security/detectionRules`;
- a supported `apiVersion`;
- a stable `properties.id`;
- `contentProvenance.source.id` matching exactly one packaged Analytic Rule;
- a query, schedule, alert template, and reviewed entity mappings; and
- `properties.status: disabled`.

Do not enable `Include XDR Content Registration` unless the user explicitly
requests it and the live resource provider is known to support registration.

## Workflow

1. Work from the repository root.
2. Confirm PowerShell 7.1 or newer, Node.js, and the `powershell-yaml` module are
   available. Install missing dependencies only after confirming they are
   required.
3. Inspect the solution-data JSON and all referenced files. Stop on missing,
   duplicate, conflicting, or review-required content.
4. Verify every `contentProvenance.source.id` resolves to exactly one Analytic
   Rule content ID.
5. Confirm the current solution version and the requested bump. Check that
   `ReleaseNotes.md`, when present, can be synchronized to the resulting
   version.
6. Run one supported local entry point. V4 usage:

   ```powershell
   pwsh -NoProfile -File `
     ".\Tools\Create-Azure-Sentinel-Solution\V4\createSolutionV4.ps1" `
     -SolutionDataFolderPath ".\Solutions\<solution>\Data" `
     -VersionMode local `
     -VersionBump none
   ```

   Use `none` for validation without modifying source versions. Replace it with
   the approved `patch`, `minor`, or `major` value when producing a release
   package; those options update the solution data and metadata versions.

   V3 remains supported for legacy Sentinel-only solutions. V3 and local V4
   are independent adapters over `common\createSolutionLocal.ps1`; only V4
   enables the XDR injection path in `common\commonFunctions.ps1`. Pipeline V4
   receives its inputs from `.script\package-automation\package-generator.ps1`.

7. Require successful packaging and inspect:

   - `Package\mainTemplate.json`;
   - `Package\createUiDefinition.json`;
   - `Package\testParameters.json`; and
   - `Package\<version>.zip`.

8. For a hybrid package, verify:

   - `E5Flavor` exists and defaults to `false`;
   - every matched AR has condition
     `[not(parameters('E5Flavor'))]`;
   - every CD nested deployment has condition
     `[parameters('E5Flavor')]`;
   - AR, CD deployment, and CD ID counts match;
   - every CD body has `status: disabled`;
   - deployment names and CD IDs are unique and deterministic;
   - Content Hub registration is absent unless explicitly enabled; and
   - the generated ZIP version matches the solution-data version.

9. Run the repository packaging validations. Do not classify skipped tests as
   passed. Separate genuine template failures from documented validator or
   environment limitations.
10. Report the generated version, artifact paths, content counts, validation
    results, and any deployment prerequisites or unresolved failures.

Packaging is complete only when the artifacts exist, versions are synchronized,
all expected resources are present, and no unexplained validation failure
remains.
