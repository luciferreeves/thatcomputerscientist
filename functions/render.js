const jwt = require("jsonwebtoken");
require("dotenv").config();
const validationString = process.env.AUTHORIZATION_STRING;
function renderRoute(req, res, page, title, protected = false, data = {}) {
  res.locals.messages = req.flash();
  jwt.verify(req.cookies.token, validationString, (err, decoded) => {
    if (err) {
      res.clearCookie("token");
      if (protected) {
        res.redirect("/");
      } else {
        res.render(page, {
          title: title,
          ...data,
        });
      }
    } else {
      res.render(page, {
        title: title,
        username: decoded.username,
        ...data,
      });
    }
  });
}

module.exports = {
  renderRoute,
};
