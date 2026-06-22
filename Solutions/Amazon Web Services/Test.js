// test-vuln.js
const express = require("express");
const app = express();
const mysql = require("mysql");

app.get("/user", (req, res) => {
  const id = req.query.id;
  const query = "SELECT * FROM users WHERE id = '" + id + "'"; // CWE-89: SQL Injection
  connection.query(query);
});
