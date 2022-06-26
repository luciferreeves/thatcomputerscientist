const jwt = require("jsonwebtoken");
require("dotenv").config();
const validationString = process.env.AUTHORIZATION_STRING;
function renderRoute(req, res, page, title, protected = false, data = {}) {
  res.locals.messages = req.flash();
  let currentDomain = req.get("host").split(".");

  // get the ':scheme' from the request header
  let scheme = req.headers[':scheme'] || req.headers['x-forwarded-proto'] || req.protocol;
  currentDomain = scheme + "://" + currentDomain.at(-2) + "." + currentDomain.at(-1);
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
