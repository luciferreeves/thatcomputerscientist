const router = require("express").Router();
const { renderRoute } = require("../functions/render");
const mysql = require("mysql2");
const jwt = require("jsonwebtoken");

require("dotenv").config();
const validationString = process.env.AUTHORIZATION_STRING;
const connectionURL = process.env.DATABASE_URL;

router.get("/", (req, res) => {
  renderRoute(req, res, "index", "Home");
});

router.get("/verifyEmail", (req, res) => {
  jwt.verify(req.cookies.token, validationString, (err, decoded) => {
    if (err) {
      renderRoute(req, res, "index", "Home");
    } else {
      const token = req.query.token;
      jwt.verify(token, validationString, (err, decoded) => {
        if (err) {
          if (err.expiredAt) {
            renderRoute(req, res, "errors/page_error", "Token Expired Error", false, {
              error: `Your token has expired at ${err.expiredAt}. Please request an email verification again from the account page.`,
            });
          } else {
            renderRoute(req, res, "errors/page_error", "Token Error", false, {
              error: err,
            });
          }
        } else {
          const username = decoded.username;
          const email = decoded.email;
          const connection = mysql.createConnection(connectionURL);
          connection.connect();
          const sql = "UPDATE Profiles SET email = ? WHERE username = ?";
          connection.query(sql, [email, username], (err, results, fields) => {
            if (err) {
              renderRoute(req, res, "errors/page_error", "Error", false, {
                error: err,
              });
            } else {
              // go to the /account route
              res.redirect("/account");
            }
          });
          connection.end();
        }
      });
    }
  });
});

module.exports = router;
