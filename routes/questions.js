const express = require("express");
const router = express.Router();
const { getSupabase } = require("../services/supabase");

router.get("/:category", async (req, res) => {
  try {
    const sb = getSupabase();
    const { category } = req.params;
    const limit = parseInt(req.query.limit) || 20;

    const { data, error } = await sb
      .from("questions")
      .select("*")
      .eq("category", category)
      .limit(limit);

    if (error) throw new Error(error.message);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post("/", async (req, res) => {
  try {
    const sb = getSupabase();
    const rows = req.body;

    if (!Array.isArray(rows) || rows.length === 0) {
      return res.status(400).json({ error: "Body must be a non-empty array" });
    }

    const { data, error } = await sb.from("questions").insert(rows).select();

    if (error) throw new Error(error.message);
    res.json({ inserted: data.length, data });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
