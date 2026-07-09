"""
Network Log API – Azure Function App
Mock data source for Microsoft Sentinel CCF (Codeless Connector Framework) testing.

Endpoints:
    GET  /api/GetNetworkLogs  – Returns paginated network activity log records (API key required)
    POST /api/RefreshData     – Triggers a data refresh job (API key required)

Authentication:
    All endpoints require the header: X-API-Key: <key>
    The key is stored in the NETWORK_LOG_API_KEY application setting.

Pagination:
    Offset-based paging via ?page=<n>&pageSize=<n> (default pageSize=5, max=100).
    The response body includes metadata.nextLink for forward navigation.

Incremental pull:
    Optionally supply ?since=<ISO-8601-timestamp> to receive only records
    whose timestamp is >= that value.

Application Settings (configured automatically by the ARM template):
    NETWORK_LOG_API_KEY  – API key required in the X-API-Key request header
"""

import hmac
import json
import logging
import os
import uuid
from datetime import datetime, timezone, timedelta

import azure.functions as func

# ---------------------------------------------------------------------------
# App and configuration
# ---------------------------------------------------------------------------
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

NETWORK_LOG_API_KEY = os.environ.get("NETWORK_LOG_API_KEY", "")
DEFAULT_PAGE_SIZE   = 5
MAX_PAGE_SIZE       = 100
TOTAL_RECORDS       = 50


