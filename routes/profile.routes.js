const router = require("express").Router();

router.get('/:username', (req, res) => {
    res.send(`Hello ${req.params.username}`);
});

module.exports = router;
