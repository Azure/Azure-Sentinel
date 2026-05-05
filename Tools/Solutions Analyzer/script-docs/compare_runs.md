# Compare Runs

**Script:** `compare_runs.py`

## Overview

Compares two Solutions Analyzer runs (CSV directories) and reports added/removed entities — with **rename detection** so that a connector whose JSON `id` field changed is not double-counted as one addition + one removal.

Currently compares: `solutions.csv`, `connectors.csv`, `tables.csv`, `parsers.csv`, `asim_parsers.csv`, `content_items.csv`.

Rename detection runs on `connectors.csv` by matching strictly-removed and strictly-added rows that share the same primary `connector_files` path.

## Prerequisites

- Python 3.7 or higher
- No third-party dependencies

## Running the Script

From the `Tools/Solutions Analyzer` directory:

```bash
# Compare two CSV directories, print to stdout
python compare_runs.py --before /path/to/prior-csvs --after .

# Write a markdown report
python compare_runs.py --before /path/to/prior-csvs --after . --out diff.md
```

A common pattern is to materialize the prior run from the
[output branch](https://github.com/Azure/Azure-Sentinel/tree/solution_analyzer_output)
into a temporary folder and compare against the current working copy:

```bash
mkdir prior
git -C ../../../Azure-Sentinel-solution-analyzer-output \
    archive HEAD "Tools/Solutions Analyzer/" | tar -xf - -C prior --strip-components=2
python compare_runs.py --before prior --after . --out diff.md
```

## Output

The markdown report contains:

| Section | Content |
|---|---|
| Summary table | Per-CSV add/remove/rename counts |
| `### Renamed (N)` | Pairs of `(prior_id, new_id)` sharing a primary file path |
| `### Added (N)` | Rows with new identifiers; for connectors, includes the file path so the user can spot when the new entry corresponds to a moved/refactored file |
| `### Removed (N)` | Rows whose identifier disappeared without a same-path replacement |

Files missing on either side are skipped silently — useful when comparing
against a snapshot that contains only a subset of the CSVs.
