const express = require('express');
const router = express.Router();
const { getQuestionsByCategory, insertQuestions, insertUserSubmitted } = require('../services/supadata');
router.get('/:category', async (req, res) => {
  try {
    const { category } = req.params;
    const limit = parseInt(req.query.limit) || 20;
    const data = await getQuestionsByCategory(category, limit);
    res.json(data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
router.post('/', async (req, res) => {
  try {
    const rows = req.body;
    if (!Array.isArray(rows) || rows.length === 0) return res.status(400).json({ error: 'Body must be non-empty array' });
    const data = await insertQuestions(rows);
    res.json({ inserted: data.length, data });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
router.post('/user-submitted', async (req, res) => {
  try {
    const row = req.body;
    if (!row || !row.text) return res.status(400).json({ error: 'Missing text' });
    const data = await insertUserSubmitted(row);
    res.json({ ok: true, data });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
module.exports = router;