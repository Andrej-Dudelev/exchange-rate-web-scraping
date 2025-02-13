
import sqlite3
from config import DB_FILE 

DB_FILE = "valiutu_kursai.db"
def create_database():
    conn = sqlite3.connect(DB_FILE )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kursai (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valiuto_kodas TEXT,
            kursas REAL,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_rates_to_db(rates):
    """Išsaugo gautus kursus į duomenų bazę."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for record in rates:
        cursor.execute("INSERT INTO kursai (valiuto_kodas, kursas, data) VALUES (?, ?, ?)", record)
    conn.commit()
    conn.close()
