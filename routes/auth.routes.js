const router = require("express").Router();
const jwt = require("jsonwebtoken");
const mysql = require("mysql2");
const bcrypt = require("bcryptjs");
const { renderRoute } = require("../functions/render");

require("dotenv").config();
const validationString = process.env.AUTHORIZATION_STRING;
const connectionURL = process.env.DATABASE_URL;

router.get("/logout", (req, res) => {
  res.clearCookie("token");
  res.redirect(req.get("referer"));
});

router.post("/login", (req, res) => {
  // Log in as user
  const username = req.body.username;
  const password = req.body.password;
  const connection = mysql.createConnection(connectionURL);
  connection.connect();
  const sql = "SELECT * FROM Users WHERE username = ?";
  connection.query(sql, [username], (err, results, fields) => {
    if (err) {
      renderRoute(req, res, "errors/page_error", "Error", false, {
        error: err.message,
      });
    } else {
      if (results.length > 0) {
        const user = results[0];
        if (bcrypt.compareSync(password, user.password)) {
          // expires in 30 days
          const token = jwt.sign(
            {
              username: user.username,
              admin: user.admin,
            },
            validationString,
            {
              expiresIn: "30d",
            }
          );
          // set cookie
          res.cookie("token", token, {
            maxAge: 30 * 24 * 60 * 60 * 1000,
          });
          res.redirect(req.get("referer"));
        } else {
          // incorrect password, redirect to referer with error
          req.flash("error", "Incorrect password");
          res.redirect(req.get("referer"));
        }
      } else {
        // user not found, redirect to referer with error
        req.flash("error", "User not found");
        res.redirect(req.get("referer"));
      }
    }
  });
  connection.end();
});

router.post("/changePassword", (req, res) => {
  jwt.verify(req.cookies.token, validationString, (err, decoded) => {
    if (err) {
      renderRoute(req, res, "index", "Home", false);
    } else {
      const username = decoded.username;
      const password = req.body.password;
      const newPassword = req.body.new_password;
      const connection = mysql.createPool(connectionURL);
      connection.getConnection((err, connection) => {
        if (err) {
          renderRoute(req, res, "errors/page_error", "Error", false, {
            error: err.message,
          });
        } else {
          const sql = "SELECT * FROM Users WHERE username = ?";
          connection.query(sql, [username], (err, results, fields) => {
            if (err) {
              renderRoute(req, res, "errors/page_error", "Error", false, {
                error: err.message,
              });
            } else {
              if (results.length > 0) {
                const user = results[0];
                if (bcrypt.compareSync(password, user.password)) {
                  const hashedPassword = bcrypt.hashSync(newPassword, 10);
                  const sql =
                    "UPDATE Users SET password = ? WHERE username = ?";
                  connection.query(
                    sql,
                    [hashedPassword, username],
                    (err, results, fields) => {
                      if (err) {
                        req.flash("passchangeerror", "Error updating password");
                        res.redirect(req.get("referer"));
                      } else {
                        req.flash(
                          "passchangesuccess",
                          "Password updated successfully"
                        );
                        res.redirect(req.get("referer"));
                      }
                    }
                  );
                } else {
                  req.flash("passchangeerror", "Incorrect password");
                  res.redirect(req.get("referer"));
                }
              } else {
                req.flash("passchangeerror", "User not found");
                res.redirect(req.get("referer"));
              }
            }
          });
        }
      });
    }
  });
});

module.exports = router;
