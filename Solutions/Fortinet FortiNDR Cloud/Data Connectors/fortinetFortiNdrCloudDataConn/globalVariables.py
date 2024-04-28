SUPPORTED_EVENT_TYPES = set(['observation', 'suricata', 'detections'])

ORCHESTRATION_NAME = 'SingletonEternalOrchestrator'

AUTH_URLS = {
    "production": "auth.icebrg.io",
    "uat": "auth-uat.icebrg.io"
}

BUCKETS = {
    "production": "fortindr-cloud-metastream",
    "uat": "fortindr-cloud-metastream-uat"
}
