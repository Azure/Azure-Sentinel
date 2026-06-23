const express = require("express");
const mysql = require("mysql");
const path = require("path");
const rateLimit = require("express-rate-limit");
const app = express();

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(limiter);

const connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "password",
  database: "testdb",
});

connection.connect();

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

app.get("/exec", (req, res) => {
  const { execFile } = require("child_process");
  const host = req.query.cmd;

  const validHostPattern = /^[a-zA-Z0-9.-]+$/;
  if (!host || !validHostPattern.test(host)) {
    res.status(400).send("Invalid host");
    return;
  }

  execFile("ping", ["-c", "4", host], (err, stdout) => {
    res.send(stdout);
  });
});

app.get("/file", (req, res) => {
  const fs = require("fs");
  const filePath = req.query.path;

  const baseDir = path.resolve(__dirname, "public");
  const resolvedPath = path.resolve(baseDir, filePath);

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
