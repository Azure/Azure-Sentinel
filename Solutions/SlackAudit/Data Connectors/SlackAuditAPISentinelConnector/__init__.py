import requests
import json
import datetime
import azure.functions as func
import base64
import hmac
import hashlib
import os
import logging
import re
from .state_manager import StateManager

customer_id = os.environ['WorkspaceID'] 
shared_key = os.environ['WorkspaceKey']
slack_api_bearer_token = os.environ['SlackAPIBearerToken']
logAnalyticsUri = os.environ.get('logAnalyticsUri')
log_type = 'SlackAudit'
slack_uri_audit = "https://api.slack.com/audit/v1/logs"
offset_limit = 1000
connection_string = os.environ['AzureWebJobsStorage']

if ((logAnalyticsUri in (None, '') or str(logAnalyticsUri).isspace())):
    logAnalyticsUri = 'https://' + customer_id + '.ods.opinsights.azure.com'

pattern = r"https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$"
match = re.match(pattern,str(logAnalyticsUri))
if(not match):
    raise Exception("Invalid Log Analytics Uri.")

def action_mapping(event):
    action_id = event["action"]
    action_dict = {
        "workspace_created": "A workspace in an organization was created.",
        "workspace_deleted": "A workspace in an organization was deleted.",
        "workspace_accepted_migration": "An administrator on a workspace has accepted an invitation to migrate to a Grid organization.",
        "workspace_declined_migration": "An administrator on a workspace has declined an invitation to migrate to a Grid organization.",
        "migration_scheduled": "A migration was scheduled.",
        "organization_verified": "Slack has confirmed the identity of your organization. The organization will now be denoted with a verified badge.",
        "organization_unverified": "Slack has flagged a change in your organization’s identity and has unverified it. The organization will no longer be denoted with a verified badge.",
        "organization_public_url_updated": "Your organization’s public URL has been changed.",
        "organization_created": "An Enterprise Grid organization was created.",
        "organization_deleted": "An Enterprise Grid organization was deleted.",
        "organization_accepted_migration": "The Org Owner accepted a workspace invitation to join their organization.",
        "organization_declined_migration": "The Org Owner declined a workspace invitation to join their organization.",
        "billing_address_added": "A billing address was added. Includes a details parameter noting the timestamp the TOS was accepted.",
        "emoji_added": "An emoji was added. Includes a details parameter with the name of the emoji.",
        "emoji_removed": "An emoji was removed. Includes a details parameter with the name of the emoji.",
        "emoji_aliased": "An emoji was given an alias. Includes a details parameter with the name of the alias.",
        "emoji_renamed": "An emoji was renamed. Includes a details parameter with the previous and new names of the emoji.",
        "message_tombstoned": "A message was tombstoned.",
        "message_restored": "A message was restored.",
        "manual_export_started": "A workspace admin or owner has started a standard export on a workspace.",
        "manual_export_completed": "A standard export on a workspace has finished.",
        "corporate_exports_approved": "The corporate export feature has been approved for use on a workspace.",
        "corporate_exports_enabled": "The corporate export feature has been enabled for a workspace.",
        "scheduled_export_started": "A scheduled corporate export has started.",
        "scheduled_export_completed": "A scheduled corporate export has finished.",
        "channels_export_started": "A channel export has begun.",
        "channels_export_completed": "A channel export is complete.",
        "pref.allow_calls": "A preference indicating whether Slack Calls can be used in this workspace has changed.",
        "pref.allow_message_deletion": "Someone altered this workspace's settings around whether messages can be deleted or not.",
        "pref.app_dir_only": "Whether only Slack App Directory apps can be installed or not in this workspace has changed.",
        "pref.app_whitelist_enabled": "Someone's carefully carved or culled the list of apps this workspace has whitelisted.",
        "pref.can_receive_shared_channels_invites": "Whether this workspace can receive invites to share channels with other workspaces has changed.",
        "pref.commands_only_regular": "The setting determining whether restricted users are restricted from using slash commands was changed.",
        "pref.custom_tos": "This workspace's settings on having a custom terms of service have changed.",
        "pref.disallow_public_file_urls": "This workspace has modified their public file URL settings for files uploaded within it.",
        "pref.dm_retention_changed": "The direct message (DM) retention setting changed. Includes a details parameter noting the previous and new values.",
        "pref.dnd_enabled": "Do not disturb settings have been enabled for a workspace.",
        "pref.dnd_end_hour": "The exact ending hour for workspace do not disturb settings has been set. Work hard and go home.",
        "pref.dnd_start_hour": "The exact starting hour for workspace do not disturb settings has been set. Hopefully everyone is awake and ready to work by then.",
        "pref.emoji_only_admins": "Someone modified the list of emoji-administrating admins, so you know who stole the cookies from the cookie jar.",
        "pref.enterprise_default_channels": "Someone modified the list of default channels across the enterprise grid.",
        "pref.enterprise_team_creation_request": "Someone has requested that your organization allow a new workspace to be created.",
        "pref.file_retention_changed": "The file retention setting changed. Includes a details parameter noting the previous and new values.",
        "pref.msg_edit_window_mins": "Someone edited the edit messaging window for a workspace!",
        "pref.private_channel_retention_changed": "The group (private channel) retention setting changed. Includes a details parameter noting the previous and new values.",
        "pref.public_channel_retention_changed": "The channel retention setting type changed. Includes a details parameter noting the previous and new values.",
        "pref.retention_override_changed": "The retention override setting, allowing workspace members to set their own retention period for private channels and DMs, changed. Includes a details parameter noting the previous and new values.",
        "pref.sign_in_with_slack_disabled": "This workspace changed their preference around allowing Sign in with Slack.",
        "pref.slackbot_responses_disabled": "The settings around whether Slackbot's witty responses are enabled or disabled changed.",
        "pref.slackbot_responses_only_admins": "There's a secret cabal of admins for those witty Slackbot responses and that list was changed.",
        "pref.sso_setting_changed": "The Single Sign On (SSO) restriction changed. Includes a details parameter noting the previous and new values.",
        "pref.stats_only_admins": "The list of admins that can work with workspace statistics only has changed.",
        "pref.two_factor_auth_changed": "The two-factor authentication requiremented changed. Includes a details parameter noting the previous and new values.",
        "pref.username_policy": "A workspace's username policy preference changed.",
        "pref.who_can_archive_channels": "Who can archive channels indeed?",
        "pref.who_can_create_delete_user_groups": "The list of who can create or delete user groups changed.",
        "pref.who_can_create_private_channels": "It's like a who's who of who can create private channels, and it changed.",
        "pref.who_can_create_public_channels": "The same as above, but for public channels.",
        "pref.who_can_edit_user_groups": "The list of those who can edit user groups changed.",
        "pref.who_can_manage_channel_posting_prefs": "Someone's been changing who can manage channel posting preferences",
        "pref.who_can_manage_ext_shared_channels": "The list of who can manage externally shared channels has changed for this workspace.",
        "pref.who_can_manage_guests": "The list of who can manage guests now has changed for this workspace.",
        "pref.who_can_manage_shared_channels": "Settings around who can remove users from shared channels has changed for a workspace.",
        "pref.who_can_remove_from_private_channels": "Settings around who can remove users from private channels has changed for a workspace.",
        "pref.who_can_remove_from_public_channels": "Settings around who can remove users from public channels has changed for a workspace.",
        "ekm_enrolled": "The workspace is now enrolled/managed by EKM.",
        "ekm_unenrolled": "The workspace is no longer enrolled or managed by EKM.",
        "ekm_key_added": "An EKM key was added for the workspace.",
        "ekm_key_removed": "An EKM key was removed for the workspace.",
        "ekm_clear_cache_set": "A revocation event has triggered a new TTL for cached date in this workspace.",
        "ekm_logging_config_set": "Logging settings for this workspace's EKM configuration have changed.",
        "ekm_slackbot_enroll_notification_sent": "Slack sent notifications about this workspace being enrolled in EKM.",
        "ekm_slackbot_unenroll_notification_sent": "Slack sent notifications about this workspace no longer being enrolled in EKM.",
        "ekm_slackbot_rekey_notification_sent": "Slack sent notifications about this workspace's EKM configuration being rekeyed.",
        "ekm_slackbot_logging_notification_sent": "Slack sent notifications about logging changes to EKM in this workspace.",
        "user_channel_join": "A user has joined a channel. The user field in this action contains a team identifier so that you can see which team the joining user comes from (useful for externally shared channels).",
        "user_channel_leave": "A user has left a channel. This action contains a team identifier so that you can see which team the departing user comes from (useful for externally shared channels).",
        "guest_channel_join": "A guest user has joined a channel. This action contains a team identifier so that you can see which team the joining guest comes from (useful for externally shared channels).",
        "guest_channel_leave": "A guest user has left a channel. This action contains a team identifier so that you can see which team the departing guest comes from (useful for externally shared channels).",
        "guest_created": "A guest was invited to a channel. This action contains a team identifier so that you can see which team the inviting user comes from.",
        "channel_moved": "A channel has been moved to a different workspace.",
        "public_channel_created": "A public channel was created.",
        "private_channel_created": "A private channel was created.",
        "public_channel_archive": "A public channel was archived.",
        "private_channel_archive": "A private channel was archived.",
        "public_channel_unarchive": "A public channel was unarchived.",
        "private_channel_unarchive": "A private channel was unarchived.",
        "public_channel_deleted": "A public channel was deleted.",
        "private_channel_deleted": "A private channel was deleted.",
        "mpim_converted_to_private": "A multi-party direct message was converted to a private channel.",
        "public_channel_converted_to_private": "A channel which was once public is now private.",
        "channel_email_address_created": "An email forwarding address was created for a channel.",
        "channel_email_address_deleted": "An email forwarding address was deleted from channel.",
        "external_shared_channel_connected": "A shared channel with another workspace has been connected with this one.",
        "external_shared_channel_disconnected": "A shared channel with another workspace is no longer connected with this one.",
        "external_shared_channel_reconnected": "A previously connected and then disconnected shared channel with another workspace is once again shared with this one.",
        "external_shared_channel_invite_sent": "An invitation to join a shared channel was sent.",
        "external_shared_channel_invite_accepted": "An invitation to join a shared channel was accepted! Nice.",
        "external_shared_channel_invite_approved": "An invitation to join a shared channel was approved by an admin.",
        "external_shared_channel_invite_created": "An invitation url to join a shared channel was created.",
        "external_shared_channel_invite_declined": "An invitation to join a shared channel was declined.",
        "external_shared_channel_invite_expired": "An invitation to join a shared channel expired.",
        "external_shared_channel_invite_revoked": "An invitation to join a shared channel was revoked.",
        "role_change_to_owner": "A team member was made an owner.",
        "role_change_to_admin": "A team member was made an admin.",
        "role_change_to_user": "A team member was a user.",
        "role_change_to_guest": "A team member was made a guest.",
        "owner_transferred": "An owner was transferred.",
        "user_created": "A team member was created.",
        "user_deactivated": "A team member was deactivated.",
        "user_reactivated": "A team member was reactivated after having been deactivated.",
        "user_login_failed": "A team member login failed",
        "guest_created": "A guest was created.",
        "guest_deactivated": "A guest was deactivated.",
        "guest_reactivated": "A guest was reactivated after having been deactivated.",
        "guest_expiration_set": "A guest had an account expiration time set.",
        "guest_expired": "A guest was deactivated when the expiration time was reached.",
        "guest_expiration_cleared": "A guest had an expiration time cleared (before this time arrived).",
        "user_login": "A team member logged in.",
        "user_logout": "A team member logged out.",
        "custom_tos_accepted": "A team member accepted a custom terms of service agreement.",
        "app_approved": "On workspaces that have admin approved apps enabled, an app has been approved but not yet installed.",
        "app_restricted": "On workspaces that have admin approved apps enabled, an app has been restricted and cannot be installed.",
        "app_installed": "An app has been installed. If a custom integration had been disabled, this event will also be triggered if it is re-enabled.",
        "app_scopes_expanded": "An app has been granted additional access to resources on a workspace, via OAuth scopes. For most apps, this requires a re-install. For workspace apps, this may also happen via the permissions API.",
        "app_resources_added": "Workspace apps have the ability to request access to a specific resource on a workspace, such as a channel or a DM, including wildcard resources (such as all public channels). This event is triggered when access has been granted.",
        "app_uninstalled": "A Slack app was uninstalled.",
        "app_token_preserved": "An app's token was preserved instead of revoked, usually due to an app owner or installer being removed from an organization.",
        "file_downloaded": "A file was downloaded.",
        "file_downloaded_blocked": "A file was blocked from being downloaded.",
        "file_uploaded": "A file was uploaded. This action contains a team identifier so that you can see which team the uploading user comes from (useful for externally shared channels).",
        "file_public_link_created": "A public link was created for a file. This action contains a team identifier so that you can see which team the creating user comes from (useful for externally shared channels).",
        "file_public_link_revoked": "A public link was revoked from a file. This action contains a team identifier so that you can see which team the revoking user comes from (useful for externally shared channels).",
        "file_shared": "A file was shared in another channel.",
        "workflow_created": "A workflow has been created.",
        "workflow_deleted": "A workflow has been deleted.",
        "workflow_published": "A workflow has been published.",
        "workflow_unpublished": "A workflow has been unpublished.",
        "workflow_responses_csv_download": "A user downloaded a workflow’s responses as a CSV file."
    }
    if action_id in action_dict.keys():
        action_desc = action_dict[action_id]
        event["action_description"] = action_desc
    return event


