import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime, timedelta

# URL kur galima pakeisti data. 
URL = "https://www.x-rates.com/historical/?from=EUR&date={}"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
# valiutos su kuriomis dirbsiu.
CURRENCY_MAP  = {
    "US Dollar": "USD",
    "British Pound": "GBP",
    "Australian Dollar": "AUD"
}
xrates_response = requests.get("https://www.x-rates.com/historical/?from=EUR&date={}", headers=headers)
print(xrates_response.status_code)
xrates_html = xrates_response.text

with open("xrates_response.html", "w", encoding="utf-8") as xrates_file:
    xrates_file.write(xrates_html)
print("Kodas parsisiustas")

# Sukuria (jei dar nera) duomenu bazes lentele 'kursai'
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

def scrape_rates_for_date(date_obj):
    """
    Parsisiunčia duomenis iš x‑rates istorinių kursų puslapio
    pagal nurodyta data ir grazina sarasa su irasais:
        (valiutos kodas, kursas, data)
    """
    date_str = date_obj.strftime("%Y-%m-%d")
    url = URL.format(date_str)
    print(f"Scraping data for date: {date_str}")

    xrates_response = requests.get(url)
    if xrates_response.status_code != 200:
        print(f"Error: Nepavyko gauti duomenu uz {date_str}")
        return []
    
    soup = BeautifulSoup(xrates_response.text, "html.parser")
    # Ieskome lenteles, kurioje pateikti kursai (paprastai jos klase yra "ratesTable")
    table = soup.find("table", {"class": "ratesTable"})
    if not table:
        print(f"Valiutu kursu lenteles nerasta {date_str}")
        return []
    
    # Pirmoji eilute paprastai yra antraste, todel praleidziame ja
    rows = table.find_all("tr")[1:]
    date = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            # paima pirmą lentelės stulpelį (valiutos pavadinimą)
            currency_name = cols[0].get_text(strip=True)
            # paima antrą lentelės stulpelį (valiutos kursą kaip tekstą)
            rate_text = cols[1].get_text(strip=True)
            try:
                # bando konvertuoti kursą iš teksto į skaičių (float).
                rate = float(rate_text)
            except ValueError:
                continue
            # Tikriname, ar eiluteje esantis valiutos pavadinimas atitinka viena is musu norimu
            for key in CURRENCY_MAP :
                if key in currency_name:
                    currencies_code = CURRENCY_MAP [key]
                    date.append((currencies_code, rate, date_str))
    return date

def save_rates_to_db(rates):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for record in rates:
        cursor.execute("INSERT INTO kursai (valiuto_kodas, kursas, data) VALUES (?, ?, ?)", record)
    conn.commit()
    conn.close()

