const router = require("express").Router();
const jwt = require("jsonwebtoken");

require("dotenv").config();
const validationString = process.env.AUTHORIZATION_STRING;

router.get("/", (req, res) => {
  res.locals.messages = req.flash();
  jwt.verify(req.cookies.token, validationString, (err, decoded) => {
    if (err) {
      res.clearCookie("token");
      res.render("index", {
        title: "Home"
      });
    } else {
      res.render("index", {
        title: "Home",
        username: decoded.username
      });
    }
  });
});

module.exports = router;
