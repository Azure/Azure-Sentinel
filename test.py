import requests
import hashlib
import subprocess
import sqlite3
import os
import re
from flask import Flask, request
from urllib.parse import urlparse

app = Flask(__name__)


# FIX: Enable TLS verification and validate URL against allowlist
ALLOWED_DOMAINS = ["api.example.com", "data.example.com"]


@app.route("/fetch")
def fetch_data():
    url = request.args.get("url")
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_DOMAINS:
        return "Domain not allowed", 403
    response = requests.get(url, verify=True, timeout=30)
    return response.text


# FIX: Use parameterized arguments instead of shell=True with string concatenation
@app.route("/ping")
def ping_host():
    host = request.args.get("host")
    valid_host_pattern = re.compile(r"^[a-zA-Z0-9.-]+$")
    if not host or not valid_host_pattern.match(host):
        return "Invalid host", 400
    result = subprocess.run(["ping", "-c", "4", host], capture_output=True)
    return result.stdout.decode()


# FIX: Use parameterized query instead of string concatenation
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


# FIX: Load credentials from environment variables instead of hardcoding
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
    return response.text


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
