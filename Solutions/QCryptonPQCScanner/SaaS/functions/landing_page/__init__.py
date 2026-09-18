"""
Azure Function: SaaS Landing Page
Customer is redirected here after purchasing QCrypton PQC Scanner from Azure Marketplace.

Flow:
  1. Customer clicks 'Buy' in Azure Marketplace
  2. Microsoft redirects to this landing page with a marketplace token
  3. We resolve the token to get subscription details
  4. Customer sees their subscription info and clicks 'Activate'
  5. We provision an API key and activate the subscription with Microsoft
  6. Customer gets their API key to configure the Sentinel data connector

Partner Center configuration:
  Landing page URL: https://<your-function-app>.azurewebsites.net/api/landing
"""

import logging
import os
import azure.functions as func
from shared.marketplace_client import MarketplaceClient
from shared.api_key_manager import ApiKeyManager

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    method = req.method.upper()

    if method == "GET":
        return _handle_get(req)
    elif method == "POST":
        return _handle_post(req)
    else:
        return func.HttpResponse("Method not allowed", status_code=405)


def _handle_get(req: func.HttpRequest) -> func.HttpResponse:
    """Display the landing page with subscription details."""
    token = req.params.get("token", "")
    if not token:
        return func.HttpResponse(_error_html("No marketplace token provided."),
                                 status_code=400, mimetype="text/html")

    client = _get_marketplace_client()

    try:
        resolved = client.resolve_token(token)
    except Exception as e:
        logger.error("Failed to resolve token: %s", e)
        return func.HttpResponse(_error_html("Failed to verify your purchase. Please try again."),
                                 status_code=400, mimetype="text/html")

    subscription_name = resolved.get("subscriptionName", "")
    offer_id = resolved.get("offerId", "")
    plan_id = resolved.get("planId", "")
    quantity = resolved.get("quantity", 1)
    subscription_id = resolved.get("id", "")
    beneficiary = resolved.get("beneficiary", {})
    email = beneficiary.get("emailId", "")
    tenant_id = beneficiary.get("tenantId", "")

    html = _landing_html(
        token=token,
        subscription_id=subscription_id,
        subscription_name=subscription_name,
        offer_id=offer_id,
        plan_id=plan_id,
        quantity=quantity,
        email=email,
        tenant_id=tenant_id,
    )
    return func.HttpResponse(html, status_code=200, mimetype="text/html")


def _handle_post(req: func.HttpRequest) -> func.HttpResponse:
    """Activate the subscription and provision an API key."""
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(_error_html("Invalid request."),
                                 status_code=400, mimetype="text/html")

    token = body.get("token", "")
    client = _get_marketplace_client()

    # Re-resolve to ensure token is still valid
    try:
        resolved = client.resolve_token(token)
    except Exception as e:
        logger.error("Failed to resolve token on activation: %s", e)
        return func.HttpResponse(_error_html("Token expired. Please restart from Azure Marketplace."),
                                 status_code=400, mimetype="text/html")

    subscription_id = resolved.get("id", "")
    plan_id = resolved.get("planId", "")
    quantity = resolved.get("quantity", 1)
    beneficiary = resolved.get("beneficiary", {})
    tenant_id = beneficiary.get("tenantId", "")
    email = beneficiary.get("emailId", "")

    api_key_mgr = _get_api_key_manager()

    # Provision API key
    try:
        api_key = api_key_mgr.provision(subscription_id, plan_id, tenant_id, email)
    except Exception as e:
        logger.error("Failed to provision API key: %s", e)
        return func.HttpResponse(_error_html("Failed to provision your API key. Please contact support@qcryptonapp.com"),
                                 status_code=500, mimetype="text/html")

    # Activate subscription with Microsoft
    try:
        client.activate_subscription(subscription_id, plan_id, quantity)
    except Exception as e:
        logger.error("Failed to activate subscription: %s", e)
        return func.HttpResponse(_error_html("Failed to activate. Please contact support@qcryptonapp.com"),
                                 status_code=500, mimetype="text/html")

    html = _success_html(api_key=api_key, plan_id=plan_id, subscription_id=subscription_id)
    return func.HttpResponse(html, status_code=200, mimetype="text/html")


# ── HTML Templates ───────────────────────────────────────────

