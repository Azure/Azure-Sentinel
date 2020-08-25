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
        private readonly AzureSentinelApiConfiguration[] configurations;

        public AppHost(
            AzureSentinelApiConfiguration[] configurations,
            AlertRulesController alertRulesController,
            AuthenticationService authenticationService,
            AlertRuleTemplatesController alertRuleTemplatesController,
            IncidentsController incidentsController,
            ActionsController actionsController,
            BookmarksController bookmarksController,
            DataConnectorsController dataConnectorsController,
            IncidentRelationController incidentRelationController)
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
        }

        public async Task Run(string[] args)
        {
            while (true)
            {
                PrintMenu();

                Console.Write(Utils.GetString("Option"));
                string option = Console.ReadLine();

                bool isValid = int.TryParse(option, out var index);
                isValid = isValid && index > 0 && index < 36;

                if (!isValid)
                {
                    Console.WriteLine(Utils.GetString("Invalid_Option_Text"));
                    Console.ReadLine();
                    continue;
                }

                string response = "";

                try
                {
                    switch (index)
                    {
                        case 1:
                            {
                                string ruleId = GetNonEmptyInput(Utils.GetString("Action_Rule_Id_Prompt_Text"));
                                await actionsController.CreateAction(ruleId);
                                break;
                            }
                        case 2:
                            {
                                string ruleId = GetNonEmptyInput(Utils.GetString("Action_Rule_Id_Prompt_Text"));
                                string actionId = GetNonEmptyInput(Utils.GetString("Action_Id_Prompt_Text"));
                                response = await actionsController.DeleteAction(ruleId, actionId);
                                break;
                            }
                        case 3:
                            {
                                string ruleId = GetNonEmptyInput(Utils.GetString("Action_Rule_Id_Prompt_Text"));
                                string actionId = GetNonEmptyInput(Utils.GetString("Action_Id_Prompt_Text"));
                                response = await actionsController.GetActionById(ruleId, actionId);
                                break;
                            }
                        case 4:
                            {
                                string ruleId = GetNonEmptyInput(Utils.GetString("Action_Rule_Id_Prompt_Text"));
                                response = await actionsController.GetActionsByRule(ruleId);
                                break;
                            }

                        case 5:
                            {
                                string ruleTmplId = GetInput(Utils.GetString("Rule_Template_Id_Prompt_Text"),
                                    "57c0cfc-d76d-463b-8755-c781608cdc1a");
                                response = await alertRuleTemplatesController.GetAlertRuleTemplateById(ruleTmplId);
                                break;
                            }
                        case 6:
                            {
                                await alertRuleTemplatesController.GetAlertRuleTemplates();
                                break;
                            }

                        case 7:
                            {
                                await alertRulesController.CreateFusionAlertRule();
                                break;
                            }
                        case 8:
                            {
                                await alertRulesController.CreateMicrosoftSecurityIncidentCreationAlertRule();
                                break;
                            }
                        case 9:
                            {
                                await alertRulesController.CreateScheduledAlertRule();
                                break;
                            }
                        case 10:
                            {
                                string ruleId = GetNonEmptyInput(Utils.GetString("Rule_Id_Prompt_Text"));
                                response = await alertRulesController.DeleteAlertRule(ruleId);
                                break;
                            }
                        case 11:
                            {
                                await alertRulesController.GetAlertRules();
                                break;
                            }
                        case 12:
                            {
                                string ruleId = GetNonEmptyInput(Utils.GetString("Get_Fusion_Rule_Prompt_Text"));
                                response = await alertRulesController.GetFusionAlertRule(ruleId);
                                break;
                            }
                        case 13:
                            {
                                string ruleId = GetInput(Utils.GetString("Get_Incident_Rule_Prompt_Text"), "Microsoft-alert-rule-2");
                                response = await alertRulesController.GetMicrosoftSecurityIdentityCreationAlertRule(ruleId);
                                break;
                            }
                        case 14:
                            {
                                string ruleId = GetInput(Utils.GetString("Get_Scheduled_Rule_Prompt_Text"), "scheduled-alert-rule-3");
                                response = await alertRulesController.GetScheduledAlertRule(ruleId);
                                break;
                            }

                        case 15:
                            {
                                await bookmarksController.CreateBookmark();
                                break;
                            }
                        case 16:
                            {
                                string bookmarkId = GetNonEmptyInput(Utils.GetString("Bookmark_Prompt_Text"));
                                response = await bookmarksController.DeleteBookmark(bookmarkId);
                                break;
                            }
                        case 17:
                            {
                                string bookmarkId = GetNonEmptyInput(Utils.GetString("Bookmark_Prompt_Text"));
                                response = await bookmarksController.GetBookmarkById(bookmarkId);
                                break;
                            }
                        case 18:
                            {
                                await bookmarksController.GetBookmarks();
                                break;
                            }

                        case 19:
                            {
                                await dataConnectorsController.GetDataConnectors();
                                break;
                            }
                        case 20:
                            {
                                string dataConnectorId = GetNonEmptyInput(Utils.GetString("Dataconnector_Prompt_Text"));
                                response = await dataConnectorsController.DeleteDataConnector(dataConnectorId);
                                break;
                            }
                        case 21:
                            {
                                await dataConnectorsController.CreateDataConnector();
                                break;
                            }

                        case 22:
                            {
                                await incidentsController.CreateIncident();
                                break;
                            }
                        case 23:
                            {
                                string incidentId = GetNonEmptyInput(Utils.GetString("Delete_Incident_Prompt_Text"));
                                response = await incidentsController.DeleteIncident(incidentId);
                                break;
                            }
                        case 24:
                            {
                                string incidentId = GetNonEmptyInput(Utils.GetString("Get_Incident_Prompt_Text"));
                                int insId = Utils.SelectInstance(configurations);
                                response = await incidentsController.GetIncidentById(incidentId, insId);
                                break;
                            }
                        case 25:
                            {
                                await incidentsController.GetIncidents();
                                break;
                            }
                        case 26:
                            {
                                string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                                response = await incidentsController.UpdateIncident(incidentId);
                                break;
                            }
                        case 27:
                            {
                                await incidentsController.BatchUpdateIncidents();
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
                                response = await incidentsController.GetAllIncidentComments(incidentId);
                                break;
                            }
                        case 30:
                            {
                                string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                                string commentId = GetNonEmptyInput(Utils.GetString("Comment_Id_Prompt_Text"));
                                response = await incidentsController.GetIncidentCommentById(incidentId, commentId);
                                break;
                            }
                        case 31:
                            {
                                string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                                string bookmarkId = GetNonEmptyInput(Utils.GetString("Bookmark_Prompt_Text"));
                                response = await incidentRelationController.CreateIncidentRelation(incidentId, bookmarkId);
                                break;
                            }
                        case 32:
                            {
                                string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                                string relationId = GetNonEmptyInput(Utils.GetString("Relation_Id_Prompt_Text"));
                                response = await incidentRelationController.DeleteIncidentRelation(incidentId, relationId);
                                break;
                            }
                        case 33:
                            {
                                string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                                await incidentRelationController.GetEntitiesforIncident(incidentId);
                                break;
                            }
                        case 34:
                            {
                                string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                                string relationId = GetNonEmptyInput(Utils.GetString("Relation_Id_Prompt_Text"));
                                await incidentRelationController.GetIncidentRelationByName(incidentId, relationId);
                                break;
                            }
                        case 35:
                            {
                                string incidentId = GetNonEmptyInput(Utils.GetString("Incident_Id_Prompt_Text"));
                                await incidentRelationController.GetIncidentEntitiesbyEntityType(incidentId);
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
                        continue;
                    }

                    Console.WriteLine(response);
                }

                catch (Exception exception)
                {
                    ConsoleColor currentColor = Console.ForegroundColor;
                    Console.ForegroundColor = ConsoleColor.Red;
                    await Console.Error.WriteLineAsync(exception.Message);
                    Console.ForegroundColor = currentColor;
                }

                Console.WriteLine();
                Console.WriteLine(Utils.GetString("Continue_Prompt_Text"));
                Console.ReadLine();
            }
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

            Console.WriteLine(Utils.GetString("Exit_Text"));
        }
    }
}
