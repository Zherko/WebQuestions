#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DIR, 'accounts.sqlite')

# Remove existing to recreate
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT,
    registered_at TEXT NOT NULL,
    birth_date TEXT,
    accepted_terms INTEGER NOT NULL
);
''')

# Insert a sample account with password 'pass123'
now = datetime.utcnow().isoformat()
cur.execute('INSERT INTO accounts (name, email, password, registered_at, birth_date, accepted_terms) VALUES (?, ?, ?, ?, ?, ?);',
            ("Usuario Ejemplo", "ejemplo@dominio.test", "pass123", now, "1990-01-01", 1))
conn.commit()
conn.close()
print(f'Created {DB_PATH} with sample account.')
