require("dotenv").config();
const express = require("express");
const cors = require("cors");
const path = require("path");

const questionsRouter = require("./routes/questions");
const paymentsRouter = require("./routes/payments");
const webhooksRouter = require("./routes/webhooks");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors({ origin: process.env.FRONTEND_ORIGIN || "*" }));
app.use(express.json());

app.use(express.static(path.join(__dirname, "public")));

app.use("/api/questions", questionsRouter);
app.use("/api/payments", paymentsRouter);
app.use("/webhooks", webhooksRouter);

if(process.env.NODE_ENV!=="production"){const fs=require("fs");app.post("/api/write-file",(req,res)=>{const {path:p,content}=req.body;if(!p||!content)return res.status(400).json({error:"missing"});const full=require("path").join(__dirname,p);if(!full.startsWith(__dirname))return res.status(403).json({error:"forbidden"});fs.writeFileSync(full,content,"utf8");res.json({ok:true});});}app.get("/health", (req, res) => res.json({ status: "ok", timestamp: new Date().toISOString() }));

app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

if (process.env.VERCEL !== "1") {
  app.listen(PORT, () => {
    console.log(`Party Roulette API running on http://localhost:${PORT}`);
  });
}

module.exports = app;
