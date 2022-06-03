const router = require("express").Router();
const home = require('./basic.routes');
const auth = require('./auth.routes');
const api = require('./api');

router.use('/', home);
router.use('/auth', auth);
router.use('/api', api);

module.exports = router;
