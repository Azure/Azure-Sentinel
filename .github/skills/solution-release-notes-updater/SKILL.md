---
name: solution-release-notes-updater
description: Update a Microsoft Sentinel solution's ReleaseNotes.md for an approved release. Use when asked to add, revise, or validate a solution release-notes entry without packaging the solution.
---

# Update Solution Release Notes

Update only `Solutions/<SolutionName>/ReleaseNotes.md` for the approved solution release. Follow `.github/instructions/releasenotes.instructions.md` as the source of truth for file path, table format, ordering, and dates. Read `.github/instructions/packaging.instructions.md` when the request overlaps packaging or version bumping; do not treat this skill as permission to package.

## Inputs

Identify the exact solution folder and establish:

- The actual changes being released, from the user's description and, when useful, the solution's diff against the intended target branch.
- The approved **solution-level** release version and whether an approved packaging/version-bump step has already selected or applied it.
- The release date to record.

Ask the user for any missing or ambiguous solution name, change summary, release version/bump, or date before editing. Never invent a feature, date, release, or version. Do not assume the current date is the release date.

## Workflow

1. Read the applicable release-notes and packaging instructions. Inspect the exact solution's `ReleaseNotes.md`, if present, and its `Data/Solution_*.json` version. If a package was already generated for this release, also inspect `Package/mainTemplate.json` → `variables._solutionVersion`. Treat an existing approved package version as authoritative for that release; do not bump it again.
2. Distinguish the solution's release version from versions on individual analytic rules, workbooks, parsers, or XDR detections. A content item's version is not the solution release version. Do not edit solution metadata or package files as part of a notes-only request.
3. Check both staged and unstaged changes to the release-notes file. If the approved version already has an uncommitted row for this same release, update that row rather than adding a duplicate. If the version already exists in committed history, do not duplicate or rewrite it; stop and clarify whether the user intended a correction to that historical entry. If a different uncommitted top entry appears to represent another release, preserve it and ask before deciding where or how to record this release.
4. For a new release, require an explicitly approved solution-level version. Confirm it is valid `X.Y.Z` and newer than the current release entry. Apply the approved patch/minor/major increment only if it has not already been applied; never independently increment a version already advanced by packaging. If the version conflicts with the solution data or generated package, stop and report the mismatch instead of reconciling it silently.
5. Write one concise, truthful entry (normally 1–2 sentences) that names the affected solution content and describes the actual change. Follow the existing table's row style. For a new file, use exactly this header and a Markdown separator:

   ```markdown
   | **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
   |---|---|---|
   ```

   Insert a new release immediately below the header/separator, keeping all existing history intact. Use the confirmed release date in `DD-MM-YYYY` format. Do not add empty rows or fabricate intermediate releases to fill apparent gaps in historical version numbers.
6. Validate the resulting table against the release-notes instructions:
   - Exact header names and order; exactly three columns in the header, separator, and every data row.
   - Each version is three-part semantic `X.Y.Z`, unique, and in descending numeric order.
   - Each date is a real date formatted `DD-MM-YYYY`.
   - Each change-history cell is nonempty and accurately reflects the approved changes.
7. Keep the edit focused. If pre-existing historical rows violate a rule, do not silently rewrite history; report the existing issue separately. Do not change any solution content, `Data/`, `Package/`, shared instructions, skills, or tooling while performing this notes-only task.

## Boundaries and result

- This workflow edits only the requested solution's `ReleaseNotes.md`.
- Do not run the V3/V3.1/V4 packaging or build-and-validate flow merely to edit notes; those flows can change versions and generated package files. If the user asks to package or validate, switch to the repository's applicable packaging workflow and obtain the required version-bump approval first.
- Do not create a PR, commit, push, deploy, or contact Azure unless separately requested and authorized.
- Report the exact file changed, the version/date and entry added or revised, validation results, and any unresolved ambiguity or pre-existing table violations. If no safe entry can be made, leave the file untouched and explain what information is needed.