# ---------------------------------------------------------------------------
# Static base record definitions – 50 network activity entries
# Each record has stable values; timestamps are generated dynamically
# relative to the current call time so data always appears "recent".
# ---------------------------------------------------------------------------
_BASE_RECORDS = [
    # ---- Outbound web / HTTPS (LOW severity, ALLOW) ----------------------
    {"idx":  0, "sourceIp": "10.0.1.15",      "destinationIp": "151.101.1.140",  "sourcePort": 52341, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 1240,    "bytesOut": 87654,   "packets": 62,   "durationMs": 345,    "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowHTTPS",           "severity": "Low",      "category": "Web",            "threatIndicator": None,               "geoCountry": "US"},
    {"idx":  1, "sourceIp": "10.0.1.22",      "destinationIp": "93.184.216.34",   "sourcePort": 49201, "destinationPort": 80,   "protocol": "TCP",  "action": "ALLOW", "bytesIn": 540,     "bytesOut": 12480,   "packets": 14,   "durationMs": 112,    "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowHTTP",            "severity": "Low",      "category": "Web",            "threatIndicator": None,               "geoCountry": "US"},
    {"idx":  2, "sourceIp": "10.0.2.44",      "destinationIp": "17.253.144.10",   "sourcePort": 61200, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 2100,    "bytesOut": 45890,   "packets": 38,   "durationMs": 290,    "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowHTTPS",           "severity": "Low",      "category": "Web",            "threatIndicator": None,               "geoCountry": "US"},
    {"idx":  3, "sourceIp": "10.0.3.88",      "destinationIp": "216.58.203.110",  "sourcePort": 55801, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 980,     "bytesOut": 24300,   "packets": 22,   "durationMs": 180,    "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowHTTPS",           "severity": "Low",      "category": "Web",            "threatIndicator": None,               "geoCountry": "US"},
    # ---- DNS (LOW severity, ALLOW / UDP) ---------------------------------
    {"idx":  4, "sourceIp": "10.0.1.15",      "destinationIp": "10.0.0.2",        "sourcePort": 45123, "destinationPort": 53,   "protocol": "UDP",  "action": "ALLOW", "bytesIn": 64,      "bytesOut": 128,     "packets": 2,    "durationMs": 5,      "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowDNS",             "severity": "Low",      "category": "DNS",            "threatIndicator": None,               "geoCountry": None},
    {"idx":  5, "sourceIp": "10.0.2.30",      "destinationIp": "8.8.8.8",         "sourcePort": 34512, "destinationPort": 53,   "protocol": "UDP",  "action": "ALLOW", "bytesIn": 72,      "bytesOut": 156,     "packets": 2,    "durationMs": 8,      "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowDNS",             "severity": "Low",      "category": "DNS",            "threatIndicator": None,               "geoCountry": "US"},
    {"idx":  6, "sourceIp": "10.0.4.100",     "destinationIp": "1.1.1.1",         "sourcePort": 51000, "destinationPort": 53,   "protocol": "UDP",  "action": "ALLOW", "bytesIn": 80,      "bytesOut": 200,     "packets": 4,    "durationMs": 12,     "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowDNS",             "severity": "Low",      "category": "DNS",            "threatIndicator": None,               "geoCountry": "US"},
    {"idx":  7, "sourceIp": "10.0.1.50",      "destinationIp": "8.8.4.4",         "sourcePort": 62001, "destinationPort": 53,   "protocol": "UDP",  "action": "ALLOW", "bytesIn": 88,      "bytesOut": 312,     "packets": 6,    "durationMs": 15,     "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowDNS",             "severity": "Low",      "category": "DNS",            "threatIndicator": None,               "geoCountry": "US"},
    # ---- SSH – blocked external brute-force (HIGH severity, DENY) --------
    {"idx":  8, "sourceIp": "185.220.101.45", "destinationIp": "10.0.10.5",       "sourcePort": 44312, "destinationPort": 22,   "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 3,    "durationMs": 0,      "networkZone": "external", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockSSHExternal",     "severity": "High",     "category": "SSH",            "threatIndicator": "KnownScanner",     "geoCountry": "RU"},
    {"idx":  9, "sourceIp": "10.0.5.12",      "destinationIp": "10.0.10.5",       "sourcePort": 55901, "destinationPort": 22,   "protocol": "TCP",  "action": "ALLOW", "bytesIn": 4200,    "bytesOut": 8900,    "packets": 44,   "durationMs": 12000,  "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowSSHInternal",     "severity": "Medium",   "category": "SSH",            "threatIndicator": None,               "geoCountry": None},
    {"idx": 10, "sourceIp": "92.118.160.22",  "destinationIp": "10.0.10.8",       "sourcePort": 41234, "destinationPort": 22,   "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 2,    "durationMs": 0,      "networkZone": "external", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockSSHExternal",     "severity": "High",     "category": "SSH",            "threatIndicator": "BruteForce",       "geoCountry": "CN"},
    {"idx": 11, "sourceIp": "104.21.5.89",    "destinationIp": "10.0.10.5",       "sourcePort": 49523, "destinationPort": 22,   "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 1,    "durationMs": 0,      "networkZone": "external", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "BlockSSHExternal",     "severity": "High",     "category": "SSH",            "threatIndicator": "KnownThreat",      "geoCountry": "NL"},
    # ---- RDP – blocked external / allowed internal (CRITICAL / MEDIUM) ---
    {"idx": 12, "sourceIp": "194.165.16.76",  "destinationIp": "10.0.20.15",      "sourcePort": 61200, "destinationPort": 3389, "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 5,    "durationMs": 0,      "networkZone": "external", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockRDPExternal",     "severity": "Critical", "category": "RDP",            "threatIndicator": "RDPBruteForce",    "geoCountry": "RU"},
    {"idx": 13, "sourceIp": "45.142.212.100", "destinationIp": "10.0.20.20",      "sourcePort": 52312, "destinationPort": 3389, "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 8,    "durationMs": 0,      "networkZone": "external", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockRDPExternal",     "severity": "Critical", "category": "RDP",            "threatIndicator": "RDPBruteForce",    "geoCountry": "DE"},
    {"idx": 14, "sourceIp": "10.0.5.12",      "destinationIp": "10.0.20.15",      "sourcePort": 54100, "destinationPort": 3389, "protocol": "TCP",  "action": "ALLOW", "bytesIn": 124560,  "bytesOut": 45320,   "packets": 892,  "durationMs": 180000, "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowRDPInternal",     "severity": "Medium",   "category": "RDP",            "threatIndicator": None,               "geoCountry": None},
    {"idx": 15, "sourceIp": "78.128.113.220", "destinationIp": "10.0.20.25",      "sourcePort": 48900, "destinationPort": 3389, "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 3,    "durationMs": 0,      "networkZone": "external", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "BlockRDPExternal",     "severity": "Critical", "category": "RDP",            "threatIndicator": "RDPBruteForce",    "geoCountry": "PL"},
    # ---- Email / SMTP ----------------------------------------------------
    {"idx": 16, "sourceIp": "10.0.1.80",      "destinationIp": "74.125.28.108",   "sourcePort": 45670, "destinationPort": 587,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 2300,    "bytesOut": 52100,   "packets": 45,   "durationMs": 2100,   "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowSMTPSubmission",  "severity": "Low",      "category": "Email",          "threatIndicator": None,               "geoCountry": "US"},
    {"idx": 17, "sourceIp": "10.0.1.81",      "destinationIp": "40.107.92.85",    "sourcePort": 48212, "destinationPort": 25,   "protocol": "TCP",  "action": "ALLOW", "bytesIn": 1800,    "bytesOut": 38400,   "packets": 32,   "durationMs": 1850,   "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowSMTP",            "severity": "Low",      "category": "Email",          "threatIndicator": None,               "geoCountry": "US"},
    {"idx": 18, "sourceIp": "192.168.1.5",    "destinationIp": "10.0.1.80",       "sourcePort": 55320, "destinationPort": 25,   "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 2,    "durationMs": 0,      "networkZone": "dmz",      "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "BlockSMTPInbound",     "severity": "Medium",   "category": "Email",          "threatIndicator": "SpamSource",       "geoCountry": None},
    {"idx": 19, "sourceIp": "10.0.1.82",      "destinationIp": "13.107.4.50",     "sourcePort": 61400, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 3200,    "bytesOut": 68900,   "packets": 58,   "durationMs": 2400,   "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowO365HTTPS",       "severity": "Low",      "category": "Email",          "threatIndicator": None,               "geoCountry": "US"},
    # ---- Large data transfers / potential exfiltration -------------------
    {"idx": 20, "sourceIp": "10.0.3.45",      "destinationIp": "52.239.162.100",  "sourcePort": 52500, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 1240,    "bytesOut": 4562000, "packets": 3200, "durationMs": 45000,  "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowHTTPS",           "severity": "Medium",   "category": "CloudStorage",   "threatIndicator": None,               "geoCountry": "US"},
    {"idx": 21, "sourceIp": "10.0.3.46",      "destinationIp": "185.199.108.153", "sourcePort": 49812, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 980,     "bytesOut": 8920000, "packets": 6234, "durationMs": 92000,  "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowHTTPS",           "severity": "High",     "category": "CloudStorage",   "threatIndicator": "LargeUpload",      "geoCountry": "US"},
    {"idx": 22, "sourceIp": "10.0.5.200",     "destinationIp": "45.33.32.156",    "sourcePort": 54321, "destinationPort": 443,  "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 1,    "durationMs": 0,      "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "BlockThreatFeed",      "severity": "Critical", "category": "Malware",        "threatIndicator": "C2Server",         "geoCountry": "US"},
    {"idx": 23, "sourceIp": "10.0.2.77",      "destinationIp": "198.51.100.10",   "sourcePort": 57891, "destinationPort": 4444, "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 2,    "durationMs": 0,      "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockThreatFeed",      "severity": "Critical", "category": "Malware",        "threatIndicator": "C2Server",         "geoCountry": "US"},
    {"idx": 24, "sourceIp": "10.0.4.33",      "destinationIp": "52.168.138.145",  "sourcePort": 60123, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 2400,    "bytesOut": 3120000, "packets": 2189, "durationMs": 61000,  "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowHTTPS",           "severity": "Medium",   "category": "CloudStorage",   "threatIndicator": None,               "geoCountry": "US"},
    # ---- Database traffic (internal) -------------------------------------
    {"idx": 25, "sourceIp": "10.0.6.10",      "destinationIp": "10.0.7.20",       "sourcePort": 55000, "destinationPort": 1433, "protocol": "TCP",  "action": "ALLOW", "bytesIn": 45000,   "bytesOut": 320000,  "packets": 289,  "durationMs": 8900,   "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowSQLInternal",     "severity": "Low",      "category": "Database",       "threatIndicator": None,               "geoCountry": None},
    {"idx": 26, "sourceIp": "10.0.6.11",      "destinationIp": "10.0.7.20",       "sourcePort": 56001, "destinationPort": 1433, "protocol": "TCP",  "action": "ALLOW", "bytesIn": 38000,   "bytesOut": 290000,  "packets": 234,  "durationMs": 7200,   "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowSQLInternal",     "severity": "Low",      "category": "Database",       "threatIndicator": None,               "geoCountry": None},
    {"idx": 27, "sourceIp": "10.0.99.5",      "destinationIp": "10.0.7.20",       "sourcePort": 43219, "destinationPort": 1433, "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 4,    "durationMs": 0,      "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "BlockUnauthorizedDB",  "severity": "High",     "category": "Database",       "threatIndicator": "UnauthorizedAccess","geoCountry": None},
    {"idx": 28, "sourceIp": "10.0.6.12",      "destinationIp": "10.0.7.21",       "sourcePort": 57212, "destinationPort": 5432, "protocol": "TCP",  "action": "ALLOW", "bytesIn": 29000,   "bytesOut": 180000,  "packets": 156,  "durationMs": 5400,   "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowPostgresInternal","severity": "Low",      "category": "Database",       "threatIndicator": None,               "geoCountry": None},
    {"idx": 29, "sourceIp": "10.0.6.13",      "destinationIp": "10.0.7.22",       "sourcePort": 58100, "destinationPort": 27017,"protocol": "TCP",  "action": "ALLOW", "bytesIn": 12000,   "bytesOut": 98000,   "packets": 88,   "durationMs": 3200,   "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowMongoInternal",   "severity": "Low",      "category": "Database",       "threatIndicator": None,               "geoCountry": None},
    # ---- ICMP / port scan / recon ----------------------------------------
    {"idx": 30, "sourceIp": "10.0.1.1",       "destinationIp": "10.0.2.1",        "sourcePort": 0,     "destinationPort": 0,    "protocol": "ICMP", "action": "ALLOW", "bytesIn": 64,      "bytesOut": 64,      "packets": 4,    "durationMs": 3,      "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowICMPInternal",    "severity": "Low",      "category": "NetworkOps",     "threatIndicator": None,               "geoCountry": None},
    {"idx": 31, "sourceIp": "10.0.1.1",       "destinationIp": "10.0.3.1",        "sourcePort": 0,     "destinationPort": 0,    "protocol": "ICMP", "action": "ALLOW", "bytesIn": 64,      "bytesOut": 64,      "packets": 4,    "durationMs": 4,      "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowICMPInternal",    "severity": "Low",      "category": "NetworkOps",     "threatIndicator": None,               "geoCountry": None},
    {"idx": 32, "sourceIp": "203.0.113.25",   "destinationIp": "10.0.0.1",        "sourcePort": 0,     "destinationPort": 0,    "protocol": "ICMP", "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 1,    "durationMs": 0,      "networkZone": "external", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockICMPExternal",    "severity": "Low",      "category": "NetworkOps",     "threatIndicator": None,               "geoCountry": "AU"},
    {"idx": 33, "sourceIp": "77.88.55.80",    "destinationIp": "10.0.0.0",        "sourcePort": 12345, "destinationPort": 0,    "protocol": "ICMP", "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 128,  "durationMs": 0,      "networkZone": "external", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "BlockPortScan",        "severity": "High",     "category": "Recon",          "threatIndicator": "PortScan",         "geoCountry": "RU"},
    {"idx": 34, "sourceIp": "45.155.205.233", "destinationIp": "10.0.0.0",        "sourcePort": 54321, "destinationPort": 445,  "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 256,  "durationMs": 0,      "networkZone": "external", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockSMBExternal",     "severity": "Critical", "category": "Recon",          "threatIndicator": "SMBScan",          "geoCountry": "BY"},
    # ---- VPN / DMZ traffic -----------------------------------------------
    {"idx": 35, "sourceIp": "10.10.0.5",      "destinationIp": "10.0.8.100",      "sourcePort": 51200, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 8900,    "bytesOut": 24500,   "packets": 78,   "durationMs": 1200,   "networkZone": "dmz",      "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowVPNTraffic",      "severity": "Low",      "category": "VPN",            "threatIndicator": None,               "geoCountry": None},
    {"idx": 36, "sourceIp": "10.10.0.12",     "destinationIp": "10.0.8.101",      "sourcePort": 52300, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 12400,   "bytesOut": 38900,   "packets": 124,  "durationMs": 2100,   "networkZone": "dmz",      "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowVPNTraffic",      "severity": "Low",      "category": "VPN",            "threatIndicator": None,               "geoCountry": None},
    {"idx": 37, "sourceIp": "10.10.0.33",     "destinationIp": "10.0.5.0",        "sourcePort": 500,   "destinationPort": 500,  "protocol": "UDP",  "action": "ALLOW", "bytesIn": 1200,    "bytesOut": 1200,    "packets": 12,   "durationMs": 450,    "networkZone": "dmz",      "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowIKEVPN",          "severity": "Low",      "category": "VPN",            "threatIndicator": None,               "geoCountry": None},
    {"idx": 38, "sourceIp": "10.10.1.20",     "destinationIp": "10.0.8.100",      "sourcePort": 53400, "destinationPort": 4500, "protocol": "UDP",  "action": "ALLOW", "bytesIn": 2400,    "bytesOut": 4800,    "packets": 48,   "durationMs": 890,    "networkZone": "dmz",      "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowNATT",            "severity": "Low",      "category": "VPN",            "threatIndicator": None,               "geoCountry": None},
    {"idx": 39, "sourceIp": "172.16.0.5",     "destinationIp": "10.0.8.100",      "sourcePort": 55600, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 18000,   "bytesOut": 42000,   "packets": 234,  "durationMs": 3400,   "networkZone": "dmz",      "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowVPNTraffic",      "severity": "Low",      "category": "VPN",            "threatIndicator": None,               "geoCountry": None},
    # ---- NTP / SNMP / network monitoring ---------------------------------
    {"idx": 40, "sourceIp": "10.0.1.1",       "destinationIp": "129.6.15.28",     "sourcePort": 61234, "destinationPort": 123,  "protocol": "UDP",  "action": "ALLOW", "bytesIn": 48,      "bytesOut": 48,      "packets": 2,    "durationMs": 12,     "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowNTP",             "severity": "Low",      "category": "NetworkOps",     "threatIndicator": None,               "geoCountry": "US"},
    {"idx": 41, "sourceIp": "10.0.1.2",       "destinationIp": "216.239.35.0",    "sourcePort": 51200, "destinationPort": 123,  "protocol": "UDP",  "action": "ALLOW", "bytesIn": 48,      "bytesOut": 48,      "packets": 2,    "durationMs": 8,      "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowNTP",             "severity": "Low",      "category": "NetworkOps",     "threatIndicator": None,               "geoCountry": "US"},
    {"idx": 42, "sourceIp": "10.0.20.1",      "destinationIp": "10.0.8.50",       "sourcePort": 62000, "destinationPort": 161,  "protocol": "UDP",  "action": "ALLOW", "bytesIn": 200,     "bytesOut": 1200,    "packets": 14,   "durationMs": 45,     "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowSNMPInternal",    "severity": "Low",      "category": "NetworkOps",     "threatIndicator": None,               "geoCountry": None},
    {"idx": 43, "sourceIp": "198.18.0.22",    "destinationIp": "10.0.20.1",       "sourcePort": 45000, "destinationPort": 161,  "protocol": "UDP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 8,    "durationMs": 0,      "networkZone": "external", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockSNMPExternal",    "severity": "Medium",   "category": "NetworkOps",     "threatIndicator": "ExternalSNMP",     "geoCountry": "US"},
    {"idx": 44, "sourceIp": "10.0.20.2",      "destinationIp": "10.0.8.50",       "sourcePort": 63000, "destinationPort": 162,  "protocol": "UDP",  "action": "ALLOW", "bytesIn": 150,     "bytesOut": 900,     "packets": 10,   "durationMs": 38,     "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowSNMPTrapInt",     "severity": "Low",      "category": "NetworkOps",     "threatIndicator": None,               "geoCountry": None},
    # ---- Lateral movement / anomalous ------------------------------------
    {"idx": 45, "sourceIp": "10.0.3.50",      "destinationIp": "10.0.7.20",       "sourcePort": 45678, "destinationPort": 445,  "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 12,   "durationMs": 0,      "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockSMBLateral",      "severity": "High",     "category": "LateralMovement","threatIndicator": "WannaCry",         "geoCountry": None},
    {"idx": 46, "sourceIp": "10.0.4.88",      "destinationIp": "10.0.1.15",       "sourcePort": 46789, "destinationPort": 445,  "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 8,    "durationMs": 0,      "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "BlockSMBLateral",      "severity": "High",     "category": "LateralMovement","threatIndicator": "SMBExploit",       "geoCountry": None},
    {"idx": 47, "sourceIp": "10.0.1.200",     "destinationIp": "10.0.9.0",        "sourcePort": 47890, "destinationPort": 8080, "protocol": "TCP",  "action": "ALLOW", "bytesIn": 3400,    "bytesOut": 12000,   "packets": 45,   "durationMs": 780,    "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "AllowWebProxy",        "severity": "Low",      "category": "Web",            "threatIndicator": None,               "geoCountry": None},
    {"idx": 48, "sourceIp": "10.0.5.77",      "destinationIp": "192.0.2.200",     "sourcePort": 48901, "destinationPort": 6667, "protocol": "TCP",  "action": "DENY",  "bytesIn": 0,       "bytesOut": 0,       "packets": 6,    "durationMs": 0,      "networkZone": "internal", "deviceId": "fw-001", "deviceName": "Firewall-Primary",    "ruleName": "BlockThreatFeed",      "severity": "Critical", "category": "Malware",        "threatIndicator": "IRCBotnet",        "geoCountry": "US"},
    {"idx": 49, "sourceIp": "10.0.2.190",     "destinationIp": "52.114.32.5",     "sourcePort": 49012, "destinationPort": 443,  "protocol": "TCP",  "action": "ALLOW", "bytesIn": 4500,    "bytesOut": 189000,  "packets": 142,  "durationMs": 5600,   "networkZone": "internal", "deviceId": "fw-002", "deviceName": "Firewall-Secondary",  "ruleName": "AllowHTTPS",           "severity": "Low",      "category": "Web",            "threatIndicator": None,               "geoCountry": "US"},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_api_key(req: func.HttpRequest) -> bool:
    """Constant-time comparison to prevent timing-based key enumeration."""
    provided = req.headers.get("X-API-Key", "")
    if not NETWORK_LOG_API_KEY or not provided:
        return False
    return hmac.compare_digest(provided.encode(), NETWORK_LOG_API_KEY.encode())


def _build_records() -> list:
    """
    Build all 50 network log records with timestamps relative to current UTC time.
    Record idx=0 is oldest (~48 h ago); idx=49 is most recent (~now).
    UUIDs are deterministic per record index so they are stable across pages.
    """
    now       = datetime.now(timezone.utc)
    base_time = now - timedelta(hours=48)
    step      = timedelta(minutes=59)   # 50 * 59 min ≈ 49.2 h total span

    records = []
    for rec in _BASE_RECORDS:
        ts = base_time + step * rec["idx"]
        records.append({
            "id":              str(uuid.uuid5(uuid.NAMESPACE_DNS, f"netlogs-{rec['idx']}")),
            "timestamp":       ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sourceIp":        rec["sourceIp"],
            "destinationIp":   rec["destinationIp"],
            "sourcePort":      rec["sourcePort"],
            "destinationPort": rec["destinationPort"],
            "protocol":        rec["protocol"],
            "action":          rec["action"],
            "bytesIn":         rec["bytesIn"],
            "bytesOut":        rec["bytesOut"],
            "packets":         rec["packets"],
            "durationMs":      rec["durationMs"],
            "networkZone":     rec["networkZone"],
            "deviceId":        rec["deviceId"],
            "deviceName":      rec["deviceName"],
            "ruleName":        rec["ruleName"],
            "severity":        rec["severity"],
            "category":        rec["category"],
            "threatIndicator": rec["threatIndicator"],
            "geoCountry":      rec["geoCountry"],
        })
    return records


def _error_response(status_code: int, message: str) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"status": "error", "code": status_code, "message": message}),
        status_code=status_code,
        mimetype="application/json",
    )


# ---------------------------------------------------------------------------
# Endpoint 1: GET /api/GetNetworkLogs
# ---------------------------------------------------------------------------

@app.route(route="GetNetworkLogs", methods=["GET"])
def get_network_logs(req: func.HttpRequest) -> func.HttpResponse:
    """
    Returns a paginated list of network activity log records.

    Query parameters:
        page      (int, default=1)  – 1-based page number
        pageSize  (int, default=5)  – Records per page (max 100)
        since     (ISO 8601 string) – Optional. Return only records with
                                      timestamp >= this value.

    Response headers:
        X-Request-ID   – Unique identifier for this request
        X-Total-Count  – Total matching record count
        X-Page         – Current page number
        X-Page-Size    – Current page size
        X-Total-Pages  – Total number of pages

    Response body (application/json):
        {
          "status":   "success",
          "metadata": {
            "totalCount":      <int>,
            "page":            <int>,
            "pageSize":        <int>,
            "totalPages":      <int>,
            "hasNextPage":     <bool>,
            "nextLink":        <string|null>,   // full URL to next page
            "hasPreviousPage": <bool>,
            "previousLink":    <string|null>    // full URL to previous page
          },
          "data": [ <NetworkLogRecord>, ... ]
        }
    """
    request_id = str(uuid.uuid4())
    logging.info("GetNetworkLogs | requestId=%s method=%s url=%s", request_id, req.method, req.url)

    if not _validate_api_key(req):
        logging.warning(
            "GetNetworkLogs | requestId=%s UNAUTHORIZED: missing or invalid X-API-Key", request_id
        )
        return _error_response(401, "Unauthorized: missing or invalid X-API-Key header")

    # -- Parse and validate query parameters --------------------------------
    try:
        page      = max(1, int(req.params.get("page", 1)))
        page_size = min(max(1, int(req.params.get("pageSize", DEFAULT_PAGE_SIZE))), MAX_PAGE_SIZE)
    except (ValueError, TypeError):
        logging.warning(
            "GetNetworkLogs | requestId=%s BAD_REQUEST: invalid pagination params page=%s pageSize=%s",
            request_id, req.params.get("page"), req.params.get("pageSize"),
        )
        return _error_response(400, "Invalid pagination parameters. 'page' and 'pageSize' must be positive integers.")

    since_str = req.params.get("since")
    since_dt  = None
    if since_str:
        try:
            since_dt = datetime.fromisoformat(since_str.replace("Z", "+00:00"))
        except ValueError:
            logging.warning(
                "GetNetworkLogs | requestId=%s BAD_REQUEST: invalid since=%s", request_id, since_str
            )
            return _error_response(400, "Invalid 'since' format. Use ISO 8601 (e.g. 2024-01-01T00:00:00Z).")

    # -- Build and filter records -------------------------------------------
    all_logs = _build_records()

    if since_dt:
        pre_filter_count = len(all_logs)
        all_logs = [
            r for r in all_logs
            if datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")) >= since_dt
        ]
        logging.info(
            "GetNetworkLogs | requestId=%s INCREMENTAL_FILTER: since=%s preFilterCount=%d postFilterCount=%d",
            request_id, since_str, pre_filter_count, len(all_logs),
        )

    total_count = len(all_logs)
    total_pages = max(1, (total_count + page_size - 1) // page_size)

    start     = (page - 1) * page_size
    page_data = all_logs[start : start + page_size]

    logging.info(
        "GetNetworkLogs | requestId=%s page=%d pageSize=%d totalCount=%d totalPages=%d returnedCount=%d hasNextPage=%s",
        request_id, page, page_size, total_count, total_pages, len(page_data), page < total_pages,
    )

    # -- Build nextLink / previousLink --------------------------------------
    base_url   = req.url.split("?")[0]
    since_qs   = f"&since={since_str}" if since_str else ""
    next_link  = f"{base_url}?page={page + 1}&pageSize={page_size}{since_qs}" if page < total_pages else None
    prev_link  = f"{base_url}?page={page - 1}&pageSize={page_size}{since_qs}" if page > 1 else None

    body = {
        "status": "success",
        "metadata": {
            "totalCount":      total_count,
            "page":            page,
            "pageSize":        page_size,
            "totalPages":      total_pages,
            "hasNextPage":     page < total_pages,
            "nextLink":        next_link,
            "hasPreviousPage": page > 1,
            "previousLink":    prev_link,
        },
        "data": page_data,
    }

    return func.HttpResponse(
        json.dumps(body, indent=2),
        status_code=200,
        mimetype="application/json",
        headers={
            "X-Request-ID":  request_id,
            "X-Total-Count": str(total_count),
            "X-Page":        str(page),
            "X-Page-Size":   str(page_size),
            "X-Total-Pages": str(total_pages),
        },
    )


# ---------------------------------------------------------------------------
# Endpoint 2: POST /api/RefreshData
# ---------------------------------------------------------------------------

@app.route(route="RefreshData", methods=["POST"])
def refresh_data(req: func.HttpRequest) -> func.HttpResponse:
    """
    Triggers a data refresh job. After calling this endpoint, the next
    call to GetNetworkLogs will return records with timestamps anchored
    to the new "now" (timestamps are always calculated relative to the
    current call time, so they naturally refresh with each invocation).

    No request body required.

    Response body (application/json):
        {
          "status":      "success",
          "message":     <string>,
          "jobId":       <UUID>,
          "refreshedAt": <ISO 8601 timestamp>,
          "recordCount": 50
        }
    """
    request_id = str(uuid.uuid4())
    logging.info("RefreshData | requestId=%s method=%s", request_id, req.method)

    if not _validate_api_key(req):
        logging.warning(
            "RefreshData | requestId=%s UNAUTHORIZED: missing or invalid X-API-Key", request_id
        )
        return _error_response(401, "Unauthorized: missing or invalid X-API-Key header")

    job_id       = str(uuid.uuid4())
    refreshed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    body = {
        "status":      "success",
        "message":     "Data refresh completed. Record timestamps have been regenerated relative to the current time.",
        "jobId":       job_id,
        "refreshedAt": refreshed_at,
        "recordCount": TOTAL_RECORDS,
    }

    logging.info(
        "RefreshData | requestId=%s jobId=%s refreshedAt=%s recordCount=%d",
        request_id, job_id, refreshed_at, TOTAL_RECORDS,
    )

    return func.HttpResponse(
        json.dumps(body, indent=2),
        status_code=200,
        mimetype="application/json",
        headers={"X-Request-ID": request_id},
    )
