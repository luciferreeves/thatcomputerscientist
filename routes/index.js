const router = require("express").Router();
const home = require('./basic.routes');
const api = require('./api');

router.use('/', home);
router.use('/api', api);

module.exports = router;
