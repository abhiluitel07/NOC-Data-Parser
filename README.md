# NOC Data Parser

A Python script that scrapes historical petrol, diesel, and LPG retail prices published by the **Nepal Oil Corporation (NOC)** and compiles them into a clean, gap-filled CSV time series.

## What it does

Nepal Oil Corporation publishes retail price change notices on its website, but there's no ready-made dataset of prices by date. This script:

1. **Scrapes** the NOC retail price page (`noc.org.np/retailprice`), paging through results 10 at a time until no more records are found.
2. **Parses** each row to extract the effective date and the petrol, diesel, and LPG prices.
3. **Cleans** the data — validating dates (from 2017-01-01 to today) and converting prices to floats, skipping any malformed rows.
4. **Fills gaps** by forward-filling prices for every single day between the earliest recorded date and today (since prices only change occasionally but stay in effect until the next change).
5. **Exports** the result to `petrol_and_diesel_prices_filled.csv`, giving you one row per day with no missing dates.

## Output format

The generated CSV (`petrol_and_diesel_prices_filled.csv`) has the following columns:

| Column | Description |
|---|---|
| `Date` | Calendar date (YYYY-MM-DD) |
| `Petrol_Price` | Petrol price in effect on that date (NPR) |
| `Diesel_Price` | Diesel price in effect on that date (NPR) |
| `LPG` | LPG price in effect on that date (NPR) |

Because prices are forward-filled, every date in the range has a value — useful for plotting trends, joining with other daily datasets, or feeding into analysis/ML pipelines without having to handle missing values yourself.

## Requirements

- Python 3.7+
- [requests](https://pypi.org/project/requests/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)

Install dependencies:

```bash
pip install requests beautifulsoup4
```

## Usage

Run the script directly:

```bash
python DatePrices.py
```

It will:
- Query the NOC website in batches of 10 records (with a 1-second delay between requests to be polite to the server)
- Stop automatically once it reaches the end of the available records
- Write the final, day-by-day filled dataset to `petrol_and_diesel_prices_filled.csv` in the same directory

No arguments or configuration are needed — just run it and wait for it to finish (runtime depends on how many price-change records NOC has published).

## How it works (implementation notes)

- **Scraping loop**: Increments an `offset` query parameter and stops when a request fails or returns no table rows.
- **Date extraction**: Uses a regex (`\d{4}\.\d{2}\.\d{2}`) to pull dates in `YYYY.MM.DD` format out of the raw table text.
- **Date range validation**: Only keeps records between `2017-01-01` and the current date, discarding anything that fails to parse.
- **Forward-fill**: Builds a `date -> price` lookup, then walks day-by-day from the first known date to today, carrying the last known price forward whenever a given day has no explicit price change on record.

## Notes & limitations

- The script depends on the current HTML structure of the NOC retail price page. If NOC changes their table layout or column order, the column indices (`cols[0]`, `cols[2]`, `cols[3]`, `cols[5]`) may need to be updated.
- There's no error handling/retry logic for network failures beyond stopping on a non-200 response — re-run the script if a request fails partway through.
- The script exits silently (via `exit()`) if no valid data is scraped.

## License

No license specified yet — consider adding one (e.g. MIT) if you'd like others to reuse this code.
