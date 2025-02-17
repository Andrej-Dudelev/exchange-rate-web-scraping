
from datetime import date
import dataclasses
import requests
from bs4 import BeautifulSoup
from config import URL, headers, CURRENCY_MAP
import logging

def scrape_rates_for_date(date_obj):
    """Parsiuncia duomenis pagal data ir grazina sarasa su valiutu kursais."""
    date_str = date_obj.strftime("%Y-%m-%d")
    url = URL.format(date_str)
    logging.info(f"Scraping data for date: {date_str}")

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logging.info(f"Error: Nepavyko gauti duomenu uz {date_str}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "ratesTable"})
    if not table:
        logging.info(f"Valiutu kursu lenteles nerasta {date_str}")
        return []

    rows = table.find_all("tr")[1:]
    Data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            currency_name = cols[0].get_text(strip=True)
            rate_text = cols[1].get_text(strip=True)
            try:
                rate = float(rate_text)
            except ValueError:
                continue
            for key in CURRENCY_MAP :
                if key in currency_name:
                    currencies_code = CURRENCY_MAP [key]
                Data.append((currencies_code, rate, date_str))
    return date 
