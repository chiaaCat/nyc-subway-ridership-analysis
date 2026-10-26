import pandas as pd
from src.database import aggregate_station_hourly

def test_aggregate_station_hourly():
    df = pd.DataFrame({
        "transit_timestamp": [
            "2025-10-29T08:00:00Z",
            "2025-10-29T08:00:00Z",
            "2025-10-29T09:00:00Z",
            "2025-10-29T08:00:00Z"
        ],
        "station_complex_id": ["A", "A", "A", "B"],
        "station_complex": [
            "Station A", "Station A", "Station A", "Station B"
        ],
        "ridership": [120, 80, 150, 50]
    })

    result = aggregate_station_hourly(df)

    assert len(result) == 3

    station_a = result[
        (result["station_complex_id"] == "A") &
        (result["transit_timestamp"] == "2025-10-29T08:00:00Z")
    ]

    assert station_a["ridership"].iloc[0] == 200
    assert result["ridership"].sum() == 400
