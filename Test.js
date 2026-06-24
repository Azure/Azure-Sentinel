const express = require("express");
const mysql = require("mysql");
const path = require("path");
const crypto = require("crypto");
const rateLimit = require("express-rate-limit");

const app = express();

// FIX CWE-798: Rate limiting to prevent brute force
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(limiter);

// FIX CWE-798: Load credentials from environment variables
const connection = mysql.createConnection({
  host: process.env.DB_HOST || "localhost",
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

connection.connect();

// FIX CWE-89: Use parameterized query to prevent SQL Injection
app.get("/user", (req, res) => {
  const id = req.query.id;
  const query = "SELECT * FROM users WHERE id = ?";
  connection.query(query, [id], (err, results) => {
    if (err) {
      res.status(500).send("Error");
      return;
    }
    res.json(results);
  });
});

// FIX CWE-78: Use execFile with input validation to prevent Command Injection
app.get("/exec", (req, res) => {
  const { execFile } = require("child_process");
  const host = req.query.cmd;
  const validHostPattern = /^[a-zA-Z0-9.-]+$/;
  if (!host || !validHostPattern.test(host)) {
    res.status(400).send("Invalid host");
    return;
  }
  execFile("ping", ["-c", "4", host], (err, stdout) => {
    if (err) {
      res.status(500).send("Command failed");
      return;
    }
    res.send(stdout);
  });
});

// FIX CWE-22: Validate resolved path stays within base directory
app.get("/file", (req, res) => {
  const fs = require("fs");
  const filePath = req.query.path;
  if (!filePath) {
    res.status(400).send("Path required");
    return;
  }
  const baseDir = path.resolve(__dirname, "public");
  const resolvedPath = path.resolve(baseDir, filePath);
  if (
    !resolvedPath.startsWith(baseDir + path.sep) &&
    resolvedPath !== baseDir
  ) {
    res.status(403).send("Access denied");
    return;
  }
  fs.readFile(resolvedPath, "utf8", (err, data) => {
    if (err) {
      res.status(404).send("File not found");
      return;
    }
    res.send(data);
  });
});

// FIX CWE-79: Escape user input to prevent XSS
app.get("/greet", (req, res) => {
  const name = req.query.name || "";
  const escapedName = name
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
  res.send("<h1>Hello, " + escapedName + "!</h1>");
});

// FIX CWE-918: Use allowlist to prevent SSRF
const ALLOWED_ENDPOINTS = {
  users: "https://api.example.com/users",
  data: "https://api.example.com/data",
  status: "https://api.example.com/status",
};

app.get("/fetch", (req, res) => {
  const https = require("https");
  const endpoint = req.query.endpoint;
  if (!endpoint || !ALLOWED_ENDPOINTS[endpoint]) {
    res.status(403).send("Endpoint not allowed");
    return;
  }
  const url = ALLOWED_ENDPOINTS[endpoint];
  https.get(url, (response) => {
    let data = "";
    response.on("data", (chunk) => {
      data += chunk;
    });
    response.on("end", () => {
      res.type("text/plain").send(data);
    });
  });
});

// FIX CWE-327: Use SHA-256 instead of MD5
app.get("/hash", (req, res) => {
  const data = req.query.data;
  if (!data) {
    res.status(400).send("Data required");
    return;
  }
  const hash = crypto.createHash("sha256").update(data).digest("hex");
  res.send(hash);
});

// FIX CWE-532: Do not log sensitive data
app.get("/login", (req, res) => {
  const password = req.query.password;
  if (!password) {
    res.status(400).send("Password required");
    return;
  }
  console.log("User login attempt received");
  res.send("OK");
});

app.listen(3000);
