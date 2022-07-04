const router = require("express").Router();
const puppeteer = require("puppeteer");
const fs = require("fs");
const yaml = require("yaml");
const config = yaml.parse(fs.readFileSync("site.config.yml", "utf8"));

router.get("/", async (req, res) => {
    const width = parseInt(req.query.width) ? parseInt(req.query.width) : 1920;
    const height = parseInt(req.query.height) ? parseInt(req.query.height) : 1080;
    const url = req.query.url || config.url;
    const format = req.query.format ? ['png', 'jpeg', 'webp'].includes(req.query.format) ? req.query.format : 'png' : 'png';
    const fullpage = req.query.fullpage || true;

    // Set screenshot options
    const options = { type: format, fullPage: fullpage };
    
    // Take a screenshot
    const image = async (url, width, height, options) => {     
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        page.setViewport({ width, height });
        // Go to the url
        await page.goto(url, { waitUntil: "networkidle2" });
        // Take a screenshot
        const screenshot = await page.screenshot(options);
        // Close the browser
        await browser.close();
        // Return the screenshot
        return screenshot;
    }

    // Get the screenshot
    image(url, width, height, options).then(screenshot => {
        // Send the screenshot
        res.setHeader("Content-Type", `image/${format}`);
        res.send(screenshot);
    }).catch(err => {
        // Send an error
        res.status(500).json({
            message: "Error",
            error: err
        });
    });
});

module.exports = router;
