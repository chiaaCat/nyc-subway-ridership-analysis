import pandas as pd
from src.fetch_data import fetch_ridership_data
from src.preprocessing import clean_ridership_data
from src.database import get_database, insert_station_hourly_data

def main():
    db = get_database()

    for date in pd.date_range("2025-10-20", "2025-10-31"):
        start_date = date.strftime("%Y-%m-%d")
        end_date = (date + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

        raw = fetch_ridership_data(start_date, end_date)
        cleaned = clean_ridership_data(raw)

        csv_path = f"data/subway_{start_date}.csv"
        cleaned.to_csv(csv_path, index=False)

        total = insert_station_hourly_data(db, csv_path)

        print(f"{start_date}: {len(cleaned):,} records")
        print(f"Total records: {total:,}")


if __name__ == "__main__":
    main()