const router = require("express").Router();
const mysql = require('mysql2');
const bcrypt = require('bcryptjs');
const validateAuthorization = require('../../functions/validate');

require("dotenv").config();
const connectionURL = process.env.DATABASE_URL;

router.get("/", (req, res) => {
    const validationHeader = req.headers.auth;
    if (validateAuthorization(validationHeader)) {
        res.status(200).json({
            message: "Welcome to the Admin API!"
        });
    } else {
        res.status(401).json({
            message: "Unauthorized"
        });
    }
});

router.post("/create", (req, res) => {
    // Creates an admin user
    const validationHeader = req.headers.auth;
    if (validateAuthorization(validationHeader)) {
        const connection = mysql.createConnection(connectionURL);
        connection.connect();
        const sql = "INSERT INTO Users (username, password, admin) VALUES (?, ?, ?)";
        const username = req.body.username;
        const password = req.body.password;
        const hashedPassword = bcrypt.hashSync(password, 10);
        const admin = 1;
        connection.query(sql, [username, hashedPassword, admin], (err, results, fields) => {
            if (err) {
                res.status(500).json({
                    message: "Error creating user",
                    error: err
                });
            } else {
                res.status(201).json({
                    message: "User created"
                });
            }
        });
        connection.end();
    } else {
        res.status(401).json({
            message: "Unauthorized"
        });
    }
});

router.post('/delete', (req, res) => {
    // Deletes an admin user
    const validationHeader = req.headers.auth;
    if (validateAuthorization(validationHeader)) {
        const connection = mysql.createConnection(connectionURL);
        connection.connect();
        const sql = "DELETE FROM Users WHERE username = ?";
        const username = req.body.username;
        connection.query(sql, [username], (err, results, fields) => {
            if (err) {
                res.status(500).json({
                    message: "Error deleting user",
                    error: err
                });
            } else {
                res.status(200).json({
                    message: "User deleted"
                });
            }
        });
        connection.end();
    } else {
        res.status(401).json({
            message: "Unauthorized"
        });
    }
});


module.exports = router;
