/**
 * Solution Automation Input File Interface
 * -----------------------------------------------------
 * The purpose of this interface is to provide detail on
 *  the various fields the input file can have.
 */
interface SolutionAutomationInput {
  Name: string;                //Solution Name      - Ex. "Symantec Endpoint Protection"
  Author: string;              //Author of Solution - Ex. "Eli Forbes - v-eliforbes@microsoft.com"
  Logo: string;                //Link to the Logo used in the CreateUiDefinition.json
  Description: string;         //Solution Description used in the CreateUiDefinition.json
  WorkbookDescription: string|string[]; //Workbook description(s) from ASI-Portal Workbooks Metadata
  Version: string;             //Package version to be created
  //The following fields take arrays of paths relative to the solutions folder.
  //Ex. Workbooks: ["Workbooks/SymantecEndpointProtection.json"]
  Workbooks?: string[];
  "Analytic Rules"?: string[];
  Playbooks?: string[];
  PlaybookDescription?: string|string[]; //Description used in the CreateUiDefinition.json
  Parsers?: string[];
  SavedSearches?: string[];
  "Hunting Queries"?: string[];
  "Data Connectors"?: string[];
  Watchlists?: string[];
  WatchlistDescription?: string|string[]; //Description used in the CreateUiDefinition.json
  BasePath?: string; //Optional base path to use. Either Internet URL or File Path. Default = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/""
  Metadata: string; //Path to the SolutionMetadata File
}
