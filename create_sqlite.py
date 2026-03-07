#!/usr/bin/env python3
import sqlite3
import os

DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DIR, 'questions.sqlite')

SEED_QUESTIONS = [
    "¿Quién es la persona más sexy de esta habitación?",
    "¿Qué es lo más vergonzoso que has hecho estando borracho/a?",
    "Si tuvieras que besar a alguien de aquí para salvar tu vida, ¿a quién elegirías?",
    "¿Cuál es el secreto que nunca le has contado a tus padres?",
    "¿Qué es lo más atrae de la persona de tu derecha?",
    "¿Has mentido alguna vez en este juego hoy?",
    "¿Cuál ha sido tu peor cita de la historia?",
    "¿Qué es lo más raro que has buscado en Google?",
    "¿Quién crees que tiene los peores gustos musicales?",
    "¿Alguna vez has enviado un mensaje por error?",
    "¿Cuál es tu mayor placer culposo?",
    "¿A quién le confiarías tu contraseña del móvil?",
    "¿Cuál es la mentira más grande que has dicho para ligar?",
    "¿Con quién del grupo cambiarías de vida?",
    "¿Cuál es el mensaje más atrevido que has enviado?",
    "¿Cuál es tu opinión impopular más fuerte?",
    "¿Qué harías si fueras del sexo opuesto por un día?",
    "¿Has tenido un 'crush' con un profesor o jefe?",
    "¿Qué es lo más infantil que sigues haciendo?",
    "¿Cuál es el sitio más extraño donde has dormido?"
]

# Remove existing DB to ensure seed is applied fresh
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT);')
cur.executemany('INSERT INTO questions (text) VALUES (?);', [(q,) for q in SEED_QUESTIONS])
conn.commit()
conn.close()

print(f'Created {DB_PATH} with {len(SEED_QUESTIONS)} questions.')
