const router = require("express").Router();
const home = require('./basic.routes');
const auth = require('./auth.routes');
const account = require('./account.routes');
const api = require('./api');

router.use('/', home);
router.use('/auth', auth);
router.use('/api', api);
router.use('/account', account);

module.exports = router;
