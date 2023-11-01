from ..Helpers.date_helper import DateHelper


class PropertyMapper:
    @staticmethod
    def map_feeds(feeds):
        threat_indicators = {"value": []}
        for feed in feeds:
            if not all((feed["FileName"], feed["FileSize"], feed["SHA256"], feed["SendingIP"])):
                continue

            threat_indicator = {
                "action": "block",
                "severity": 5,
                "confidence": 100,
                "isActive": True,
                "tlpLevel": "red",
                "threatType": "Malware",
                "fileType": feed["FileMimeType"],
                "fileName": feed["FileName"],
                "fileSize": feed["FileSize"],
                "fileHashType": "sha256",
                "fileHashValue": feed["SHA256"],
                "fileCompileDateTime": DateHelper.convert_from_mimecast_format(feed["Timestamp"]),
                "expirationDateTime": DateHelper.get_utc_time_from_now(days=30),
                "emailSourceIpAddress": feed["SendingIP"],
                "targetProduct": "Azure Sentinel",
                "description": "Mimecast Regional Threat Intel",
            }

            threat_indicators["value"].append(threat_indicator)

        return threat_indicators
