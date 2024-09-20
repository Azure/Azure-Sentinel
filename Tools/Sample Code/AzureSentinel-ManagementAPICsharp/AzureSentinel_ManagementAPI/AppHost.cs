using System;
using System.Threading.Tasks;
using AzureSentinel_ManagementAPI.Actions;
using AzureSentinel_ManagementAPI.AlertRules;
using AzureSentinel_ManagementAPI.AlertRuleTemplates;
using AzureSentinel_ManagementAPI.Bookmarks;
using AzureSentinel_ManagementAPI.DataConnectors;
using AzureSentinel_ManagementAPI.Incidents;
using AzureSentinel_ManagementAPI.IncidentRelation;
using AzureSentinel_ManagementAPI.Infrastructure.Authentication;
using AzureSentinel_ManagementAPI.Infrastructure.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;
using AzureSentinel_ManagementAPI.Infrastructure.SharedModels;
using Microsoft.Extensions.Configuration;
using AzureSentinel_ManagementAPI.Hunting;

namespace AzureSentinel_ManagementAPI
{
    class AppHost
    {
        private readonly AuthenticationService authenticationService;
        private readonly AlertRulesController alertRulesController;
        private readonly AlertRuleTemplatesController alertRuleTemplatesController;
        private readonly IncidentsController incidentsController;
        private readonly ActionsController actionsController;
        private readonly BookmarksController bookmarksController;
        private readonly DataConnectorsController dataConnectorsController;
        private readonly IncidentRelationController incidentRelationController;
        private readonly SavedSearchController savedSearchController;
        private readonly AzureSentinelApiConfiguration[] configurations;

        private List<Tuple<string, int>> cmdArgs;
        private bool cliMode;

        public AppHost(
            IConfigurationRoot rawConfig,
            AzureSentinelApiConfiguration[] configurations,
            AlertRulesController alertRulesController,
            AuthenticationService authenticationService,
            AlertRuleTemplatesController alertRuleTemplatesController,
            IncidentsController incidentsController,
            ActionsController actionsController,
            BookmarksController bookmarksController,
            DataConnectorsController dataConnectorsController,
            IncidentRelationController incidentRelationController,
            SavedSearchController savedSearchController)
        {
            this.configurations = configurations;
            this.alertRulesController = alertRulesController;
            this.authenticationService = authenticationService;
            this.alertRuleTemplatesController = alertRuleTemplatesController;
            this.incidentsController = incidentsController;
            this.actionsController = actionsController;
            this.bookmarksController = bookmarksController;
            this.dataConnectorsController = dataConnectorsController;
            this.incidentRelationController = incidentRelationController;
            this.savedSearchController = savedSearchController;

            cliMode = rawConfig.GetValue<bool>("Climode");

            string exeName = "AzureSentinel_ManagementAPI.exe";
            cmdArgs = new TupleList<string, int>
            {
                {$": {exeName} 1 <actionRuleId> [instanceId]", 3 },
                {$": {exeName} 2 <actionRuleId> <actionId> [instanceId]", 4 },
                {$": {exeName} 3 <actionRuleId> <actionId> [instanceId]", 4},
                {$": {exeName} 4 <actionRuleId> [instanceId]", 3},
                {$": {exeName} 5 <alertRuleTemplateId> [instanceId]", 3},
                {$": {exeName} 6 [instanceId]", 2},
                {$": {exeName} 7 [instanceId]", 2},
                {$": {exeName} 8 [instanceId]", 2},
                {$": {exeName} 9 [instanceId]", 2},
                {$": {exeName} 10 <actionRuleId> [instanceId]", 3},
                {$": {exeName} 11 [instanceId]", 2},
                {$": {exeName} 12 <fusionRuleId> [instanceId]",   3},
                {$": {exeName} 13 <securityRuleId> [instanceId]", 3},
                {$": {exeName} 14 <scheduledRuleId> [instanceId]", 3},
                {$": {exeName} 15 [instanceId]", 2},
                {$": {exeName} 16 <bookmarkId> [instanceId]", 3},
                {$": {exeName} 17 <bookmarkId> [instanceId]", 3},
                {$": {exeName} 18 [instanceId]", 2},
                {$": {exeName} 19 [instanceId]", 2},
                {$": {exeName} 20 <bookmarkId> [instanceId]", 3},
                {$": {exeName} 21 [instanceId]", 2},
                {$": {exeName} 22 [instanceId]", 2},
                {$": {exeName} 23 <incidentId> [instanceId]", 3},
                {$": {exeName} 24 <incidentId> [instanceId]", 3},
                {$": {exeName} 25 [instanceId]", 2},
                {$": {exeName} 26 <incidentId> [instanceId]", 3},
                {$": {exeName} 27 [instanceId]", 2},
                {$": {exeName} 28 <incidentId> [instanceId]", 3},
                {$": {exeName} 29 <incidentId> [instanceId]", 3},
                {$": {exeName} 30 <incidentId> <commentId> [instanceId]", 4},
                {$": {exeName} 31 <incidentId> <bookmarkId> [instanceId]", 4},
                {$": {exeName} 32 <incidentId> <relationId> [instanceId]", 4},
                {$": {exeName} 33 <incidentId> [instanceId]", 3},
                {$": {exeName} 34 <incidentId> <relationId> [instanceId]", 4},
                {$": {exeName} 35 <incidentId> [instanceId]", 3},
            };
        }