def process_events(events_obj):
    map_result = map(action_mapping, events_obj)
    to_list = list(map_result)
    element_count = len(to_list)
    global global_element_count, oldest, latest
    if element_count > 0:
        post_status_code = post_data(json.dumps(to_list))
        if post_status_code is not None:
            global_element_count = global_element_count + element_count


def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
    x_headers = 'x-ms-date:' + date
    string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
    bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
    decoded_key = base64.b64decode(shared_key)
    encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
    authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
    return authorization


def post_data(body):
    method = 'POST'
    content_type = 'application/json'
    resource = '/api/logs'
    rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    content_length = len(body)
    signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
    uri = logAnalyticsUri + resource + '?api-version=2016-04-01'
    headers = {
        'content-type': content_type,
        'Authorization': signature,
        'Log-Type': log_type,
        'x-ms-date': rfc1123date
    }
    response = requests.post(uri,data=body, headers=headers)
    if (response.status_code >= 200 and response.status_code <= 299):
        return response.status_code
    else:
        logging.warn("Events are not processed into Azure. Response code: {}".format(response.status_code))
        return None


def get_result_request(params):
    try:
        r = requests.get(url=slack_uri_audit,
                         headers={'Accept': 'application/json',
                                  "Authorization": "Bearer "+ slack_api_bearer_token
                                  },
                         params=params)
        if r.status_code == 200:
            if "entries" in r.json():
                result = r.json()["entries"]
                if len(result) > 0:
                    logging.info("Processing {} events".format(len(result)))
                    process_events(result)
            else:
                logging.info("There are no entries from the output.")
            #check next_page cursor
            if "response_metadata" in r.json():
                if "next_cursor" in r.json()["response_metadata"]:
                    if r.json()["response_metadata"]["next_cursor"] == "":
                        return None
                    else:
                        return r.json()["response_metadata"]["next_cursor"]
                else:
                    return None
            else:
                return None
        elif r.status_code == 401:
            logging.error("The authentication credentials are incorrect or missing. Error code: {}".format(r.status_code))
        elif r.status_code == 403:
            logging.error("The user does not have the required permissions. Error code: {}".format(r.status_code))
        else:
            logging.error("Something wrong. Error code: {}".format(r.status_code))
    except Exception as err:
        logging.error("Something wrong. Exception error text: {}".format(err))


