const jwt = require("jsonwebtoken");
require("dotenv").config();
const validationString = process.env.AUTHORIZATION_STRING;
function renderRoute(req, res, page, title, protected = false, data = {}) {
  res.locals.messages = req.flash();
  let currentDomain = req.get("host").split(".");
  currentDomain = req.protocol + "://" + currentDomain.at(-2) + "." + currentDomain.at(-1);
  jwt.verify(req.cookies.token, validationString, (err, decoded) => {
    if (err) {
      res.clearCookie("token");
      if (protected) {
        res.redirect("/");
      } else {
        res.render(page, {
          title: title,
          ...data,
          domain: currentDomain
        });
      }
    } else {
      res.render(page, {
        title: title,
        username: decoded.username,
        ...data,
        domain: currentDomain
      });
    }
  });
}

module.exports = {
  renderRoute,
};
