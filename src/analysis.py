from src.database import get_database

# Find stations with the highest ridership in sample
def top_stations(db, limit=10):

    collection = db["hourly_ridership"]

    pipeline = [
        {
            "$group": {
                "_id": {
                    "station_id": "$station_complex_id",
                    "station_name": "$station_complex"
                },
                "total_ridership": {"$sum": "$ridership"},
                "records": {"$sum": 1}
            }
        },
        {
            "$sort": {"total_ridership": -1}
        },
        {
            "$limit": limit
        }
    ]

    return list(collection.aggregate(pipeline))


if __name__ == "__main__":
    db = get_database()
    results = top_stations(db)

    print("Top 10 subway stations by ridership:\n")

    for rank, station in enumerate(results, start=1):
        name = station["_id"]["station_name"]
        ridership = station["total_ridership"]
        print(f"{rank}. {name}: {ridership:,.1f} riders")