def generate_date():
    current_time = datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(minutes=10)
    state = StateManager(connection_string=connection_string)
    past_time = state.get()
    if past_time is not None:
        logging.info("The last time point is: {}".format(past_time))
    else:
        logging.info("There is no last time point, trying to get events for last hour.")
        past_time = (current_time - datetime.timedelta(minutes=60)).strftime("%s")
    state.post(current_time.strftime("%s"))
    return (past_time, current_time.strftime("%s"))


def main(mytimer: func.TimerRequest)  -> None:
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Starting program')
    global global_element_count
    global_element_count = 0
    oldest, latest = generate_date()
    logging.info("Start processing events to Azure Sentinel. Time period: from {} to {}.".format(datetime.datetime.fromtimestamp(int(oldest)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                                                      datetime.datetime.fromtimestamp(int(latest)).strftime("%Y-%m-%dT%H:%M:%SZ")))
    params = {
        "limit": offset_limit,
        "oldest": oldest,
        "latest": latest
    }
    next_cursor = get_result_request(params)
    while next_cursor is not None:
        params = {
            "limit": offset_limit,
            "oldest": oldest,
            "latest": latest,
            "cursor": next_cursor
        }
        next_cursor = get_result_request(params)
    logging.info("Processed {} events to Azure Sentinel. Time period: from {} to {}.".format(global_element_count, datetime.datetime.fromtimestamp(int(oldest)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                                                      datetime.datetime.fromtimestamp(int(latest)).strftime("%Y-%m-%dT%H:%M:%SZ")))