import pandas as pd
from pymongo import ASCENDING, UpdateOne
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Connect to NYC subway MongoDB database
def get_database():

    uri = os.getenv("MONGO_URI")

    if not uri:
        raise ValueError("MONGO_URI is missing from .env")

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=10000
    )

    client.admin.command("ping")

    return client["nyc_subway"]

# Insert clean data into MongoDB

def insert_ridership_data(db, csv_path, batch_size=1000):

    df = pd.read_csv(
        csv_path,
        dtype={"station_complex_id": str}
    )

    df["transit_timestamp"] = pd.to_datetime(
        df["transit_timestamp"],
        utc=True
    )

    collection = db["hourly_ridership"]

    collection.create_index(
        [
            ("transit_timestamp", ASCENDING),
            ("station_complex_id", ASCENDING),
            ("payment_method", ASCENDING),
            ("fare_class_category", ASCENDING)
        ],
        unique=True
    )

    total_processed = 0

    for start in range(0, len(df), batch_size):
        batch = df.iloc[start:start + batch_size]
        operations = []

        for record in batch.to_dict("records"):
            record["transit_timestamp"] = (
                record["transit_timestamp"].to_pydatetime()
            )
            record["ridership"] = float(record["ridership"])
            record["transfers"] = float(record["transfers"])
            record["latitude"] = float(record["latitude"])
            record["longitude"] = float(record["longitude"])
            record.pop("georeference", None)

            identifier = {
                "transit_timestamp": record["transit_timestamp"],
                "station_complex_id": record["station_complex_id"],
                "payment_method": record["payment_method"],
                "fare_class_category": record["fare_class_category"]
            }

            operations.append(
                UpdateOne(
                    identifier,
                    {"$set": record},
                    upsert=True
                )
            )

        if operations:
            collection.bulk_write(
                operations,
                ordered=False
            )

        total_processed += len(batch)

    return collection.count_documents({})


if __name__ == "__main__":
    db = get_database()

    total = insert_ridership_data(
        db,
        "data/subway_test.csv"
    )

    print(f"Total MongoDB records: {total:,}")
