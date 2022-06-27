const fs = require("fs");
const shell = require("shelljs");

// Open the readme file
const readme = fs.readFileSync("README.md", "utf8");

// Find the line which starts with "![Screenshot]"
const screenshotLine = readme.split("\n").find(line => line.startsWith("![Screenshot]"));

// Replace the line with the new screenshot
const newScreenshotLine = `![Screenshot](https://api.thatcomputerscientist.com/screenshot?random=${Math.random()})`;
const newReadme = readme.replace(screenshotLine, newScreenshotLine);

// Write the new readme file
fs.writeFileSync("README.md", newReadme);

// Add the readme file to the git commit
shell.exec("git add README.md");
// shell.exec("git commit -m 'Auto Update Readme'");
