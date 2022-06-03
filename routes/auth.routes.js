const router = require("express").Router();
const jwt = require("jsonwebtoken");
const mysql = require('mysql2');
const bcrypt = require('bcryptjs');

require("dotenv").config();
const validationString = process.env.AUTHORIZATION_STRING;
const connectionURL = process.env.DATABASE_URL;

router.get('/logout', (req, res) => {
    res.clearCookie("token");
    res.redirect(req.get('referer'));
})

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
                    // expires in 30 days
                    const token = jwt.sign({
                        username: user.username,
                        admin: user.admin
                    }, validationString, {
                        expiresIn: '30d'
                    });
                    // set cookie
                    res.cookie('token', token, {
                        maxAge: 30 * 24 * 60 * 60 * 1000,
                        httpOnly: true
                    });
                    res.redirect(req.get('referer'));
                } else {
                    // incorrect password, redirect to referer with error
                    req.flash('error', 'Incorrect password');
                    res.redirect(req.get('referer'));
                }
            } else {
                // user not found, redirect to referer with error
                req.flash('error', 'User not found');
                res.redirect(req.get('referer'));
            }
        }
    });
    connection.end();
});


module.exports = router;