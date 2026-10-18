import pandas as pd

# Clean and standardize raw ridership records
def clean_ridership_data(df: pd.DataFrame) -> pd.DataFrame:

    cleaned = df.copy()

    # Convert timestamp strings into datetime objects
    cleaned["transit_timestamp"] = (
        pd.to_datetime(
            cleaned["transit_timestamp"],
            errors="coerce"
        )
        .dt.tz_localize(
            "America/New_York",
            ambiguous="NaT",
            nonexistent="NaT"
        )
        .dt.tz_convert("UTC")
    )

    # Convert numeric fields
    numeric_columns = [
        "ridership",
        "transfers",
        "latitude",
        "longitude"
    ]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(
            cleaned[column],
            errors="coerce"
        )

    # Remove records missing important information
    cleaned = cleaned.dropna(
        subset=[
            "transit_timestamp",
            "station_complex_id",
            "ridership",
            "latitude",
            "longitude"
        ]
    )

    # Remove invalid ridership values
    cleaned = cleaned[cleaned["ridership"] >= 0]

    cleaned = cleaned.reset_index(drop=True)

    return cleaned