def compute_averages(start_date, end_date):
    """
    Apskaiciuoja vidutini kursą (AVG) kiekvienai valiutai is duomenu bazes
    per laikotarpi tarp pradzios_data ir pabaigos_data.
    Grazina zodyną: { valiutos kodas: vidurkis }
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    averages = {}
    for currencies_code in CURRENCY_MAP.values():
        query = """
            SELECT AVG(kursas) FROM kursai
            WHERE valiuto_kodas = ? AND data BETWEEN ? AND ?
        """
        cursor.execute(query, (currencies_code, start_date, end_date))
        avg_rate = cursor.fetchone()[0]
        averages[currencies_code] = avg_rate
    conn.close()
    return averages

if __name__ == '__main__':
    # Sukuriame duomenu baze, jei jos dar nera
    create_database()
    # Renkami duomenys per paskutines 30 dienų.
    end_date_obj = datetime.now()
    start_date_obj  = end_date_obj - timedelta(days=29)
    print(f"Laikotarpis: {start_date_obj .strftime('%Y-%m-%d')} iki {end_date_obj.strftime('%Y-%m-%d')}")
    
    # Iteruojame per kiekviena diena ir surenkame duomenis
    all_rates = []
    current_date  = start_date_obj 
    while current_date  <= end_date_obj:
        daily_rates = scrape_rates_for_date(current_date )
        all_rates.extend(daily_rates)
        current_date  += timedelta(days=1)
    #Irasome surinktus duomenis i duomenu baze
    save_rates_to_db(all_rates)
    print("Visi duomenys įrašyti į duomenų bazę.")
    
    # Apskaiciuojame vidurkius
    # Nustatome datos laikotarpi
    # kaip pavyzdy irasyta 30dienu.
    start_date_str = start_date_obj.strftime("%Y-%m-%d") + " 00:00:00"
    end_date_str = end_date_obj.strftime("%Y-%m-%d") + " 23:59:59"
    averages = compute_averages(start_date_str, end_date_str)
    print("\nVidutiniai kursai per 30 dienu laikotarpi:")
    for  currencies_code, avg in averages.items():
        if avg is not None:
            print(f"{currencies_code}: {avg:.3f}")
        else:
            print(f"{currencies_code}: Nera duomenu")
print()
# apsakaiciujamas auksciausias kursas nurodytoms valiutoms per nurodyta laikotarpi
# laikotarpis 30 dienu
def get_max_rate(currency, start_date, end_date):
    """
    Grąžina aukščiausią (MAX) kursą nurodytai valiutai per laikotarpį 
    tarp start_date ir end_date.
    Parametrai:
      - currency: valiutos kodas (pvz., "USD")
      - start_date: pradžios data, pvz., "2025-02-01 00:00:00"
      - end_date: pabaigos data, pvz., "2025-02-28 23:59:59"
    Grąžina:
      - aukščiausią kursą kaip skaičių, arba None, jei duomenų nėra.
    """
    # Prisijungiame prie duomenų bazės
    conn = sqlite3.connect("valiutu_kursai.db")
    cursor = conn.cursor()
    # SQL užklausa, kuri naudoja funkciją MAX, kad rastų aukščiausią kursą
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
if __name__ == '__main__':
    # Nustatome laikotarpio ribas
    start_date = "2025-02-01 00:00:00"
    end_date   = "2025-02-10 23:59:59"
    
    # Nurodytos valiutos, kurių aukščiausi kursai ieškomi
    currencies = ["USD", "GBP", "AUD"]
    for curr in currencies:
        max_rate = get_max_rate(curr, start_date, end_date)
        if max_rate is not None:
            print(f"{curr} aukščiausias kursas nuo {start_date} iki {end_date} yra {max_rate:.3f}")
        else:
            print(f"{curr}: duomenų nerasta.")
print()
# paskaiciuojamas maziausias kursas nurodytoms valiutoms
# laikotarpis 30 dienu 
def get_min_rate(currency, start_date, end_date):
    """
    Grąžina mažiausią (MIN) kursą nurodytai valiutai per laikotarpį
    tarp start_date ir end_date.

    Parametrai:
      - currency: valiutos kodas (pvz., "USD")
      - start_date: pradžios data (pvz., "2025-02-01 00:00:00")
      - end_date: pabaigos data (pvz., "2025-02-28 23:59:59")
    
    Grąžina:
      - mažiausią kursą kaip skaičių arba None, jei duomenų nėra.
    """
     
    conn = sqlite3.connect("valiutu_kursai.db")
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

if __name__ == '__main__':
    # Nustatome laikotarpio ribas parasiau pavyzdine laikotarpi
    start_date = "2025-02-01 00:00:00"
    end_date = "2025-02-10 23:59:59"
    # Norimos valiutos, kurių mažiausi kursai ieškomi
    currencies = ["USD", "GBP", "AUD"]
    # curr - tai yra 
    for curr in currencies:
        min_rate = get_min_rate(curr, start_date, end_date)
        if min_rate is not None:
            print(f"{curr} mažiausias kursas nuo {start_date} iki {end_date} yra {min_rate:.3f}")
        else:
            print(f"{curr}: duomenų nerasta.")
print()