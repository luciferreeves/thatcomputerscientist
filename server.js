const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");
const cookieParser = require('cookie-parser');
const flash = require('connect-flash');
const expressSession = require('express-session');
const app = express();
const port = process.env.PORT || 3000;
require("dotenv").config();

// Middleware
app.use(cors());
app.use(express.json());
app.use(cookieParser());
app.use(express.urlencoded({ extended: true }));
app.use(expressSession({
  cookie: { maxAge: 30 * 24 * 60 * 60 * 1000 },
  secret: process.env.AUTHORIZATION_STRING,
}));
app.use(flash());

// Set Template Engine
app.set("view engine", "ejs");

// Set public folder
app.use(express.static(__dirname + "/public"));

// set views folder
app.set("views", __dirname + "/views");

// Routes
app.use("/", require("./routes"));

// Start server
app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
