import pandas as pd
from src.preprocessing import clean_ridership_data

def test_clean_ridership_data():
    raw_data = pd.DataFrame({
        "transit_timestamp": [
            "2025-05-23T00:00:00.000",
            "2025-05-23T01:00:00.000"
        ],
        "station_complex_id": ["100", "101"],
        "ridership": ["12.0", "-5.0"],
        "transfers": ["0.0", "2.0"],
        "latitude": ["40.70687", "40.70700"],
        "longitude": ["-73.95343", "-73.95400"]
    })

    cleaned = clean_ridership_data(raw_data)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["ridership"] == 12.0
    assert pd.api.types.is_datetime64_any_dtype(
        cleaned["transit_timestamp"]
    )
    assert pd.api.types.is_numeric_dtype(
        cleaned["ridership"]
    )
    assert pd.api.types.is_numeric_dtype(
        cleaned["latitude"]
    )
