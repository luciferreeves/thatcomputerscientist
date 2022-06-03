const jwt = require("jsonwebtoken");
require("dotenv").config();
const validationString = process.env.AUTHORIZATION_STRING;
function validateAuthorization(auth) {
  if (!auth) return false;
  if (auth === validationString) {
    return true;
  } else {
    const parsedJWT = jwt.verify(auth, validationString);
    if (parsedJWT.admin == 1) {
      return true;
    } else {
      return false;
    }
  }
}

module.exports = {
  validateAuthorization,
};
