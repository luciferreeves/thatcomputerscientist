const router = require("express").Router();
const puppeteer = require("puppeteer");
const fs = require("fs");

router.get("/", async (req, res) => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    page.setViewport({ width: 1920, height: 1080 });
    // Go to the url
    await page.goto("https://www.thatcomputerscientist.com/", {
        waitUntil: "networkidle2",
    });
    // Take a screenshot
    const image = await page.screenshot({fullPage : true});
    await browser.close();
    // Send the image as a response
    res.setHeader("Content-Type", "image/png");
    res.send(image);
});

module.exports = router;
