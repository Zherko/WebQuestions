const fetch = global.fetch || require('node-fetch');
const SUPADATA_API_KEY = process.env.SUPADATA_API_KEY || 'sd_bpeUti64kQu-0l-Qu0qBx4qhlYXT9kVT';
const SUPADATA_ENC_KEY = process.env.SUPADATA_ENC_KEY || SUPADATA_API_KEY;
const SUPADATA_DB = process.env.SUPADATA_DB || 'db17';
const SUPADATA_MCP = process.env.SUPADATA_MCP || 'https://pro-serv.tail9f39ff.ts.net/mcp';
async function supadataCall(name, args) {
  const body = JSON.stringify({jsonrpc:'2.0', id:1, method:'tools/call', params:{name, arguments: args}});
  const res = await fetch(SUPADATA_MCP, {method:'POST', headers:{'Content-Type':'application/json','Accept':'application/json, text/event-stream','Authorization':'Bearer '+SUPADATA_API_KEY,'SUPADATA_ENC_KEY': SUPADATA_ENC_KEY}, body});
  const txt = await res.text();
  const j = JSON.parse(txt);
  const inner = j.result?.content?.[0]?.text;
  if(j.result?.isError) throw new Error(inner || 'supadata error');
  try { return JSON.parse(inner); } catch { return inner; }
}
async function insertQuestions(rows) {
  const data = [];
  for(const row of rows){
    const r = await supadataCall('supadata_insert', {db: SUPADATA_DB, table: 'questions', row});
    data.push(r.data || r);
  }
  return data;
}
async function getQuestionsByCategory(category, limit=20) {
  const r = await supadataCall('supadata_rows', {db: SUPADATA_DB, table: 'questions', limit: 500});
  const rows = r.rows || r.data || [];
  const filtered = category ? rows.filter(x=>x.category===category) : rows;
  return filtered.slice(0, limit);
}
async function insertUserSubmitted(row) {
  const r = await supadataCall('supadata_insert', {db: SUPADATA_DB, table: 'user_submitted_questions', row});
  return r.data || r;
}
module.exports = { supadataCall, insertQuestions, getQuestionsByCategory, insertUserSubmitted };