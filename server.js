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

app.get("/health", (req, res) => res.json({ status: "ok", timestamp: new Date().toISOString() }));

app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, () => {
  console.log(`Party Roulette API running on http://localhost:${PORT}`);
});
