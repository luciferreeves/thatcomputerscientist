const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Set Template Engine
app.set("view engine", "ejs");

// Set public folder
app.use(express.static(__dirname + "/public"));

// set views folder
app.set("views", __dirname + "/views");

// Routes
app.get("/", (req, res) => {
  res.render("index");
});

// Start server
app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
