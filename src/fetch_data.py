import requests
import pandas as pd
from src.preprocessing import clean_ridership_data

URL = "https://data.ny.gov/resource/5wq4-mkjj.json"

# Fetch raw MTA ridership records
def fetch_ridership_data(start_date, end_date):

    all_records = []
    batch_size = 5000
    offset = 0

    with requests.Session() as session:
        while True:
            params = {
                "$where": (
                    f"transit_timestamp >= '{start_date}T00:00:00' "
                    f"AND transit_timestamp < '{end_date}T00:00:00' "
                    "AND transit_mode = 'subway'"
                ),
                "$order": ":id",
                "$limit": batch_size,
                "$offset": offset
            }

            response = session.get(
                URL,
                params=params,
                timeout=60
            )
            response.raise_for_status()

            batch = response.json()
            all_records.extend(batch)

            if len(batch) < batch_size:
                break

            offset += batch_size

    return pd.DataFrame(all_records)


if __name__ == "__main__":
    raw_data = fetch_ridership_data("2025-10-29", "2025-10-30")
    cleaned_data = clean_ridership_data(raw_data)

    print(f"Raw records: {len(raw_data):,}")
    print(f"Cleaned records: {len(cleaned_data):,}")

    cleaned_data.to_csv("data/subway_2025-10-29.csv", index=False)
    print("Saved cleaned data to data/subway_2025-10-29.csv")
