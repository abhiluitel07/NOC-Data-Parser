import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import re
import csv

scraped_data = []
cleaned_data = []

url_offset = 0

while True:
    url = f"https://noc.org.np/retailprice?offset={url_offset}&max=10"
    response = requests.get(url)

    if response.status_code != 200:
        break

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    rows = tables[0].find("tbody").find_all("tr")

    if not rows:
        break

    for row in rows:
        cols = row.find_all("td")

        if len(cols) > 0:
            date_text = cols[0].text.strip()
            petrol = cols[2].text.strip()
            diesel = cols[3].text.strip()
            LPG = cols[5].text.strip()

            scraped_data.append((date_text, petrol, diesel, LPG))

    url_offset += 10
    time.sleep(1)

today = datetime.today().date()

for entry in scraped_data:
    dates = re.findall(r'\d{4}\.\d{2}\.\d{2}', entry[0])

    for date_str in dates:
        try:
            date_obj = datetime.strptime(date_str, "%Y.%m.%d").date()

            if datetime(2017, 1, 1).date() <= date_obj <= today:
                cleaned_data.append({
                    "date": date_obj,
                    "petrol_price": float(entry[1]),
                    "diesel_price": float(entry[2]),
                    "LPG": float(entry[3])
                })

        except ValueError:
            pass

if not cleaned_data:
    exit()

cleaned_data.sort(key=lambda x: x['date'])

start_date = cleaned_data[0]['date']
end_date = today
current_date = start_date

price_map = {item['date']: (item['petrol_price'], item['diesel_price'], item['LPG']) for item in cleaned_data}

last_known_price = None

with open("petrol_and_diesel_prices_filled.csv", "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow(["Date", "Petrol_Price", "Diesel_Price", "LPG"])

    while current_date <= end_date:
        if current_date in price_map:
            last_known_price = price_map[current_date]

        writer.writerow([current_date, last_known_price[0], last_known_price[1], last_known_price[2]])

        current_date += timedelta(days=1)