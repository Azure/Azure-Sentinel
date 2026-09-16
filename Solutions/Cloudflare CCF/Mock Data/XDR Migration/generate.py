from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def event(
    marker: str,
    ip: str,
    *,
    method: str = "GET",
    path: str = "/home",
    uri: str | None = None,
    user_agent: str = "Cloudflare-Parity-Benign",
    country: str = "US",
    ip_class: str = "clean",
    request_bytes: int = 1,
    response_bytes: int = 1,
    status: int = 200,
    security_action: str = "",
    security_rule_id: str = "",
    security_rule_description: str = "",
) -> dict[str, Any]:
    return {
        "ClientIP": ip,
        "ClientIPClass": ip_class,
        "ClientCountry": country,
        "ClientRequestMethod": method,
        "ClientRequestHost": "cloudflare-parity.example.test",
        "ClientRequestPath": path,
        "ClientRequestURI": uri or path,
        "ClientRequestUserAgent": user_agent,
        "ClientRequestBytes": request_bytes,
        "EdgeResponseBytes": response_bytes,
        "OriginResponseStatus": status,
        "RayID": marker,
        "SecurityAction": security_action,
        "SecurityRuleID": security_rule_id,
        "SecurityRuleDescription": security_rule_description,
    }


def write(name: str, records: list[dict[str, Any]]) -> None:
    (ROOT / name).write_text(
        json.dumps(records, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    write(
        "BadClientIp.json",
        [
            event(
                "cf-bad-ip-malicious",
                "192.0.2.11",
                ip_class="badHost",
                path="/bad-ip",
            ),
            event("cf-bad-ip-benign", "198.51.100.11", path="/bad-ip-control"),
        ],
    )
    write(
        "ClientRequestFromBlockedCountry.json",
        [
            event(
                "cf-country-malicious",
                "192.0.2.12",
                country="CN",
                path="/blocked-country",
            ),
            event(
                "cf-country-benign",
                "198.51.100.12",
                country="US",
                path="/allowed-country",
            ),
        ],
    )
    write(
        "EmptyUserAgent.json",
        [
            event(
                "cf-empty-ua-malicious",
                "192.0.2.13",
                user_agent="",
                path="/empty-user-agent",
            ),
            event(
                "cf-empty-ua-benign",
                "198.51.100.13",
                user_agent="Cloudflare-Parity-Control",
                path="/present-user-agent",
            ),
        ],
    )

    multiple_errors = [
        event(
            f"cf-errors-malicious-{index:03d}",
            "192.0.2.14",
            path=f"/error-burst/{index:03d}",
        )
        for index in range(101)
    ]
    multiple_errors.extend(
        event(
            f"cf-errors-benign-{index:03d}",
            "198.51.100.14",
            path=f"/error-boundary/{index:03d}",
        )
        for index in range(100)
    )
    write("MultipleErrorsSingleSource.json", multiple_errors)

    multiple_agents = [
        event(
            f"cf-user-agents-malicious-{index:02d}",
            "192.0.2.15",
            user_agent=f"Cloudflare-Parity-Agent-{index:02d}",
            path="/user-agent-burst",
        )
        for index in range(11)
    ]
    multiple_agents.extend(
        event(
            f"cf-user-agents-benign-{index:02d}",
            "198.51.100.15",
            user_agent=f"Cloudflare-Parity-Control-{index:02d}",
            path="/user-agent-boundary",
        )
        for index in range(10)
    )
    write("MultipleUserAgentsSingleSource.json", multiple_agents)

    write(
        "UnexpectedClientRequest.json",
        [
            event(
                "cf-client-request-malicious",
                "192.0.2.16",
                path="/admin",
            ),
            event(
                "cf-client-request-benign",
                "198.51.100.16",
                path="/home",
            ),
        ],
    )
    write(
        "UnexpectedPostRequests.json",
        [
            event(
                "cf-post-malicious",
                "192.0.2.17",
                method="POST",
                path="/upload/avatar.jpg",
            ),
            event(
                "cf-post-benign",
                "198.51.100.17",
                method="POST",
                path="/upload/avatar.html",
            ),
        ],
    )
    write(
        "UnexpectedURI.json",
        [
            event(
                "cf-uri-malicious",
                "192.0.2.18",
                path="/proxy",
                uri="/proxy?target=http://10.20.30.40/admin",
            ),
            event(
                "cf-uri-benign",
                "198.51.100.18",
                path="/proxy",
                uri="/proxy?target=https://public.example.test/",
            ),
        ],
    )
    write(
        "WAFAllowedThreat.json",
        [
            event(
                "cf-waf-malicious",
                "192.0.2.19",
                path="/waf-allowed",
                security_action="Allow",
                security_rule_id="cf-parity-rule-1001",
                security_rule_description="Synthetic SQL injection signature",
            ),
            event(
                "cf-waf-benign",
                "198.51.100.19",
                path="/waf-blocked-control",
                security_action="Block",
                security_rule_id="cf-parity-rule-1001",
                security_rule_description="Synthetic blocked control",
            ),
        ],
    )
    write(
        "XSSProbingPattern.json",
        [
            event(
                "cf-xss-malicious",
                "192.0.2.20",
                method="POST",
                path="/search",
                uri="/search?q=alert%28document.domain%29",
                user_agent="Cloudflare-Parity-XSS",
            ),
            event(
                "cf-xss-benign",
                "198.51.100.20",
                path="/health",
                user_agent="Cloudflare-Parity-Control",
            ),
        ],
    )

    manifest = {
        "schemaVersion": "1.0",
        "stream": "Custom-Cloudflare",
        "expectedResultCountPerPlatform": 1,
        "rules": [
            {
                "sourceFile": "CloudflareCCFBadClientIp.yaml",
                "mockFile": "BadClientIp.json",
                "matchKey": {"SrcIpAddr": "192.0.2.11"},
            },
            {
                "sourceFile": "CloudflareCCFUnexpectedCountry.yaml",
                "mockFile": "ClientRequestFromBlockedCountry.json",
                "matchKey": {"SrcIpAddr": "192.0.2.12"},
            },
            {
                "sourceFile": "CloudflareCCFEmptyUA.yaml",
                "mockFile": "EmptyUserAgent.json",
                "matchKey": {"SrcIpAddr": "192.0.2.13"},
            },
            {
                "sourceFile": "CloudflareCCFMultipleErrorsSource.yaml",
                "mockFile": "MultipleErrorsSingleSource.json",
                "matchKey": {"SrcIpAddr": "192.0.2.14"},
            },
            {
                "sourceFile": "CloudflareCCFMultipleUAs.yaml",
                "mockFile": "MultipleUserAgentsSingleSource.json",
                "matchKey": {"SrcIpAddr": "192.0.2.15"},
            },
            {
                "sourceFile": "CloudflareCCFUnexpectedRequest.yaml",
                "mockFile": "UnexpectedClientRequest.json",
                "matchKey": {"SrcIpAddr": "192.0.2.16"},
            },
            {
                "sourceFile": "CloudflareCCFUnexpectedPost.yaml",
                "mockFile": "UnexpectedPostRequests.json",
                "matchKey": {"SrcIpAddr": "192.0.2.17"},
            },
            {
                "sourceFile": "CloudflareCCFUnexpectedUrl.yaml",
                "mockFile": "UnexpectedURI.json",
                "matchKey": {"SrcIpAddr": "192.0.2.18"},
            },
            {
                "sourceFile": "CloudflareCCFWafThreatAllowed.yaml",
                "mockFile": "WAFAllowedThreat.json",
                "matchKey": {
                    "SrcIpAddr": "192.0.2.19",
                    "CompleteUrl": "cloudflare-parity.example.test/waf-allowed",
                },
            },
            {
                "sourceFile": "CloudflareCCFXSSProbingPattern.yaml",
                "mockFile": "XSSProbingPattern.json",
                "matchKey": {
                    "SrcIpAddr": "192.0.2.20",
                    "CompleteUrl": "cloudflare-parity.example.test/search",
                },
            },
        ],
    }
    (ROOT / "validation-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
