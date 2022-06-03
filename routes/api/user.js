const router = require("express").Router();
const mysql = require('mysql2');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

require("dotenv").config();

const connectionURL = process.env.DATABASE_URL;
const validationString = process.env.AUTHORIZATION_STRING;

router.post('/login', (req, res) => {
    // Log in as user
    const username = req.body.username;
    const password = req.body.password;
    const connection = mysql.createConnection(connectionURL);
    connection.connect();
    const sql = "SELECT * FROM Users WHERE username = ?";
    connection.query(sql, [username], (err, results, fields) => {
        if (err) {
            res.status(500).json({
                message: "Error logging in",
                error: err
            });
        } else {
            if (results.length > 0) {
                const user = results[0];
                if (bcrypt.compareSync(password, user.password)) {
                    const token = jwt.sign({
                        username: user.username,
                        admin: user.admin
                    }, validationString);
                    res.status(200).json({
                        message: "Logged in",
                        token: token
                    });
                } else {
                    res.status(401).json({
                        message: "Incorrect password"
                    });
                }
            } else {
                res.status(401).json({
                    message: "User not found"
                });
            }
        }
    });
    connection.end();
});

router.post('/create', (req, res) => {
    // Creates a regular user
    const username = req.body.username;
    const password = req.body.password;
    const connection = mysql.createConnection(connectionURL);
    connection.connect();
    const sql = "INSERT INTO Users (username, password, admin) VALUES (?, ?, ?)";
    const hashedPassword = bcrypt.hashSync(password, 10);
    const admin = 0;
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
});



module.exports = router;