---
applyTo: "Parsers/ASim*/CHANGELOG/*.md"
---

# ASIM Changelog Review Instructions

## Overview

Use these instructions when reviewing changelog files under `Parsers/ASim*/CHANGELOG/`. Each changelog records the version history of one ASIM parser. Validate the changelog against the corresponding parser YAML and the pull request changes.

Review only issues introduced or exposed by the current change. Do not report unrelated historical formatting or ordering issues unless the pull request modifies the affected entry or relies on it for a new entry.

## Corresponding Parser

1. Derive the expected parser filename from the changelog filename:
   - `CHANGELOG/ASimAuthenticationAADManagedIdentity.md` corresponds to `ASimAuthenticationAADManagedIdentity.yaml`.
   - `CHANGELOG/vimAuthenticationAADManagedIdentity.md` corresponds to `vimAuthenticationAADManagedIdentity.yaml`.
2. Locate the corresponding YAML in the schema's `Parsers/` directory.
3. Flag a new changelog that has no corresponding parser YAML.
4. When a parser version changes, verify that its corresponding changelog is updated in the same pull request.
5. Parameterless, parameterized, unifying, and ingestion-time parsers must each use their own changelog. Do not use one parser's changelog as a substitute for another parser's history.

## Required Document Structure

The changelog must use this structure:

```markdown
# Changelog for <ParserFileName>.yaml

## Version <version>

- (<YYYY-MM-DD>) <change summary> - [PR #<number>](https://github.com/Azure/Azure-Sentinel/pull/<number>)
- <optional implementation detail>
```

Validate all of the following:

- The document starts with exactly one level-one heading.
- The heading uses `# Changelog for <ParserFileName>.yaml`.
- `<ParserFileName>.yaml` exactly matches the corresponding parser filename, including casing.
- Every release section uses a level-two `## Version <version>` heading.
- Each version section contains at least one non-empty bullet.
- Flag empty bullets, placeholder text, and empty version sections.
- Keep one blank line between headings and their content and between version sections.

## Version Validation

- The newest version section must match the corresponding YAML's `Parser.Version` value exactly.
- A newly added version must be greater than the previous highest version.
- Do not add a duplicate version heading.
- List version sections in descending numeric version order, newest first.
- Compare version components numerically rather than lexicographically; for example, `0.2.10` is newer than `0.2.9`.
- Preserve valid historical version formats. Require new versions to follow the version format used by the corresponding parser metadata.
- If both parameterless and parameterized parser versions change, validate each YAML against its own changelog independently.

## Entry Validation

The first bullet for a new version must include:

1. A date in `(YYYY-MM-DD)` format.
2. A concise summary of the parser change.
3. A Markdown link to the Azure-Sentinel pull request.

Validate all of the following:

- The date is a real calendar date and uses four-digit year, two-digit month, and two-digit day values.
- The date accurately represents the pull request change and is not later than the current date.
- New entries are chronologically consistent with the surrounding version history.
- The summary describes the parser change rather than unrelated repository work.
- The summary is consistent with the parser diff and does not claim unsupported behavior.
- Significant mapping, enumeration, filtering, schema, or source-table changes are described clearly. Add detail bullets when the summary alone is insufficient.
- Detail bullets are concise, non-empty, and belong to the version section in which they appear.
- Do not duplicate the same change entry within a changelog.

## Pull Request Link Validation

Use this link format:

```markdown
[PR #<number>](https://github.com/Azure/Azure-Sentinel/pull/<number>)
```

Validate all of the following:

- The link targets `Azure/Azure-Sentinel`.
- The displayed pull request number and URL number are identical.
- The pull request exists and is the pull request associated with the documented change.
- Do not accept issue links, commit links, links to another repository, or bare unlinked pull request numbers for new entries.

## Parser Metadata Consistency

Compare the changelog with the corresponding parser YAML:

- Verify that the latest changelog version equals `Parser.Version`.
- Verify that the parser's `Parser.LastUpdated` was updated appropriately for the documented parser change.
- Verify that the changelog summary and details agree with changes to `ParserQuery`, `ParserParams`, schema metadata, and other parser metadata.
- Flag a parser version bump with no matching changelog entry.
- Flag a changelog version bump with no matching parser version change.

## Review Findings

Report only concrete, actionable findings. Each finding must identify:

- The invalid or inconsistent changelog content.
- The corresponding parser metadata or pull request evidence.
- The exact correction required.

If the changed entries satisfy all requirements, do not invent a finding.
