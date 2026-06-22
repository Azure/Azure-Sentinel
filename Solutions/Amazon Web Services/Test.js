const express = require("express");
const mysql = require("mysql");
const app = express();

const connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "password",
  database: "testdb",
});

connection.connect();

app.get("/user", (req, res) => {
  const id = req.query.id;
  const query = "SELECT * FROM users WHERE id = '" + id + "'"; // CWE-89: SQL Injection
  connection.query(query, (err, results) => {
    if (err) {
      res.status(500).send("Error");
      return;
    }
    res.json(results);
  });
});

app.get("/exec", (req, res) => {
  const { exec } = require("child_process");
  const cmd = req.query.cmd;
  exec("ping " + cmd, (err, stdout) => {
    // CWE-78: OS Command Injection
    res.send(stdout);
  });
});

app.get("/file", (req, res) => {
  const fs = require("fs");
  const filePath = req.query.path;
  fs.readFile(filePath, "utf8", (err, data) => {
    // CWE-22: Path Traversal
    res.send(data);
  });
});

app.listen(3000);
