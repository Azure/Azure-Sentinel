# Intel 471 solution — release checklist

Internal notes for cutting a new version of this solution. Each item exists because it has
bitten us at least once.

## 1. Before repackaging

- [ ] **Bump the `User-Agent` in both playbooks.** The packaging tool copies the header literal
      from `azuredeploy.json` verbatim — nothing injects the solution version — so a stale value
      ships silently. Both playbooks must carry
      `Intel471-SentinelMalwareIntelligence/<version>` and
      `Intel471-SentinelMalwareIntelligenceGraph/<version>`, matching the solution version.
- [ ] **Bump `hidden-SentinelTemplateVersion`** on the `Microsoft.Logic/workflows` resource of
      every playbook whose content changed. The packaging tool reads the playbook template
      version from this tag and defaults to `1.0` when it is missing. If the tag does not move,
      the content hub cannot tell that the playbook template changed, existing installations
      never receive the update, and customers have to uninstall the solution first.
- [ ] **Add a `ReleaseNotes.md` entry.** Mandatory for marketplace certification. State the new
      playbook template versions alongside the solution version, in customer-facing language.
- [ ] **Validate every hunting query YAML before packaging.** The packaging tool stops at the
      first unparseable file and still writes a package, silently, so a single bad file ships a
      solution with only the queries that preceded it alphabetically:

      ```bash
      pwsh -NoProfile -Command 'foreach ($f in Get-ChildItem "Solutions/Intel471/Hunting Queries/*.yaml") {
        try { $null = ConvertFrom-Yaml (Get-Content -Raw $f.FullName) -ErrorAction Stop }
        catch { Write-Host "INVALID:" $f.Name } }'
      ```

      The usual cause is indentation inside the `query: |` block: a line at column 0 ends the
      block scalar, and everything after it is parsed as top-level YAML. Any continuation line
      must stay indented, even when editing only the KQL.
- [ ] **Hunting query IDs must be globally unique.** Content hub keys hunting queries on their
      `id`, so a GUID reused from another solution collides for any customer with both
      installed. Never copy a query from another solution without reissuing its GUID.

## 2. Repackage with the V3 tool

```bash
pwsh Tools/Create-Azure-Sentinel-Solution/V3/createSolutionV3.ps1 \
  -SolutionDataFolderPath <repo>/Solutions/Intel471/Data \
  -VersionMode local -VersionBump patch
```

- `-VersionMode local` **always increments** the version in `Data/Solution_Intel471.json` and
  writes the result back. To land on a specific version, seed the data file with the *previous*
  one. `-VersionMode catalog` derives the version from the published catalog entry instead, which
  is wrong whenever the catalog is behind (see section 5).
- The package filename must equal the version, e.g. `3.0.1` → `Package/3.0.1.zip`.
- The version must match across Partner Center, `Data/Solution_Intel471.json` and
  `Package/mainTemplate.json`.
- Delete the zip of any version that was built but never published, so the folder does not
  advertise a version that does not exist.
- **Re-apply the `learn.microsoft.com` hunting URI in `Package/createUiDefinition.json` after
  every packaging run.** The tool hardcodes `https://docs.microsoft.com/azure/sentinel/hunting`
  (`Tools/Create-Azure-Sentinel-Solution/common/commonFunctions.ps1`), so regeneration reverts the
  fix each time. After patching the file, rebuild the zip so the two agree:
  `zip -X -j <version>.zip createUiDefinition.json mainTemplate.json`.

## 3. Validate

```bash
# the zip must match the loose files it was built from
python3 -c "import zipfile,hashlib,io;z=zipfile.ZipFile('Package/<version>.zip');[print(n, hashlib.sha256(z.read(n)).hexdigest()==hashlib.sha256(io.open('Package/'+n,'rb').read()).hexdigest()) for n in z.namelist()]"

# the content counts must match what the solution actually ships
python3 -c "import json;from collections import Counter;d=json.load(open('Package/mainTemplate.json'));print(Counter(r['properties'].get('contentKind') for r in d['resources']))"

# UA and solution version must agree
grep -rho '"User-Agent": "[^"]*"' Playbooks/*/azuredeploy.json Package/mainTemplate.json | sort -u
grep -o '"_solutionVersion": "[^"]*"' Package/mainTemplate.json
```

- **arm-ttk:** one known failure, `IDs Should Be Derived From ResourceIDs`, is expected. It is a
  false positive on the `contentProductId` / `id` properties that the V3 tool generates for every
  Sentinel solution, and the already-certified packages fail it identically. Any *other* failure
  is real.
- The zip submitted for certification must match the repository contents exactly, so merge the
  PR before publishing the offer.

## 4. Partner Center

- [ ] Plan → Technical configuration: version and package filename both set to the new version.
- [ ] Offer listing → **Search keywords must include the Sentinel GUID**
      `f1de974b-f438-4719-b423-8bf704ba2aef`. Without it the solution does not appear in
      Microsoft Sentinel at all, and only three keywords are allowed — do not let it be pushed out.
- [ ] Plan → Availability: `Hide plan` unchecked; offer not hidden; Azure regions set to Azure Global.
- [ ] Offer listing → Description: this text is what the content hub shows. Keep it naming the
      Verity 471 backend, listing the content counts, and linking `ReleaseNotes.md`.

## 5. After publishing

Microsoft's documented window for a published offer to reach the Sentinel content hub is
**3–5 days**. Verify it actually arrived rather than assuming — a Live offer in Partner Center
does not prove the catalog was refreshed:

```bash
az rest --method get --url "https://management.azure.com/subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.OperationalInsights/workspaces/<WS>/providers/Microsoft.SecurityInsights/contentProductPackages?api-version=2023-04-01-preview" \
  --query "value[?contains(properties.displayName,'Intel')].{name:properties.displayName,version:properties.version}"
```

Check in a workspace where the solution is **not installed**, so the number reflects the catalog
rather than a local installation. If the version is still the old one past the window, escalate to
the Microsoft Sentinel Solutions Onboarding Team (`AzureSentinelPartner@microsoft.com`) and open a
Partner Center support ticket, quoting the offer ID, plan ID, publish timestamp and the SHA-256 of
the published package.

## References

- [Guide to building Microsoft Sentinel solutions](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions#guide-to-building-microsoft-sentinel-solutions)
- [Publish SIEM solutions to Microsoft Sentinel](https://learn.microsoft.com/azure/sentinel/publish-sentinel-solutions)
- [Microsoft Sentinel solution lifecycle in Partner Center](https://learn.microsoft.com/azure/sentinel/sentinel-solutions-post-publish-tracking)
- [Release notes guidance](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/ReleaseNotesGuidance.md)
