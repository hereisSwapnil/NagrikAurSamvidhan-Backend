const express = require("express");
const cors = require("cors");
const cookieParser = require("cookie-parser");
const methodOverride = require("method-override");

const app = express();

app.use(cors({ origin: process.env.ORIGIN, credentials: true }));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));
app.use(cookieParser());
app.use(methodOverride("_method"));

// routes import
const userRoutes = require("./routes/user.routes.js");
const questionRoutes = require("./routes/question.routes.js");
const quizRoutes = require("./routes/quiz.routes.js");
const mapRoutes = require("./routes/map.routes.js");
const caseStudyRoutes = require("./routes/caseStudy.routes.js");

// routes declare
app.use("/user", userRoutes);
app.use("/question", questionRoutes);
app.use("/quiz", quizRoutes);
app.use("/map", mapRoutes);
app.use("/casestudy", caseStudyRoutes);

app.get("/", (req, res) => {
  res.send("Yupp The server is runnng 🎉 !");
});

module.exports = app;
