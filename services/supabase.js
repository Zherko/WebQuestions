const { createClient } = require("@supabase/supabase-js");

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.warn("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set. Supabase client not initialized.");
}

const supabase = supabaseUrl && supabaseKey
  ? createClient(supabaseUrl, supabaseKey)
  : null;

function getSupabase() {
  if (!supabase) throw new Error("Supabase client not initialized");
  return supabase;
}

module.exports = { getSupabase };
