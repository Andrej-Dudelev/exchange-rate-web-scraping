import sqlite3
from config import DB_FILE

def compute_averages(start_date, end_date):
    """Apskaiciuoja vidutini kursa kiekvienai valiutai per nurodyta laikotarpi."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    averages = {}

    query = """
        SELECT valiuto_kodas, AVG(kursas) 
        FROM kursai
        WHERE data BETWEEN ? AND ?
        GROUP BY valiuto_kodas
    """
    cursor.execute(query, (start_date, end_date))
    results = cursor.fetchall()
    
    for currency_code, avg_rate in results:
        averages[currency_code] = avg_rate
    
    conn.close()
    return averages

def get_max_rate(currency, start_date, end_date):
    """Grazina auksciausia kursa valiutai per nurodyta laikotarpi."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    query = """
        SELECT MAX(kursas) 
        FROM kursai 
        WHERE valiuto_kodas = ? 
          AND data BETWEEN ? AND ?
    """
    cursor.execute(query, (currency, start_date, end_date))
    result = cursor.fetchone()[0]
    conn.close()
    return result

def get_min_rate(currency, start_date, end_date):
    """Grazina maziausia kursa valiutai per nurodyta laikotarpi."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    query = """
        SELECT MIN(kursas) 
        FROM kursai 
        WHERE valiuto_kodas = ? 
          AND data BETWEEN ? AND ?
    """
    cursor.execute(query, (currency, start_date, end_date))
    result = cursor.fetchone()[0]
    conn.close()
    return result

