const express = require("express");
const mysql = require("mysql");
const path = require("path");
const crypto = require("crypto");
const rateLimit = require("express-rate-limit");

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(limiter);

const connection = mysql.createConnection({
  host: process.env.DB_HOST || "localhost",
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

connection.connect();

// FIX CWE-89: Parameterized query
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

// FIX CWE-78: execFile + input validation
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

// FIX CWE-22: Reject traversal sequences, validate resolved path
app.get("/file", (req, res) => {
  const fs = require("fs");
  const filePath = req.query.path;
  if (!filePath) {
    res.status(400).send("Path required");
    return;
  }
  if (filePath.includes("..") || path.isAbsolute(filePath)) {
    res.status(403).send("Access denied");
    return;
  }
  const baseDir = path.join(__dirname, "public");
  const sanitizedPath = path
    .normalize(filePath)
    .replace(/^(\.\.(\/|\\|$))+/, "");
  const resolvedPath = path.join(baseDir, sanitizedPath);
  if (!resolvedPath.startsWith(baseDir)) {
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

// FIX CWE-79: HTML-escape user input
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

// FIX CWE-918: Allowlist for endpoints
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

// FIX CWE-327: Use SHA-256
app.get("/hash", (req, res) => {
  const data = req.query.data;
  if (!data) {
    res.status(400).send("Data required");
    return;
  }
  const hash = crypto.createHash("sha256").update(data).digest("hex");
  res.send(hash);
});

// FIX CWE-598: Use POST for sensitive data, do not log passwords
app.post("/login", (req, res) => {
  const password = req.body.password;
  if (!password) {
    res.status(400).send("Password required");
    return;
  }
  console.log("User login attempt received");
  res.send("OK");
});

app.listen(3000);
