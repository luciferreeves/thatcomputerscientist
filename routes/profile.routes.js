const router = require("express").Router();
const {renderRoute} = require("../functions/render");

router.get('/:username', (req, res) => {
    // res.send(`Hello ${req.params.username}`);
    renderRoute(req, res, "index", "Profile");
});

module.exports = router;
