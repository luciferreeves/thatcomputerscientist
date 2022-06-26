const express = require("express");
const cors = require("cors");
const cookieParser = require("cookie-parser");
const flash = require("connect-flash");
const expressSession = require("express-session");
const mysql = require("mysql2");
const app = express();
const port = process.env.PORT || 3000;
const connectionURL = process.env.DATABASE_URL;
const cron = require("node-cron");
const subdomains = require("wildcard-subdomains");
require("dotenv").config();

// Middleware
app.use(cors());
app.use(express.json());
app.use(cookieParser());
app.use(express.urlencoded({ extended: true }));
app.use(
  expressSession({
    cookie: {
      maxAge: 30 * 24 * 60 * 60 * 1000,
    },
    secret: process.env.AUTHORIZATION_STRING,
    resave: true,
    saveUninitialized: false
  })
);
app.use(function(req, res, next) {
  res.header('Access-Control-Allow-Credentials', true);
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE');
  res.header('Access-Control-Allow-Headers', 'X-Requested-With, X-HTTP-Method-Override, Content-Type, Accept');
  // Removing some custom headers
  res.removeHeader('X-Powered-By');
  res.removeHeader('fly-request-id');
  res.removeHeader('server');
  res.removeHeader('via');
  next();
});
app.use(flash());

app.use(
  subdomains({
    namespace: "_profile",
    whitelist: ["www"],
  })
);

// Set Template Engine
app.set("view engine", "ejs");

// Set public folder
app.use(express.static(__dirname + "/public"));

// set views folder
app.set("views", __dirname + "/views");

// Routes
app.use("/", require("./routes"));

// Run a cron job every 6 days to connect to the database - so that the database does not sleep
cron.schedule("0 0 */6 * *", () => {
  console.log("Cron job running");
  const connection = mysql.createConnection(connectionURL);
  connection.connect();
  connection.query("SELECT 1", (err, results, fields) => {
    if (err) {
      console.log(err);
    } else {
      console.log("Database connected");
    }
  });
  connection.end();
});

// Start server
app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
