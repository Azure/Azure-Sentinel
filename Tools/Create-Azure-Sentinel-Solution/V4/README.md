# Create Solution V4

`createSolutionV4.ps1` supports both local and GitHub pipeline invocation. It
is placed beside V3 to make the supported packaging generations explicit:

- `V3\createSolutionV3.ps1` remains the legacy Sentinel-only local entry point.
- `V4\createSolutionV4.ps1` adds XDR Detection packaging, supports local use,
  and remains the CI entry point.

Both entry points use `common\commonFunctions.ps1` for the core packaging
implementation. Only V4 enables Defender XDR Custom Detection injection.

They are alternative entry points, not two required packaging steps. Use V3
for a legacy Sentinel-only package and V4 when the solution contains XDR
Detections. The repository pipeline runs V4 for PR/CI packaging.

## Local usage

```powershell
.\Tools\Create-Azure-Sentinel-Solution\V4\createSolutionV4.ps1 `
  -SolutionDataFolderPath ".\Solutions\<solution>\Data" `
  -VersionMode local `
  -VersionBump none
```

The local parameter set calls `common\createSolutionLocal.ps1` directly. V3
uses the same common implementation through its own adapter; neither entry
point invokes the other.

Use `none` for repeat validation without changing source versions. Use
`patch`, `minor`, or `major` when preparing a release; those options persist
the new version into the solution data file and `SolutionMetadata.json`.

## Pipeline usage

In CI, V4 receives pipeline-calculated metadata and version parameters. The
package automation calls it through:

```text
.script\package-automation\package-generator.ps1
```