def _landing_html(token, subscription_id, subscription_name, offer_id, plan_id, quantity, email, tenant_id):
    plan_display = {"basic": "Basic", "professional": "Professional", "enterprise": "Enterprise"}.get(plan_id, plan_id)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QCrypton PQC Scanner - Activate Subscription</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 640px; margin: 60px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #0078d4, #005a9e); padding: 32px; color: #fff; }}
        .header h1 {{ font-size: 24px; font-weight: 600; }}
        .header p {{ margin-top: 8px; opacity: 0.9; font-size: 14px; }}
        .body {{ padding: 32px; }}
        .field {{ margin-bottom: 16px; }}
        .field label {{ display: block; font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
        .field .value {{ font-size: 16px; font-weight: 500; padding: 8px 12px; background: #f8f9fa; border-radius: 4px; }}
        .plan-badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: 600; }}
        .plan-basic {{ background: #e8f4fd; color: #0078d4; }}
        .plan-professional {{ background: #e8f5e9; color: #2e7d32; }}
        .plan-enterprise {{ background: #fff3e0; color: #e65100; }}
        .btn {{ display: block; width: 100%; padding: 14px; background: #0078d4; color: #fff; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 24px; }}
        .btn:hover {{ background: #005a9e; }}
        .footer {{ padding: 16px 32px; background: #f8f9fa; font-size: 12px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>QCrypton PQC Scanner</h1>
            <p>Post-Quantum Cryptography Vulnerability Scanner for Microsoft Sentinel</p>
        </div>
        <div class="body">
            <h2 style="margin-bottom: 24px;">Activate Your Subscription</h2>
            <div class="field">
                <label>Subscription</label>
                <div class="value">{subscription_name}</div>
            </div>
            <div class="field">
                <label>Plan</label>
                <div class="value"><span class="plan-badge plan-{plan_id}">{plan_display}</span></div>
            </div>
            <div class="field">
                <label>Account</label>
                <div class="value">{email}</div>
            </div>
            <div class="field">
                <label>Tenant ID</label>
                <div class="value" style="font-size: 13px; font-family: monospace;">{tenant_id}</div>
            </div>
            <button class="btn" onclick="activate()">Activate Subscription</button>
        </div>
        <div class="footer">
            By activating, you agree to <a href="https://www.qcrypton.com/terms">QCrypton Terms of Service</a>.
            Need help? <a href="mailto:support@qcryptonapp.com">support@qcryptonapp.com</a>
        </div>
    </div>
    <script>
        async function activate() {{
            const btn = document.querySelector('.btn');
            btn.disabled = true;
            btn.textContent = 'Activating...';
            try {{
                const resp = await fetch(window.location.pathname, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ token: '{token}' }}),
                }});
                const html = await resp.text();
                document.documentElement.innerHTML = html;
            }} catch (e) {{
                btn.disabled = false;
                btn.textContent = 'Activate Subscription';
                alert('Activation failed. Please try again or contact support@qcryptonapp.com');
            }}
        }}
    </script>
</body>
</html>"""


def _success_html(api_key, plan_id, subscription_id):
    plan_display = {"basic": "Basic", "professional": "Professional", "enterprise": "Enterprise"}.get(plan_id, plan_id)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QCrypton PQC Scanner - Activated</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 640px; margin: 60px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #2e7d32, #1b5e20); padding: 32px; color: #fff; }}
        .header h1 {{ font-size: 24px; font-weight: 600; }}
        .body {{ padding: 32px; }}
        .api-key-box {{ background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 6px; font-family: 'Cascadia Code', 'Fira Code', monospace; font-size: 14px; word-break: break-all; margin: 16px 0; position: relative; }}
        .copy-btn {{ position: absolute; top: 8px; right: 8px; background: #333; color: #fff; border: none; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }}
        .copy-btn:hover {{ background: #555; }}
        .steps {{ margin-top: 24px; }}
        .steps h3 {{ margin-bottom: 12px; }}
        .steps ol {{ padding-left: 20px; }}
        .steps li {{ margin-bottom: 12px; line-height: 1.5; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px; padding: 12px 16px; margin-top: 20px; font-size: 14px; }}
        .footer {{ padding: 16px 32px; background: #f8f9fa; font-size: 12px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Subscription Activated</h1>
            <p>QCrypton PQC Scanner - {plan_display} Plan</p>
        </div>
        <div class="body">
            <p>Your QCrypton PQC Scanner subscription is now active. Use the API key below to configure the Sentinel data connector.</p>
            <h3 style="margin-top: 20px;">Your API Key</h3>
            <div class="api-key-box">
                <span id="apikey">{api_key}</span>
                <button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('apikey').textContent).then(()=>this.textContent='Copied!')">Copy</button>
            </div>
            <div class="warning">
                Save this API key now. For security, it will not be shown again.
            </div>
            <div class="steps">
                <h3>Next Steps</h3>
                <ol>
                    <li>Go to <strong>Microsoft Sentinel &gt; Content Hub</strong></li>
                    <li>Search for <strong>QCrypton PQC Scanner</strong> and install the solution</li>
                    <li>Navigate to <strong>Data Connectors</strong> and open QCrypton PQC Scanner</li>
                    <li>Paste the API key above into the <strong>QCrypton API Key</strong> field</li>
                    <li>Set the API Server URL to <strong>https://api.qcrypton.com</strong></li>
                    <li>Click <strong>Connect</strong> to start ingesting PQC findings</li>
                </ol>
            </div>
        </div>
        <div class="footer">
            Need help? <a href="mailto:support@qcryptonapp.com">support@qcryptonapp.com</a> |
            <a href="https://www.qcrypton.com/docs">Documentation</a>
        </div>
    </div>
</body>
</html>"""


def _error_html(message):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>QCrypton - Error</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f5f5f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; }}
        .card {{ background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); padding: 40px; max-width: 480px; text-align: center; }}
        .card h2 {{ color: #d32f2f; margin-bottom: 16px; }}
        .card p {{ color: #666; line-height: 1.6; }}
        .card a {{ color: #0078d4; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>Something went wrong</h2>
        <p>{message}</p>
        <p style="margin-top: 16px;">Contact <a href="mailto:support@qcryptonapp.com">support@qcryptonapp.com</a> for assistance.</p>
    </div>
</body>
</html>"""


# ── Initialization ───────────────────────────────────────────

def _get_marketplace_client() -> MarketplaceClient:
    return MarketplaceClient(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )


def _get_api_key_manager() -> ApiKeyManager:
    return ApiKeyManager(keyvault_url=os.environ["KEYVAULT_URL"])
