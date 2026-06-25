import requests
import hashlib
import subprocess
import sqlite3
import os
import re
from flask import Flask, request, jsonify
from urllib.parse import urlparse
import html

app = Flask(__name__)


# FIX: Construct URL internally using only user-provided path parameter, not full URL
ALLOWED_ENDPOINTS = {
    "users": "https://api.example.com/users",
    "data": "https://api.example.com/data",
    "status": "https://api.example.com/status",
}


@app.route("/fetch")
def fetch_data():
    endpoint = request.args.get("endpoint")
    if endpoint not in ALLOWED_ENDPOINTS:
        return "Endpoint not allowed", 403
    url = ALLOWED_ENDPOINTS[endpoint]
    response = requests.get(url, verify=True, timeout=30)
    sanitized = html.escape(response.text)
    return sanitized, 200, {"Content-Type": "text/plain"}


# FIX: Use parameterized arguments instead of shell=True
@app.route("/ping")
def ping_host():
    host = request.args.get("host")
    valid_host_pattern = re.compile(r"^[a-zA-Z0-9.-]+$")
    if not host or not valid_host_pattern.match(host):
        return "Invalid host", 400
    result = subprocess.run(["ping", "-c", "4", host], capture_output=True)
    return result.stdout.decode()


# FIX: Use parameterized query
@app.route("/user")
def get_user():
    user_id = request.args.get("id")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return str(cursor.fetchall())


# FIX: Use SHA-256 instead of MD5
@app.route("/hash")
def hash_data():
    data = request.args.get("data")
    result = hashlib.sha256(data.encode()).hexdigest()
    return result


# FIX: Load credentials from environment variables
@app.route("/connect")
def connect_service():
    api_key = os.environ.get("API_KEY")
    if not api_key:
        return "API key not configured", 500
    response = requests.post(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer " + api_key},
        verify=True,
        timeout=30,
    )
    return jsonify({"status": response.status_code})


# FIX: Do not log sensitive data
@app.route("/login")
def login():
    password = request.args.get("password")
    if not password:
        return "Password required", 400
    print("User login attempt received")
    return "OK"


if __name__ == "__main__":
    app.run(debug=False)
