
from datetime import datetime, timedelta
from gmail_client import GmailClient
from database_operations import create_database, save_rates_to_db
from scraping import scrape_rates_for_date
from config import CURRENCY_MAP
import logging
from database_operations import compute_averages, get_max_rate, get_min_rate

if __name__ == '__main__':
    create_database()
    end_date_obj = datetime.now()
    start_date_obj = end_date_obj - timedelta(days=29)
    print(f"Laikotarpis: {start_date_obj.strftime('%Y-%m-%d')} iki {end_date_obj.strftime('%Y-%m-%d')}")

    all_rates = []
    current_date = start_date_obj
    while current_date <= end_date_obj:
        daily_rates = scrape_rates_for_date(current_date)
        all_rates.extend(all_rates)
        current_date += timedelta(days=1)

    save_rates_to_db(all_rates)
    logging.info("Visi duomenys irasyti i duomenu baze.")
    averages = compute_averages(start_date_obj.strftime("%Y-%m-%d"), end_date_obj.strftime("%Y-%m-%d"))
    logging.info("\nVidutiniai kursai per 30 dienu:")
    for currency, avg in averages.items():
        logging.info(f"{currency}: {avg:.3f}")

    for currency in CURRENCY_MAP.values():
        max_rate = get_max_rate(currency, start_date_obj.strftime("%Y-%m-%d"), end_date_obj.strftime("%Y-%m-%d"))
        min_rate = get_min_rate(currency, start_date_obj.strftime("%Y-%m-%d"), end_date_obj.strftime("%Y-%m-%d"))
        logging.info(f"{currency} Maks: {max_rate:.3f}, Min: {min_rate:.3f}")

recipient_email = "gavejas@gmail.com"
start_date = "2025-02-01 00:00:00"
end_date = "2025-02-10 23:59:59"
currencies = ["USD", "GBP", "AUD"]


for curr in currencies:
    max_rate = get_max_rate(curr, start_date, end_date)
    if max_rate is not None:
        subject = f"{curr} - Auksciausias kursas pasiektas!"
        body = f"{curr} auksciausias kursas nuo {start_date} iki {end_date} yra {max_rate:.3f}"
        
        gmail_client = GmailClient()
        GmailClient.send_email(subject, body, recipient_email)

    min_rate = get_min_rate(curr, start_date, end_date)
    if min_rate is not None:
        subject = f"{curr} - Maziausias kursas pasiektas!"
        body = f"{curr} maziausias kursas nuo {start_date} iki {end_date} yra {min_rate:.3f}"
        GmailClient.send_email(subject, body, recipient_email)
