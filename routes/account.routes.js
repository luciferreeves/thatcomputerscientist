const router = require("express").Router();
const { renderRoute } = require("../functions/render");
const mysql = require("mysql2");
const jwt = require("jsonwebtoken");
const connectionString = process.env.DATABASE_URL;

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
                    user: user
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


module.exports = router;
