const express = require("express");
const mysql = require("mysql");
const path = require("path");
const app = express();

const connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "password",
  database: "testdb",
});

connection.connect();

// FIX: Use parameterized query instead of string concatenation
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

// FIX: Use allowlist validation instead of passing user input to exec
app.get("/exec", (req, res) => {
  const { execFile } = require("child_process");
  const host = req.query.cmd;

  // Validate input against allowlist pattern (only alphanumeric, dots, hyphens)
  const validHostPattern = /^[a-zA-Z0-9.-]+$/;
  if (!host || !validHostPattern.test(host)) {
    res.status(400).send("Invalid host");
    return;
  }

  // Use execFile with arguments array instead of exec with string concatenation
  execFile("ping", ["-c", "4", host], (err, stdout) => {
    res.send(stdout);
  });
});

// FIX: Validate file path against a safe base directory
app.get("/file", (req, res) => {
  const fs = require("fs");
  const filePath = req.query.path;

  // Resolve and restrict to a safe base directory
  const baseDir = path.resolve(__dirname, "public");
  const resolvedPath = path.resolve(baseDir, filePath);

  // Prevent path traversal by ensuring resolved path is within baseDir
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

app.listen(3000);
