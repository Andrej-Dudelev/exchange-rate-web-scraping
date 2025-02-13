
from datetime import date
import requests
from bs4 import BeautifulSoup
from config import URL, headers, CURRENCY_MAP

def scrape_rates_for_date(date_obj):
    """Parsiunčia duomenis pagal datą ir grąžina sąrašą su valiutų kursais."""
    date_str = date_obj.strftime("%Y-%m-%d")
    url = URL.format(date_str)
    print(f"Scraping data for date: {date_str}")

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Nepavyko gauti duomenų už {date_str}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "ratesTable"})
    if not table:
        print(f"Valiutų kursų lentelės nerasta {date_str}")
        return []

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

# xrates_response = requests.get("https://www.x-rates.com/historical/?from=EUR&date={}", headers=headers)
# print(xrates_response.status_code)
# xrates_html = xrates_response.text