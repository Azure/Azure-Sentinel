import requests
import hashlib
import subprocess
import sqlite3
import os
from flask import Flask, request, jsonify

app = Flask(__name__)


# CWE-918: Server-Side Request Forgery (SSRF) - fetching arbitrary user-supplied URL
@app.route("/fetch")
def fetch_data():
    url = request.args.get("url")
    response = requests.get(url)
    return response.text


# CWE-78: OS Command Injection - using shell=True with unsanitized input
@app.route("/ping")
def ping_host():
    host = request.args.get("host")
    result = subprocess.run("ping -c 4 " + host, shell=True, capture_output=True)
    return result.stdout.decode()


# CWE-89: SQL Injection - string concatenation in query
@app.route("/user")
def get_user():
    user_id = request.args.get("id")
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = '" + user_id + "'")
    return str(cursor.fetchall())


# CWE-327: Weak hashing algorithm - using MD5
@app.route("/hash")
def hash_data():
    data = request.args.get("data")
    result = hashlib.md5(data.encode()).hexdigest()
    return result


# CWE-798: Hardcoded credentials
API_KEY = "sk-proj-abc123def456ghi789jkl012mno345"
DB_PASSWORD = "SuperSecret123!"


@app.route("/connect")
def connect_service():
    response = requests.post(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer " + API_KEY},
    )
    return jsonify({"status": response.status_code})


# CWE-532: Logging sensitive data
@app.route("/login")
def login():
    password = request.args.get("password")
    print("User login attempt with password: " + password)
    return "OK"


# CWE-79: Reflected XSS - unsanitized user input in HTML response
@app.route("/greet")
def greet():
    name = request.args.get("name")
    return "<h1>Hello, " + name + "!</h1>"


# CWE-22: Path Traversal - reading arbitrary files
@app.route("/file")
def read_file():
    filename = request.args.get("filename")
    with open(filename, "r") as f:
        return f.read()


if __name__ == "__main__":
    app.run(debug=True)
