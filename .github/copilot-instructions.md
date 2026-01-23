# Copilot Instructions for Azure-Sentinel Repository

## Documentation Generator (Solutions Analyzer)

When working with the documentation generator in `Tools/Solutions Analyzer/generate_connector_docs.py`:

### Regenerating Documentation

When regenerating documentation, always:

1. **Delete previous generated docs first** to ensure clean output before regenerating
2. **Output location:** `C:\Users\ofshezaf\GitHub\sentinelninja\Solutions Docs`
3. **Use the `--output-dir` flag** to specify the output directory explicitly

This output directory is in a separate repository from Azure-Sentinel where the generated markdown documentation is stored.

### Running the Documentation Generator

The generator has two steps:

1. **Generate CSVs first** (from Azure-Sentinel repo):
   ```bash
   cd Tools/Solutions\ Analyzer
   python map_solutions_connectors_tables.py
   ```

2. **Generate documentation** (output to sentinelninja repo):
   ```bash
   python generate_connector_docs.py --output-dir "C:\Users\ofshezaf\GitHub\sentinelninja\Solutions Docs"
   ```

**IMPORTANT:** Never run `generate_connector_docs.py` without the `--output-dir` flag, as it will generate docs in the Azure-Sentinel repo which should NOT contain generated content. The default output is `connector-docs/` which is only a placeholder README in this repo.

### Performance Notes

- The CSVs generation (`map_solutions_connectors_tables.py`) processes all solution files locally - no network access
- The docs generation (`generate_connector_docs.py`) also runs locally - no network access
- Both scripts should complete in under 2 minutes on a typical machine
