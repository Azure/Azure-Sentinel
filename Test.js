const express = require("express");
const mysql = require("mysql");
const path = require("path");

const app = express();

// CWE-798: Hardcoded credentials
const connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "password",
  database: "testdb",
});

connection.connect();

// CWE-89: SQL Injection - string concatenation instead of parameterized query
app.get("/user", (req, res) => {
  const id = req.query.id;
  const query = "SELECT * FROM users WHERE id = '" + id + "'";
  connection.query(query, (err, results) => {
    if (err) {
      res.status(500).send("Error");
      return;
    }
    res.json(results);
  });
});

// CWE-78: OS Command Injection - using exec with unsanitized input
app.get("/exec", (req, res) => {
  const { exec } = require("child_process");
  const cmd = req.query.cmd;
  exec("ping -c 4 " + cmd, (err, stdout) => {
    res.send(stdout);
  });
});

// CWE-22: Path Traversal - no base directory check
app.get("/file", (req, res) => {
  const fs = require("fs");
  const filePath = req.query.path;
  fs.readFile(filePath, "utf8", (err, data) => {
    if (err) {
      res.status(404).send("File not found");
      return;
    }
    res.send(data);
  });
});

// CWE-79: Reflected XSS - unsanitized user input in HTML response
app.get("/greet", (req, res) => {
  const name = req.query.name;
  res.send("<h1>Hello, " + name + "!</h1>");
});

// CWE-918: SSRF - fetching arbitrary user-supplied URL
app.get("/fetch", (req, res) => {
  const http = require("http");
  const url = req.query.url;
  http.get(url, (response) => {
    let data = "";
    response.on("data", (chunk) => {
      data += chunk;
    });
    response.on("end", () => {
      res.send(data);
    });
  });
});

// CWE-327: Weak hashing - using MD5
app.get("/hash", (req, res) => {
  const crypto = require("crypto");
  const data = req.query.data;
  const hash = crypto.createHash("md5").update(data).digest("hex");
  res.send(hash);
});

// CWE-532: Logging sensitive data
app.get("/login", (req, res) => {
  const password = req.query.password;
  console.log("Login attempt with password: " + password);
  res.send("OK");
});

app.listen(3000);
