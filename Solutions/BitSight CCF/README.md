# BitSight Full CCF ARM package

This package provides the BitSight CCF data connector with the full integration scope of the deprecated Function-based connector.

## Files

- `bitsight-full-connection-template.json` — Template 1. Creates custom tables, a DCR, an optional DCE, and multiple `RestApiPoller` connections.
- `bitsight-full-connector-definition.json` — Template 2. Creates the BitSight `Customizable` connector definition in Microsoft Sentinel.
- `*.parameters.json` — starter parameter files.
- `README.md` — deployment notes and assumptions.

## Important assumptions

1. The uploaded deprecated ARM template exposed the **tables, DCR streams, transforms, schedules, and settings**, but **not** the exact BitSight REST URLs used by the Function runtime because the runtime logic lived in the external package referenced by `WEBSITE_RUN_FROM_PACKAGE`.
2. Because of that, this package keeps the **data model and transforms** close to the deprecated connector, but leaves the **connection rules parameterized**.
3. The starter parameter file intentionally contains **placeholder BitSight endpoints** such as `https://api.bitsighttech.com/<replace>/alerts`. Replace those with the exact tenant-tested URLs before production use.
4. The default paging configuration is a conservative scaffold:
   - most connection defaults use `Offset`
   - observation statistics defaults use `None`
   Review and adjust these to the exact BitSight endpoint behavior.

## Scope covered

The package creates resources for these BitSight datasets:

- BitsightPortfolio_Companies_CL
- BitsightCompany_details_CL
- BitsightCompany_rating_details_CL
- BitsightAlerts_data_CL
- BitsightGraph_data_CL
- BitsightDiligence_historical_statistics_CL
- BitsightDiligence_statistics_CL
- BitsightIndustrial_statistics_CL
- BitsightObservation_statistics_CL
- BitsightFindings_data_CL
- BitsightFindings_summary_CL
- BitsightBreaches_data_CL

## Deployment flow

1. Publish **Template 1** as a Template Spec.
2. Update the Template 1 parameter file with:
   - workspace name
   - region
   - exact BitSight endpoint URLs
   - exact response paths and paging settings as needed
3. Deploy **Template 2** with:
   - workspace name
   - template spec name
   - template spec version
4. Open the BitSight connector in Microsoft Sentinel and provide the BitSight API token.

## Notes

- The template uses the current stable Microsoft Sentinel ARM API version `2025-09-01` for `Microsoft.SecurityInsights/dataConnectors` and `Microsoft.SecurityInsights/dataConnectorDefinitions`.
- The template keeps one intentional schema cleanup from the pilot: `BitsightAlerts_data.guid` is normalized to `string`.
- If you later confirm the exact BitSight endpoint-by-endpoint request model, you can harden the parameter file or inline the connection settings into the template.