        private void CommandInvalidFormatError()
        {
            Console.WriteLine("invalid command line");
            PrintCLIMenu();
            throw new Exception("invalid command line");
        }

        public async Task Run(string[] args)
        {
            if (cliMode) 
            {
                if (args.Length < 1)
                {
                    CommandInvalidFormatError();
                }

                string option = args[0];
                bool isValid = int.TryParse(option, out var index);
                isValid = isValid && index > 0 && index < 36;
                if (!isValid)
                {
                    CommandInvalidFormatError();
                }

                if (args.Length < cmdArgs[index - 1].Item2 - 1)
                {
                    CommandInvalidFormatError();
                }

                int insId = args.Length == cmdArgs[index - 1].Item2 - 1 ?
                    0 : int.Parse(args[cmdArgs[index - 1].Item2 - 1]);

                await RunCommands(cliMode, index, args, insId);
            } 
            else
            {
                while (true)
                {
                    PrintMenu();

                    Console.Write(Utils.GetString("Option"));
                    string option = Console.ReadLine();

                    bool isValid = int.TryParse(option, out var index);
                    isValid = isValid && index > 0 && index < 41;

                    if (!isValid)
                    {
                        Console.WriteLine(Utils.GetString("Invalid_Option_Text"));
                        Console.ReadLine();
                        continue;
                    }

                    await RunCommands(cliMode, index, args);

                    Console.WriteLine();
                    Console.WriteLine(Utils.GetString("Continue_Prompt_Text"));
                    Console.ReadLine();
                }
            }
        }

