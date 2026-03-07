import sqlite3
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY are required.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def migrate_questions(sqlite_path, category):
    if not os.path.exists(sqlite_path):
        print(f"File {sqlite_path} not found. Skipping.")
        return
    
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("SELECT text FROM questions")
    rows = cur.fetchall()
    
    data = [{"text": row[0], "category": category} for row in rows]
    
    if data:
        print(f"Migrating {len(data)} questions for {category}...")
        supabase.table("questions").insert(data).execute()
        print("Done.")
    
    conn.close()

if __name__ == "__main__":
    # Base path for the project
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Migrate amigos.sqlite
    migrate_questions(os.path.join(base_path, "amigos.sqlite"), "amigos")
    
    print("Migration finished successfully.")
