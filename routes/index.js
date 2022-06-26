const router = require("express").Router();
const home = require('./basic.routes');
const auth = require('./auth.routes');
const account = require('./account.routes');
const api = require('./api');
const profile = require('./profile.routes');
const { renderRoute } = require('../functions/render');

router.use('/', home);
router.use('/auth', auth);
router.use('/api', api);
router.use('/account', account);
router.use('/_profile', profile);
router.get('*', (req, res) => {
    // renderRoute(req, res, "404", "Page Not Found");
    res.status(404).send('404');
});

module.exports = router;
