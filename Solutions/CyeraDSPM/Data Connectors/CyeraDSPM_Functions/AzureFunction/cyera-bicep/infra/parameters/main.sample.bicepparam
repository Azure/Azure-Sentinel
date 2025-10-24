// sample params for RG-scoped deployment
using 'main.bicep'

param location = 'westus2'
param workspaceResourceId = '/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace>'
param dceName = 'cyera-dce'
param dcrName = 'cyera-dcr'
param functionAppName = 'func-cyera-connector-<suffix>'
param cyeraClientId = '<entra-app-client-id>'
param cyeraSecret = '<entra-app-client-secret>'

/* Optional: if you host the function zip with SAS or public URL, set it here
param functionPackageUrl = 'https://<account>.blob.core.windows.net/<container>/cyera-connector.zip?<sas>'
*/
