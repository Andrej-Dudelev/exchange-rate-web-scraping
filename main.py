
from datetime import datetime, timedelta
from database_operations import create_database, save_rates_to_db
from scraping import scrape_rates_for_date
from calculations import compute_averages, get_max_rate, get_min_rate
from config import CURRENCY_MAP

if __name__ == '__main__':
    create_database()
    
    # Nustatome laikotarpį
    end_date_obj = datetime.now()
    start_date_obj = end_date_obj - timedelta(days=29)

    print(f"Laikotarpis: {start_date_obj.strftime('%Y-%m-%d')} iki {end_date_obj.strftime('%Y-%m-%d')}")

    all_rates = []
    current_date = start_date_obj
    while current_date <= end_date_obj:
        daily_rates = scrape_rates_for_date(current_date)
        all_rates.extend(daily_rates)
        current_date += timedelta(days=1)

    save_rates_to_db(all_rates)
    print("Visi duomenys įrašyti į duomenų bazę.")

    # Skaičiuojame vidutinius valiutos kursa (avg) 
    averages = compute_averages(start_date_obj.strftime("%Y-%m-%d"), end_date_obj.strftime("%Y-%m-%d"))
    print("\nVidutiniai kursai per 30 dienų:")
    # perziuri zodyno reiksmes
    for currency, avg in averages.items():
        print(f"{currency}: {avg:.3f}")

    # Skaičiuojame max ir min kursus
    for currency in CURRENCY_MAP.values():
        max_rate = get_max_rate(currency, start_date_obj.strftime("%Y-%m-%d"), end_date_obj.strftime("%Y-%m-%d"))
        min_rate = get_min_rate(currency, start_date_obj.strftime("%Y-%m-%d"), end_date_obj.strftime("%Y-%m-%d"))
        print(f"{currency} Maks: {max_rate:.3f}, Min: {min_rate:.3f}")
        # išveda valiutos kodą ir vidutinį kursą, suapvalintą iki 4 skaičių po kablelio.