        public async Task RunCommands(bool cliMode, int index, string[] args, int insId = 0)
        {
            string response = "";

            try
            {
                switch (index)
                {
                    case 1:
                        {
                            string ruleId = cliMode ? args[1] : GetNonEmptyInput(Utils.GetString("Action_Rule_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await actionsController.CreateAction(ruleId, insId);
                            break;
                        }
                    case 2:
                        {
                            string ruleId = cliMode ? args[1] : GetNonEmptyInput(Utils.GetString("Action_Rule_Id_Prompt_Text"));
                            string actionId = cliMode ? args[2] : GetNonEmptyInput(Utils.GetString("Action_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await actionsController.DeleteAction(ruleId, actionId, insId);
                            break;
                        }
                    case 3:
                        {
                            string ruleId = cliMode ? args[1] : GetNonEmptyInput(Utils.GetString("Action_Rule_Id_Prompt_Text"));
                            string actionId = cliMode ? args[2] : GetNonEmptyInput(Utils.GetString("Action_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await actionsController.GetActionById(ruleId, actionId, insId);
                            break;
                        }
                    case 4:
                        {
                            string ruleId = cliMode ? args[1] : GetNonEmptyInput(Utils.GetString("Action_Rule_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await actionsController.GetActionsByRule(ruleId, insId);
                            break;
                        }

                    case 5:
                        {

                            string ruleTmplId = cliMode? args[1]: GetInput(Utils.GetString("Rule_Template_Id_Prompt_Text"),
                                "57c0cfc-d76d-463b-8755-c781608cdc1a");
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await alertRuleTemplatesController.GetAlertRuleTemplateById(ruleTmplId, insId);
                            break;
                        }
                    case 6:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await alertRuleTemplatesController.GetAlertRuleTemplates(insId);
                            break;
                        }

                    case 7:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await alertRulesController.CreateFusionAlertRule(insId);
                            break;
                        }
                    case 8:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await alertRulesController.CreateMicrosoftSecurityIncidentCreationAlertRule(insId);
                            break;
                        }
                    case 9:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await alertRulesController.CreateScheduledAlertRule(actionsController, insId);
                            break;
                        }
                    case 10:
                        {
                            string ruleId = cliMode ? args[1] : GetNonEmptyInput(Utils.GetString("Rule_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await alertRulesController.DeleteAlertRule(ruleId, insId);
                            break;
                        }
                    case 11:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await alertRulesController.GetAlertRules(insId);
                            break;
                        }
                    case 12:
                        {
                            string ruleId = cliMode ? args[1] : GetNonEmptyInput(Utils.GetString("Get_Fusion_Rule_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await alertRulesController.GetFusionAlertRule(ruleId, insId);
                            break;
                        }
                    case 13:
                        {
                            string ruleId = cliMode ? args[1] : GetInput(Utils.GetString("Get_Incident_Rule_Prompt_Text"), "Microsoft-alert-rule-2");
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await alertRulesController.GetMicrosoftSecurityIdentityCreationAlertRule(ruleId, insId);
                            break;
                        }
                    case 14:
                        {
                            string ruleId = cliMode ? args[1] : GetInput(Utils.GetString("Get_Scheduled_Rule_Prompt_Text"), "scheduled-alert-rule-3");
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await alertRulesController.GetScheduledAlertRule(ruleId, insId);
                            break;
                        }

                    case 15:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await bookmarksController.CreateBookmark(insId);
                            break;
                        }
                    case 16:
                        {
                            string bookmarkId = cliMode ? args[1] : GetNonEmptyInput(Utils.GetString("Bookmark_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await bookmarksController.DeleteBookmark(bookmarkId, insId);
                            break;
                        }
                    case 17:
                        {
                            string bookmarkId = cliMode ? args[1] : GetNonEmptyInput(Utils.GetString("Bookmark_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await bookmarksController.GetBookmarkById(bookmarkId, insId);
                            break;
                        }
                    case 18:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await bookmarksController.GetBookmarks(insId);
                            break;
                        }

                    case 19:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await dataConnectorsController.GetDataConnectors(insId);
                            break;
                        }
                    case 20:
                        {
                            string dataConnectorId = GetNonEmptyInput(Utils.GetString("Dataconnector_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await dataConnectorsController.DeleteDataConnector(dataConnectorId, insId);
                            break;
                        }
                    case 21:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await dataConnectorsController.CreateDataConnector(insId);
                            break;
                        }

                    case 22:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await incidentsController.CreateIncident(insId);
                            break;
                        }
                    case 23:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Delete_Incident_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await incidentsController.DeleteIncident(incidentId, insId);
                            break;
                        }
                    case 24:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Get_Incident_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await incidentsController.GetIncidentById(incidentId, insId);
                            break;
                        }
                    case 25:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await incidentsController.GetIncidents(insId);
                            break;
                        }
                    case 26:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await incidentsController.UpdateIncident(incidentId, insId);
                            break;
                        }
                    case 27:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await incidentsController.BatchUpdateIncidents(insId);
                            break;
                        }
                    case 28:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                            await incidentsController.CreateIncidentComment(incidentId);
                            break;
                        }
                    case 29:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await incidentsController.GetAllIncidentComments(incidentId, insId);
                            break;
                        }
                    case 30:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                            string commentId = GetNonEmptyInput(Utils.GetString("Comment_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await incidentsController.GetIncidentCommentById(incidentId, commentId, insId);
                            break;
                        }
                    case 31:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                            string bookmarkId = GetNonEmptyInput(Utils.GetString("Bookmark_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await incidentRelationController.CreateIncidentRelation(incidentId, bookmarkId, insId);
                            break;
                        }
                    case 32:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                            string relationId = GetNonEmptyInput(Utils.GetString("Relation_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await incidentRelationController.DeleteIncidentRelation(incidentId, relationId, insId);
                            break;
                        }
                    case 33:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            await incidentRelationController.GetEntitiesforIncident(incidentId, insId);
                            break;
                        }
                    case 34:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                            string relationId = GetNonEmptyInput(Utils.GetString("Relation_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            await incidentRelationController.GetIncidentRelationByName(incidentId, relationId, insId);
                            break;
                        }
                    case 35:
                        {
                            string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            await incidentRelationController.GetIncidentEntitiesbyEntityType(incidentId, insId);
                            break;
                        }
                    case 36:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await savedSearchController.CreateSavedSearch(insId);
                            break;
                        }
                    case 37:
                        {
                            string savedSearchId = GetNonEmptyInput(Utils.GetString("Saved_Search_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await savedSearchController.DeleteSavedSearch(savedSearchId, insId);
                            break;
                        }
                    case 38:
                        {
                            string savedSearchId = GetNonEmptyInput(Utils.GetString("Saved_Search_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            response = await savedSearchController.GetSavedSearchById(savedSearchId, insId);
                            break;
                        }
                    case 39:
                        {
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstanceOrApplyAll(configurations);
                            }
                            await savedSearchController.GetSavedSearches(insId);
                            break;
                        }
                    case 40:
                        {
                            string savedSearchId = GetNonEmptyInput(Utils.GetString("Saved_Search_Id_Prompt_Text"));
                            if (!cliMode)
                            {
                                insId = Utils.SelectInstance(configurations);
                            }
                            await savedSearchController.UpdateSavedSearch(savedSearchId, insId);
                            break;
                        }
                }

                if (response != string.Empty)
                {
                    Console.WriteLine(JToken.Parse(response).ToString(Formatting.Indented));
                }
            }
            catch (JsonReaderException exception)
            {
                if (string.IsNullOrEmpty(response))
                {
                    Console.WriteLine("Deleted");
                    Console.WriteLine(Utils.GetString("Continue_Prompt_Text"));
                    Console.ReadLine();
                    return;
                }               
            }
            catch (Exception exception)
            {
                ConsoleColor currentColor = Console.ForegroundColor;
                Console.ForegroundColor = ConsoleColor.Red;
                await Console.Error.WriteLineAsync(exception.Message);
                Console.ForegroundColor = currentColor;
            }

            Console.WriteLine(response);
        }

        private string GetNonEmptyInput(string promptText)
        {
            var id = "";
            
            while (id.Trim() == string.Empty)
            {
                Console.WriteLine(promptText);
                id = Console.ReadLine();
            }

            return id;
        }

        private string GetInput(string promptText, string defaultValue = "")
        {
            Console.WriteLine(promptText);
            var input = Console.ReadLine();
            
            if (input.Trim() == string.Empty)
            {
                input = defaultValue;
            }

            return input;
        }

        public void PrintMenu()
        {
            Console.WriteLine(Utils.GetString("Actions_Menu"));
            Console.WriteLine(Utils.GetString("Create_Action_Menu"));
            Console.WriteLine(Utils.GetString("Delete_Action_Menu"));
            Console.WriteLine(Utils.GetString("Get_Action_By_Id_Menu"));
            Console.WriteLine(Utils.GetString("Get_Actions_Menu"));
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Alert_Rule_Template_Menu"));
            Console.WriteLine(Utils.GetString("Get_Rule_Template_By_Id_Menu"));
            Console.WriteLine(Utils.GetString("Get_Rule_Templates_Menu"));
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Alert_Rules_Menu"));
            Console.WriteLine(Utils.GetString("Create_Fusion_Rule_Menu"));
            Console.WriteLine(Utils.GetString("Create_Incident_Rule_Menu"));
            Console.WriteLine(Utils.GetString("Create_Scheduled_Rule_Menu"));
            Console.WriteLine(Utils.GetString("Delete_Rule_Menu"));
            Console.WriteLine(Utils.GetString("Get_Rules_Menu"));
            Console.WriteLine(Utils.GetString("Get_Fusion_Rule_Menu"));
            Console.WriteLine(Utils.GetString("Get_Incident_Rule_Menu"));
            Console.WriteLine(Utils.GetString("Get_Scheduled_Rule_Menu"));
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Bookmarks_Menu"));
            Console.WriteLine(Utils.GetString("Create_Bookmark_Menu"));
            Console.WriteLine(Utils.GetString("Delete_Bookmark_Menu"));
            Console.WriteLine(Utils.GetString("Get_Bookmark_By_Id_Menu"));
            Console.WriteLine(Utils.GetString("Get_Bookmarks_Menu"));
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("DataConnectors_Menu"));
            Console.WriteLine(Utils.GetString("Get_DataConnectors_Menu"));
            Console.WriteLine(Utils.GetString("Delete_DataConnector_Menu"));
            Console.WriteLine(Utils.GetString("Create_DataConnector_Menu"));
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Incident_Menu"));
            Console.WriteLine(Utils.GetString("Create_Incident_Menu"));
            Console.WriteLine(Utils.GetString("Delete_Incident_Menu"));
            Console.WriteLine(Utils.GetString("Get_Incident_By_Id_Menu"));
            Console.WriteLine(Utils.GetString("Get_Incidents_Menu"));
            Console.WriteLine(Utils.GetString("Update_Incident_Menu"));
            Console.WriteLine(Utils.GetString("Batch_Update_Incidents_Menu"));
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Incident_Comments_Menu"));
            Console.WriteLine(Utils.GetString("Create_Incident_Comment_Menu"));
            Console.WriteLine(Utils.GetString("Get_Incident_Comments_Menu"));
            Console.WriteLine(Utils.GetString("Get_Incident_Comment_Menu"));
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Incident_Relation_Menu"));
            Console.WriteLine(Utils.GetString("Create_Relation_Menu"));
            Console.WriteLine(Utils.GetString("Delete_Relation_Menu"));
            Console.WriteLine(Utils.GetString("Get_Relations_Menu"));
            Console.WriteLine(Utils.GetString("Get_Relation_Menu"));
            Console.WriteLine(Utils.GetString("Get_Entities_By_Type_Menu"));
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Saved_Searches_Menu"));
            Console.WriteLine(Utils.GetString("Create_Saved_Search_Menu"));
            Console.WriteLine(Utils.GetString("Delete_Saved_Search_Menu"));
            Console.WriteLine(Utils.GetString("Get_Saved_Search_Menu"));
            Console.WriteLine(Utils.GetString("Get_Saved_Searches_Menu"));
            Console.WriteLine(Utils.GetString("Update_Saved_Search_Menu"));
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Exit_Text"));
        }


        public void PrintCLIMenu()
        {
            Console.WriteLine(Utils.GetString("Actions_Menu"));
            Console.WriteLine(Utils.GetString("Create_Action_Menu") + cmdArgs[0].Item1);
            Console.WriteLine(Utils.GetString("Delete_Action_Menu") + cmdArgs[1].Item1);
            Console.WriteLine(Utils.GetString("Get_Action_By_Id_Menu") + cmdArgs[2].Item1);
            Console.WriteLine(Utils.GetString("Get_Actions_Menu") + cmdArgs[3].Item1);
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Alert_Rule_Template_Menu"));
            Console.WriteLine(Utils.GetString("Get_Rule_Template_By_Id_Menu") + cmdArgs[4].Item1);
            Console.WriteLine(Utils.GetString("Get_Rule_Templates_Menu") + cmdArgs[5].Item1);
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Alert_Rules_Menu"));
            Console.WriteLine(Utils.GetString("Create_Fusion_Rule_Menu") + cmdArgs[6].Item1);
            Console.WriteLine(Utils.GetString("Create_Incident_Rule_Menu") + cmdArgs[7].Item1);
            Console.WriteLine(Utils.GetString("Create_Scheduled_Rule_Menu") + cmdArgs[8].Item1);
            Console.WriteLine(Utils.GetString("Delete_Rule_Menu") + cmdArgs[9].Item1);
            Console.WriteLine(Utils.GetString("Get_Rules_Menu") + cmdArgs[10].Item1);
            Console.WriteLine(Utils.GetString("Get_Fusion_Rule_Menu") + cmdArgs[11].Item1);
            Console.WriteLine(Utils.GetString("Get_Incident_Rule_Menu") + cmdArgs[12].Item1);
            Console.WriteLine(Utils.GetString("Get_Scheduled_Rule_Menu") + cmdArgs[13].Item1);
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Bookmarks_Menu"));
            Console.WriteLine(Utils.GetString("Create_Bookmark_Menu") + cmdArgs[14].Item1);
            Console.WriteLine(Utils.GetString("Delete_Bookmark_Menu") + cmdArgs[15].Item1);
            Console.WriteLine(Utils.GetString("Get_Bookmark_By_Id_Menu") + cmdArgs[16].Item1);
            Console.WriteLine(Utils.GetString("Get_Bookmarks_Menu") + cmdArgs[17].Item1);
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("DataConnectors_Menu"));
            Console.WriteLine(Utils.GetString("Get_DataConnectors_Menu") + cmdArgs[18].Item1);
            Console.WriteLine(Utils.GetString("Delete_DataConnector_Menu") + cmdArgs[19].Item1);
            Console.WriteLine(Utils.GetString("Create_DataConnector_Menu") + cmdArgs[20].Item1);
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Incident_Menu"));
            Console.WriteLine(Utils.GetString("Create_Incident_Menu") + cmdArgs[21].Item1);
            Console.WriteLine(Utils.GetString("Delete_Incident_Menu") + cmdArgs[22].Item1);
            Console.WriteLine(Utils.GetString("Get_Incident_By_Id_Menu") + cmdArgs[23].Item1);
            Console.WriteLine(Utils.GetString("Get_Incidents_Menu") + cmdArgs[24].Item1);
            Console.WriteLine(Utils.GetString("Update_Incident_Menu") + cmdArgs[25].Item1);
            Console.WriteLine(Utils.GetString("Batch_Update_Incidents_Menu") + cmdArgs[26].Item1);
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Incident_Comments_Menu"));
            Console.WriteLine(Utils.GetString("Create_Incident_Comment_Menu") + cmdArgs[27].Item1);
            Console.WriteLine(Utils.GetString("Get_Incident_Comments_Menu") + cmdArgs[28].Item1);
            Console.WriteLine(Utils.GetString("Get_Incident_Comment_Menu") + cmdArgs[29].Item1);
            Console.WriteLine();

            Console.WriteLine(Utils.GetString("Incident_Relation_Menu"));
            Console.WriteLine(Utils.GetString("Create_Relation_Menu") + cmdArgs[30].Item1);
            Console.WriteLine(Utils.GetString("Delete_Relation_Menu") + cmdArgs[31].Item1);
            Console.WriteLine(Utils.GetString("Get_Relations_Menu") + cmdArgs[32].Item1);
            Console.WriteLine(Utils.GetString("Get_Relation_Menu") + cmdArgs[33].Item1);
            Console.WriteLine(Utils.GetString("Get_Entities_By_Type_Menu") + cmdArgs[34].Item1);
            Console.WriteLine();
        }
    }
}
