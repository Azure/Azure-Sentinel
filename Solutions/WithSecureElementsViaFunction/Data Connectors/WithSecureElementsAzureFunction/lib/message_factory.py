import configparser
import os
import re

from pathlib import PurePosixPath, PureWindowsPath


class MessageFactory:
    DEEP_GUARD_RARITIES = ["unknown", "rare", "common"]
    DEEP_GUARD_REPUTATIONS = [
        "unknown",
        "clean",
        "harmful",
        "potentiallyUnwanted",
        "unwanted",
    ]
    DEEP_GUARD_ALERTS_WITH_TARGET = {
        "deep_guard.modifying_settings.block",
        "deep_guard.modifying_file_or_folder.block",
        "deep_guard.modifying_another_process.block",
        "deep_guard.ransomware.block",
    }

    def __init__(self):
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, "messages.properties")
        self.config = configparser.ConfigParser()
        self.config.read(path_config_file)

    def get_message(self, event):
        try:
            details = event.details
            if "initiator" in details:
                source = details["initiator"]
            else:
                source = self.config.get(
                    "generic", "security_event_message.not_available"
                )
            return self._get_custom_message(source, event)
        except configparser.NoOptionError:
            return self._get_not_available_message()

    def _get_custom_message(self, source, event):
        message = self._get_detailed_message(source, event)
        if not message:
            return self._get_default_message(source, event.engine, event.action)
        return message

    def _get_not_available_message(self):
        return self.config.get("generic", "security_event_message.not_available")

    def _get_default_message(self, source, engine, action):
        key = "security_event_message.{engine}"
        action_name = self.config.get("actions", f"actions.{action}")
        return self._format_msg(engine, key, {"engine": engine}, [action_name, source])

    def _get_detailed_message(self, source, event):
        details = event.details
        engine = event.engine
        action = event.action
        match event.engine:
            case "webTrafficScanning":
                if "alertType" in details:
                    alert_type = (
                        str(details["alertType"])
                        .replace("web_traffic_scanning.", "")
                        .replace(".", "_")
                    )
                    key = "security_event_message.{engine}.alerts.{alert_type}"
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "alert_type": alert_type},
                        [
                            details.get("url", ""),
                            event.process_name(),
                        ],
                    )
                else:
                    key = "security_event_message.{engine}.actions.{action}"
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "action": action},
                        [
                            details.get("websiteUrl", ""),
                            event.file_name(),
                        ],
                    )
            case "webContentControl":
                reason = details.get("reason", "")
                if reason == "WF_Category":
                    key = "security_event_message.{engine}.{reason}.{action}"
                    category = str(details["categories"]).split(",")[0]
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "reason": reason, "action": action},
                        [category],
                    )
                else:
                    return None
            case "fileScanning" | "manualScanning" | "realtimeScanning":
                key = "security_event_message.fileScanning.{action}"
                if "infectionType" in details:
                    return self._format_msg(
                        "fileScanning",
                        key,
                        {"action": action},
                        [details["infectionType"], get_file_name(source)],
                    )
                else:
                    if "name" in details:
                        name = details["name"]
                    else:
                        name = details.get("infectionName", "")
                    file_path = event.file_path()
                    return self._format_msg(
                        "fileScanning",
                        key,
                        {"action": action},
                        [name, get_file_name(file_path)],
                    )
            case "deepGuard":
                deep_guard_rarity_reputation_regex = (
                    "Rarity: (\\d+), Reputation: (\\d+)"
                )
                if "name" in details:
                    # V1 event
                    match_result = re.findall(
                        deep_guard_rarity_reputation_regex, details["name"]
                    )
                    if len(match_result) != 0:
                        rarity_index = int(match_result[0][0])
                        reputation_index = int(match_result[0][1])
                        rarity = MessageFactory.DEEP_GUARD_RARITIES[rarity_index]
                        reputation = MessageFactory.DEEP_GUARD_REPUTATIONS[
                            reputation_index
                        ]
                        key = "security_event_message.{engine}.rarity_{rarity}.reputation_{reputation}"
                        return self._format_msg(
                            engine,
                            key,
                            {
                                "engine": engine,
                                "rarity": rarity,
                                "reputation": reputation,
                            },
                            [source],
                        )
                    elif details["name"] == "DeepGuard blocks a rare application":
                        key = "security_event_message.{engine}.rare_application_blocked"
                        return self._format_msg(
                            engine, key, {"engine": engine}, [source]
                        )
                    else:
                        key = "security_event_message.{engine}.action_{action}"
                        return self._format_msg(
                            engine,
                            key,
                            {"engine": engine, "action": action},
                            [details["name"], source],
                        )
                else:
                    # V2 event
                    alert_type = details.get("alertType", "")
                    if (
                        "targetPath" in details
                        and alert_type in MessageFactory.DEEP_GUARD_ALERTS_WITH_TARGET
                    ):
                        key = "security_event_message.{engine}.{alert_type}.target"
                        return self._format_msg(
                            engine,
                            key,
                            {"engine": engine, "alert_type": alert_type},
                            [source, get_file_name(details["targetPath"])],
                        )
                    else:
                        key = "security_event_message.{engine}.{alert_type}"
                        return self._format_msg(
                            engine,
                            key,
                            {"engine": engine, "alert_type": alert_type},
                            [source],
                        )
            case "dataGuard":
                key = "security_event_message.{engine}.{action}"
                return self._format_msg(
                    engine,
                    key,
                    {"engine": engine, "action": action},
                    [get_file_name(details.get("targetData", ""))],
                )
            case "browsingProtection":
                reason = details.get("reason", "")
                if reason == "WF_Denied":
                    key = "security_event_message.{engine}.{reason}.{action}"
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "reason": reason, "action": action},
                        [],
                    )
                else:
                    return None
            case "connectionControl":
                key = "security_event_message.{engine}.{action}"
                return self._format_msg(
                    engine,
                    key,
                    {"engine": engine, "action": action},
                    [details.get("process", "")],
                )
            case "reputationBasedBrowsing":
                supported_reasons = {"BP_Suspicious", "BP_Harmful", "BP_Illegal"}
                if details.get("reason") in supported_reasons:
                    key = "security_event_message.{engine}.{reason}.{action}"
                    return self._format_msg(
                        engine,
                        key,
                        {
                            "engine": engine,
                            "reason": details["reason"],
                            "action": action,
                        },
                        [details.get("url", "")],
                    )
                else:
                    return None
            case "tamperProtection":
                if "requestType" in details:
                    request_type = details["requestType"]
                else:
                    if "actionType" in details:
                        action_type = details["actionType"]
                        if action_type == "service":
                            request_type = "service_stop"
                        elif action_type == "uninstall":
                            request_type = "uninstall"
                        else:
                            request_type = "unknown"
                    else:
                        request_type = "unknown"
                key = "security_event_message.{engine}.{request_type}"
                if request_type == "service_stop":
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "request_type": request_type},
                        [details.get("service", "")],
                    )
                elif request_type == "uninstall":
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "request_type": request_type},
                        [get_file_name(details.get("initiator", ""))],
                    )
                elif request_type == "rename_file" or request_type == "rename_folder":
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "request_type": request_type},
                        [
                            get_file_name(details.get("initiator", "")),
                            details.get("path", ""),
                            details.get("target", ""),
                        ],
                    )
                elif request_type in (
                    "reg_delete_key",
                    "reg_delete_value",
                    "reg_set_value",
                    "reg_rename_key",
                ):
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "request_type": request_type},
                        [
                            get_file_name(details.get("initiator", "")),
                            details.get("path", ""),
                        ],
                    )
                else:
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "request_type": request_type},
                        [
                            get_file_name(details.get("initiator", "")),
                            get_file_name(details.get("path", "")),
                        ],
                    )
            case "firewall":
                key = "security_event_message.{engine}.{action}.{rule_direction}"
                rule_direction = details.get("ruleDirection", "")
                return self._format_msg(
                    engine,
                    key,
                    {
                        "engine": engine,
                        "action": action,
                        "rule_direction": rule_direction,
                    },
                    [
                        details.get("remoteAddress"),
                        get_file_name(details.get("process", "")),
                    ],
                )
            case "amsi":
                infection_type = details.get("infectionType", "undefined")
                key = "security_event_message.{engine}.{infection_type}.{action}"
                return self._format_msg(
                    engine,
                    key,
                    {
                        "engine": engine,
                        "infection_type": infection_type,
                        "action": action,
                    },
                    [get_file_name(details.get("path", ""))],
                )
            case "connector":
                key = "security_event_message.{engine}.{alert_type}"
                alert_type = details.get("alertType", "")
                return self._format_msg(
                    engine,
                    key,
                    {"engine": engine, "alert_type": alert_type},
                    [details.get("daysFromLastUpdate", "")],
                )
            case "applicationControl":
                key = "security_event_message.{engine}.{action}"
                if action == "blocked" or action == "reported":
                    if "targetProductName" in details and details["targetProductName"]:
                        target = details.get("targetProductName")
                    else:
                        target = details.get("targetPath", "")
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "action": action},
                        [
                            details.get("ruleEvent", ""),
                            target,
                            details.get("ruleName", ""),
                        ],
                    )
                else:
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "action": action},
                        [details["ruleName"]],
                    )
            case "deviceControl":
                alert_type = details.get("alertType", "")
                key = "security_event_message.{engine}.{alert_type}"
                if alert_type == "device_control.device.blocked":
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "alert_type": alert_type},
                        [details.get("deviceName", ""), details.get("appliedRule", "")],
                    )
                else:
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "alert_type": alert_type},
                        [details.get("deviceName", "")],
                    )
            case "integrityChecker":
                alert_type = details.get("alertType", "")
                file_path = event.file_path()
                if alert_type == "detection":
                    key = "security_event_message.{engine}.{alert_type}.{action}"
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "alert_type": alert_type, "action": action},
                        [details.get("detection.description", ""), file_path],
                    )
                elif alert_type == "tampering":
                    key = "security_event_message.{engine}.{alert_type}.{action}"
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "alert_type": alert_type, "action": action},
                        [file_path],
                    )
                elif alert_type == "tampering-action":
                    key = "security_event_message.{engine}.{alert_type}"
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "alert_type": alert_type},
                        [details.get("process-id", ""), file_path],
                    )
                else:
                    return None
            case "setting":
                key = "security_event_message.{engine}.{setting_name}.{new_value}"
                setting_name = details.get("settingName", "")
                new_value = details.get("newValue", "")
                return self._format_msg(
                    engine,
                    key,
                    {
                        "engine": engine,
                        "setting_name": setting_name,
                        "new_value": new_value,
                    },
                    [],
                )
            case "edr":
                key = "security_event_message.{engine}.{action}"
                if action == "closed" or action == "created" or action == "updated":
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "action": action},
                        [details.get("incidentPublicId", "")],
                    )
                elif action == "merged":
                    return self._format_msg(
                        engine,
                        key,
                        {"engine": engine, "action": action},
                        [
                            details.get("incidentPublicId", ""),
                            details.get("mergedTo", ""),
                        ],
                    )
                else:
                    return None
            case "systemEventsLog":
                key = "security_event_message.{engine}.{action}"
                return self._format_msg(
                    engine,
                    key,
                    {"engine": engine, "action": action},
                    [
                        details.get("systemDataEventId", ""),
                        details.get("systemDataProviderName", ""),
                        details.get("description", ""),
                    ],
                )
            case "activityMonitor":
                activity_monitor_action = str(details.get("alertType", "")).rpartition(
                    "."
                )
                activity_monitor_action_value = (
                    activity_monitor_action[2]
                    if len(activity_monitor_action) == 3
                    else ""
                )
                key = "security_event_message.{engine}.{activity_monitor_action_value}"
                return self._format_msg(
                    engine,
                    key,
                    {
                        "engine": engine,
                        "activity_monitor_action_value": activity_monitor_action_value,
                    },
                    [details.get("affectedSharedFolders", "")],
                )
            case "xFence":
                key = "security_event_message.{engine}.{operation}"
                operation = details.get("operation", "")
                return self._format_msg(
                    engine,
                    key,
                    {"engine": engine, "operation": operation},
                    [details.get("targetPath", "")],
                )
            case "emailScan":
                key = "security_event_message.{engine}"
                category = self.config.get(
                    "category", f"category.{details.get('category', '')}"
                )
                return self._format_msg(
                    engine,
                    key,
                    {"engine": engine},
                    [
                        category,
                        details.get("userPrincipalName", ""),
                        str(details.get("itemSubject", ""))[:50],
                        details.get("itemParentFolderName", ""),
                        action,
                    ],
                )
            case "teamsScan" | "oneDriveScan" | "sharePointScan":
                key = "security_event_message.{engine}"
                return self._format_msg(
                    engine,
                    key,
                    {"engine": engine},
                    [
                        get_file_name(details.get("fileName", "")),
                        details.get("verdict", ""),
                        action,
                    ],
                )
            case "emailBreach":
                key = "security_event_message.{engine}"
                return self._format_msg(
                    engine,
                    key,
                    {"engine": engine},
                    [details.get("userPrincipalName", ""), action],
                )
            case "inboxRuleScan":
                key = "security_event_message.{engine}"
                return self._format_msg(
                    engine,
                    key,
                    {"engine": engine},
                    [
                        details.get("inboxRuleName", ""),
                        details.get("userPrincipalName", ""),
                    ],
                )
            case _:
                return self.config.get("generic", "security_event_message.unknown")

    def _format_msg(self, engine, key_fmt, key_args={}, msg_args=[]):
        key = key_fmt.format(**key_args)
        msg = self.config.get(engine, key)
        return msg.format(*msg_args)


def get_file_name(full_path):
    posix = PureWindowsPath(full_path).as_posix()
    return PurePosixPath(posix).name
