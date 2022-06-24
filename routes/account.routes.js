const router = require("express").Router();
const { renderRoute } = require("../functions/render");
const mysql = require("mysql2");
const jwt = require("jsonwebtoken");
const connectionString = process.env.DATABASE_URL;
const md5 = require("md5");

router.get('/', (req, res) => {
    const username = jwt.decode(req.cookies.token).username;
    const connection = mysql.createConnection(connectionString);
    connection.connect();
    const sql = "SELECT * FROM Profiles WHERE username = ?";
    connection.query(sql, [username], (err, results, fields) => {
        if (err) {
            res.status(500).render('error', {
                error: err,
            });
        } else {
            if (results.length > 0) {
                const user = results[0];
                renderRoute(req, res, 'account', 'My Account', true, {
                    user: {
                        ...user,
                        avatar: md5(user.email || '')
                    }
                });
            } else {
                renderRoute(req, res, 'account', 'My Account', true, {
                    user: null
                });
            }
        }
    });
    connection.end();
});

router.post('/updateAccount', (req, res) => {
    jwt.verify(req.cookies.token, process.env.AUTHORIZATION_STRING, (err, decoded) => {
        if (err) {
            renderRoute(req, res, 'error', 'Error', false)
        } else {
            const username = decoded.username;
            const firstname = req.body.firstname;
            const lastname = req.body.lastname;
            const location = req.body.location;
            const bio = req.body.bio;
            const public = req.body.isPublic;
            const emailPublic = req.body.emailPublic;
            const connection = mysql.createPool(connectionString);
            connection.getConnection((err, connection) => {
                if (err) {
                    renderRoute(req, res, 'error', 'Error', false, {
                        error: err.message
                    });
                } else {
                    const sql = "UPDATE Profiles SET firstname = ?, lastname = ?, location = ?, bio = ?, public = ?, emailPublic = ? WHERE username = ?";
                    connection.query(sql, [firstname, lastname, location, bio, public, emailPublic, username], (err, results, fields) => {
                        if (err) {
                            req.flash('updateaccerror', err.message);
                            res.redirect(req.get('referer'));
                        } else {
                            req.flash('updateaccsuccess', 'Account updated successfully');
                            res.redirect(req.get('referer'));
                        }
                    });
                }
            });
        }
    });
});


module.exports = router;
