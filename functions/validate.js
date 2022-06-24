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

var emailRegex = /^[-!#$%&'*+\/0-9=?A-Z^_a-z{|}~](\.?[-!#$%&'*+\/0-9=?A-Z^_a-z`{|}~])*@[a-zA-Z0-9](-*\.?[a-zA-Z0-9])*\.[a-zA-Z](-?[a-zA-Z0-9])+$/;

function isEmailValid(email) {
    if (!email)
        return false;

    if(email.length>254)
        return false;

    var valid = emailRegex.test(email);
    if(!valid)
        return false;

    // Further checking of some things regex can't handle
    var parts = email.split("@");
    if(parts[0].length>64)
        return false;

    var domainParts = parts[1].split(".");
    if(domainParts.some(function(part) { return part.length>63; }))
        return false;

    return true;
}

module.exports = {
  validateAuthorization,
  isEmailValid
};
