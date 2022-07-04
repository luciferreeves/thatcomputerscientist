const router = require("express").Router();
const admin = require("./private/admin");
const user = require("./private/user");
const screenshot = require("./public/screenshot");

router.use("/admin", admin);
router.use("/user", user);
router.use("/screenshot", screenshot);

router.get("/", (req, res) => {
    res.status(200).json({
        message: "Welcome to That Computer Scientist's Public API Service.",
        apis: {
            screenshot: "/screenshot",
        }
    });
});

module.exports = router;
