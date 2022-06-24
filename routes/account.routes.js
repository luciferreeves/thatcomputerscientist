const router = require("express").Router();
const { renderRoute } = require("../functions/render");
const mysql = require("mysql2");
const jwt = require("jsonwebtoken");
const connectionString = process.env.DATABASE_URL;
const md5 = require("md5");
const { isEmailValid } = require("../functions/validate");

router.get("/", (req, res) => {
  const username = jwt.decode(req.cookies.token).username;
  const connection = mysql.createConnection(connectionString);
  connection.connect();
  const sql = "SELECT * FROM Profiles WHERE username = ?";
  connection.query(sql, [username], (err, results, fields) => {
    if (err) {
      res.status(500).render("error", {
        error: err,
      });
    } else {
      if (results.length > 0) {
        const user = results[0];
        renderRoute(req, res, "account", "My Account", true, {
          user: {
            ...user,
            avatar: md5(user.gravatarEmail || user.email || ""),
            url:
              user.public == 1
                ? `${req.protocol + "://" + req.get("host")}/profile/${
                    user.username
                  }`
                : "",
          },
        });
      } else {
        renderRoute(req, res, "account", "My Account", true, {
          user: null,
        });
      }
    }
  });
  connection.end();
});

router.post("/sendVerificationEmail", (req, res) => {
  jwt.verify(
    req.cookies.token,
    process.env.AUTHORIZATION_STRING,
    (err, decoded) => {
      if (err) {
        renderRoute(req, res, "error", "Error", false, {
          error: err,
        });
      } else {
        const username = decoded.username;
        const newEmail = req.body.email;
        if (!newEmail || !isEmailValid(newEmail)) {
            req.flash("mailsenderror", "Error sending verification email. Provided email is invalid.",);
            res.redirect(req.get("referer"));
        } else {
          const connection = mysql.createConnection(connectionString);
          connection.connect();
          const sql = "SELECT * FROM Profiles WHERE username = ?";
          connection.query(sql, [username], (err, results, fields) => {
            if (err) {
              renderRoute(req, res, "error", "Error", false, {
                error: err.message,
              });
            } else {
              if (results.length > 0) {
                const user = results[0];
                // const transporter = require("nodemailer").createTransport({
                //   service: "gmail",
                //   auth: {
                //     user: process.env.EMAIL_USER,
                //     pass: process.env.EMAIL_PASSWORD,
                //   },
                // });
                // // Generate a verification URL and send it to the user
                const verificationUrl = `${req.get(
                  "origin"
                )}/verifyemail?token=${jwt.sign(
                  {
                    username: user.username,
                    email: newEmail,
                  },
                  process.env.AUTHORIZATION_STRING,
                  {
                    expiresIn: "1h",
                  }
                )}`;
                // const mailOptions = {
                //   from: process.env.EMAIL_USER,
                //   to: newEmail,
                //   priority: "high",
                //   subject:
                //     "[That Computer Scientist] Request to change your email address",
                //   html: `<p>Hi ${user.firstname || user.username},</p>
                //                     <p>We received a request to change your email address to <em><u>${newEmail}</u></em>.</p>
                //                     <p>If you made this request, please click the link below to verify your new email address:</p>
                //                     <p><a href="${verificationUrl}">${verificationUrl}</a></p>
                //                     <p>If you did not make this request, you can ignore this email.</p>
                //                     <p>Thanks,</p>
                //                     <p>Kumar Priyansh</p>
                //                     <p>That Computer Scientist</p>`,
                // };
                // transporter.sendMail(mailOptions, (err, info) => {
                //   if (err) {
                //     req.flash("mailsenderror", "Error sending verification email. Please try again later.",);
                //     req.redirect(req.get("referer"));
                //   } else {
                req.flash(
                  "mailsendsuccess",
                  `Verification email sent! The link expires in 1 hour. Please check your email. Also, make sure to check your spam folder. Verification URL: ${verificationUrl}`
                );
                res.redirect(req.get("referer"));
                //   }
                // });
              } else {
                res.status(500).render("error", {
                  error: "User not found",
                });
              }
            }
          });
          connection.end();
        }
      }
    }
  );
});

router.post("/updateAccount", (req, res) => {
  jwt.verify(
    req.cookies.token,
    process.env.AUTHORIZATION_STRING,
    (err, decoded) => {
      if (err) {
        renderRoute(req, res, "error", "Error", false);
      } else {
        const username = decoded.username;
        const firstname = req.body.firstname;
        const lastname = req.body.lastname;
        const location = req.body.location;
        const bio = req.body.bio;
        const gravatarEmail = req.body.gravatarEmail;
        const public = req.body.isPublic;
        const emailPublic = req.body.emailPublic || 0;
        const connection = mysql.createPool(connectionString);
        connection.getConnection((err, connection) => {
          if (err) {
            renderRoute(req, res, "error", "Error", false, {
              error: err.message,
            });
          } else {
            const sql =
              "UPDATE Profiles SET firstname = ?, lastname = ?, location = ?, bio = ?, gravatarEmail = ?, public = ?, emailPublic = ? WHERE username = ?";
            connection.query(
              sql,
              [
                firstname,
                lastname,
                location,
                bio,
                gravatarEmail,
                public,
                emailPublic,
                username,
              ],
              (err, results, fields) => {
                if (err) {
                  req.flash("updateaccerror", err.message);
                  res.redirect(req.get("referer"));
                } else {
                  req.flash("updateaccsuccess", "Account updated successfully");
                  res.redirect(req.get("referer"));
                }
              }
            );
          }
        });
      }
    }
  );
});

module.exports = router;
