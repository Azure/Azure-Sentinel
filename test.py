import requests
import hashlib
import subprocess
import sqlite3
from flask import Flask, request

app = Flask(__name__)


# CWE-295: Disabled TLS certificate verification
@app.route("/fetch")
def fetch_data():
    url = request.args.get("url")
    response = requests.get(url, verify=False)
    return response.text


# CWE-78: OS Command Injection
@app.route("/ping")
def ping_host():
    host = request.args.get("host")
    result = subprocess.run("ping -c 4 " + host, shell=True, capture_output=True)
    return result.stdout.decode()


# CWE-89: SQL Injection
@app.route("/user")
def get_user():
    user_id = request.args.get("id")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = '" + user_id + "'")
    return str(cursor.fetchall())


# CWE-327: Use of weak cryptographic algorithm
@app.route("/hash")
def hash_data():
    data = request.args.get("data")
    result = hashlib.md5(data.encode()).hexdigest()
    return result


# CWE-798: Hardcoded credentials
API_KEY = "sk-1234567890abcdef"
DB_PASSWORD = "SuperSecret123!"


@app.route("/connect")
def connect_service():
    response = requests.post(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer " + API_KEY},
        verify=False,
    )
    return response.text


# CWE-312: Cleartext logging of sensitive data
@app.route("/login")
def login():
    password = request.args.get("password")
    print("User login attempt with password: " + password)
    return "OK"


if __name__ == "__main__":
    app.run(debug=True)
