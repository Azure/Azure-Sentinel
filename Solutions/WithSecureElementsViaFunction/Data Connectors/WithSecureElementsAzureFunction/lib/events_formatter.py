from .message_factory import MessageFactory
import re


class Formatter:
    SEVERITY_TO_INDEX = {
        "critical": 10,
        "fatal_error": 8,
        "error": 6,
        "warning": 4,
        "info": 1,
    }
    ENGINE_TO_ACTIVITY = {
        "webTrafficScanning": "Web Traffic Scanning event",
        "webContentControl": "Web Content Control event",
        "applicationControl": "Application Control event",
        "fileScanning": "File Scanning event",
        "manualScanning": "Manual Scanning event",
        "realtimeScanning": "Real - time Scanning event",
        "deviceControl": "Device Control event",
        "deepGuard": "DeepGuard event",
        "dataGuard": "DataGuard event",
        "browsingProtection": "Browsing Protection event",
        "connectionControl": "Network connection event",
        "reputationBasedBrowsing": "Browsing Protection event",
        "integrityChecker": "Integrity Checker event",
        "tamperProtection": "Tamper Protection event",
        "firewall": "Firewall event",
        "amsi": "Antimalware Scan Interface (AMSI) event",
        "connector": "Elements Connector event",
        "setting": "Setting event",
        "edr": "Endpoint Detection and Response (EDR) event",
        "xFence": "XFENCE event",
        "systemEventsLog": "System event",
        "activityMonitor": "Server Share Protection event",
        "emailScan": "Email scanning event",
        "emailBreach": "Email breach event",
        "teamsScan": "Microsoft Teams scanning event",
        "oneDriveScan": "Microsoft OneDrive scanning event",
        "sharePointScan": "Microsoft SharePoint scanning event",
        "inboxRuleScan": "Suspicious inbox rule event",
        "activityMonitorClientProtection": "Activity Monitor Client Protection",
    }
    DEEP_GUARD_RARITY_REPUTATION_REGEX = "Rarity: (\\d+), Reputation: (\\d+)"

    def __init__(self):
        self._message_factory = MessageFactory()

    def format(self, event):
        engine = event.engine
        result = {
            "DeviceVendor": "WithSecure",
            "DeviceEventClassID": f"{engine}.{event.action}",
            "Activity": Formatter.ENGINE_TO_ACTIVITY.get(engine, engine),
            "LogSeverity": Formatter.SEVERITY_TO_INDEX.get(event.severity),
            "Message": self._message_factory.get_message(event),
            "DeviceAction": event.action,
            "SimplifiedDeviceAction": event.action,
            "PersistenceTimestamp": event.persistenceTimestamp,
        }
        details = event.details
        infected_object = Formatter.get_infection_properties(engine, event)
        if "infectedObject" in infected_object:
            result["DeviceCustomString1"] = infected_object["infectedObject"]
            result["DeviceCustomString1Label"] = "Infected object"
        if "malwareName" in infected_object:
            result["DeviceCustomString2"] = infected_object["malwareName"]
            result["DeviceCustomString2Label"] = "Malware"
        if "userName" in details:
            result["SourceUserName"] = details["userName"]

        host_name = event.host_name()
        if host_name:
            result["SourceHostName"] = host_name
        additional_extensions = dict(details)
        additional_extensions["accountName"] = event.organization["name"]
        additional_extensions_string = ";".join(
            [f"details_{k}={v}" for k, v in additional_extensions.items()]
        )
        result["AdditionalExtensions"] = additional_extensions_string
        return result

    @staticmethod
    def get_infection_properties(engine, event):
        details = event.details
        match engine:
            case "fileScanning" | "manualScanning":
                return Formatter.get_infection_object(
                    event.file_path(), event.infection_name()
                )
            case "deepGuard":
                name = details.get("name", "")
                match_result = re.findall(
                    Formatter.DEEP_GUARD_RARITY_REPUTATION_REGEX, name
                )
                if not match_result and name != "DeepGuard blocks a rare application":
                    return Formatter.get_infection_object(
                        details.get("filePath", ""), details.get("name", "")
                    )
            case "webTrafficScanning":
                if "alertType" in details:
                    return Formatter.get_infection_object(
                        details.get("url", ""),
                        event.process_name(),
                    )
                else:
                    return Formatter.get_infection_object(
                        details.get("websiteUrl", ""), event.file_name()
                    )
            case "amsi":
                return Formatter.get_infection_object(
                    details.get("path", ""), details.get("infectionName", "")
                )
            case _:
                return {}
        return {}

    @staticmethod
    def get_infection_object(path, name):
        return {"infectedObject": path, "malwareName": name}
