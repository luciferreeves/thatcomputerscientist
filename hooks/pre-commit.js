const fs = require("fs");

// Open the readme file
const readme = fs.readFileSync("README.md", "utf8");

// Find the line which starts with "![Screenshot]"
const screenshotLine = readme.split("\n").find(line => line.startsWith("![Screenshot]"));
screenshotLine.replace("![Screenshot]", `![Screenshot](https://api.thatcomputerscientist.com/screenshot?random=${Math.random()})`);

// Write the new line to the readme file
fs.writeFileSync("README.md", readme);
