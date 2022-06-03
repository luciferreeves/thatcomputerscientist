const router = require("express").Router();
const { renderRoute } = require('../functions/render'); 

router.get("/", (req, res) => {
  renderRoute(req, res, 'index', 'Home');
});

module.exports = router;
