const router = require("express").Router();
const admin = require("./admin");
const user = require("./user");
const screenshot = require("./screenshot");

router.use("/admin", admin);
router.use("/user", user);
router.use("/screenshot", screenshot);

module.exports = router;
