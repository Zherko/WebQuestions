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
    const allowed = ['javierortunorodriguez@gmail.com','kiril.ivanov.petrov@gmail.com'];
    const authHeader = req.headers.authorization || '';
    const token = authHeader.replace('Bearer ','');
    if(!token) return res.status(401).json({error:'No token'});
    const { createClient } = require('@supabase/supabase-js');
    const supa = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);
    const { data:{user}, error } = await supa.auth.getUser(token);
    if(error || !user || !allowed.includes(user.email?.toLowerCase())) return res.status(403).json({error:'No autorizado'});
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