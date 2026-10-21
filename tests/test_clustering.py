import pandas as pd
import pytest
from unittest.mock import MagicMock
from src.clustering import create_station_features
from src.clustering import normalize_station_features

def test_create_station_features():
    db = MagicMock()

    db["hourly_ridership"].aggregate.return_value = [
        {
            "_id": {
                "station_id": "A",
                "station_name": "Station A",
                "hour": 8
            },
            "ridership": 100
        },
        {
            "_id": {
                "station_id": "A",
                "station_name": "Station A",
                "hour": 17
            },
            "ridership": 200
        },
        {
            "_id": {
                "station_id": "B",
                "station_name": "Station B",
                "hour": 8
            },
            "ridership": 50
        }
    ]

    features = create_station_features(db)

    assert features.shape == (2, 24)
    assert features.loc[("A", "Station A"), "hour_8"] == 100
    assert features.loc[("A", "Station A"), "hour_17"] == 200
    assert features.loc[("B", "Station B"), "hour_8"] == 50
    assert features.loc[("B", "Station B"), "hour_17"] == 0

def test_normalize_station_features():
    features = pd.DataFrame({
        "hour_0": [100],
        "hour_1": [200],
        "hour_2": [100]
    })

    normalized = normalize_station_features(features)

    assert normalized["hour_0"].iloc[0] == pytest.approx(0.25)
    assert normalized["hour_1"].iloc[0] == pytest.approx(0.50)
    assert normalized["hour_2"].iloc[0] == pytest.approx(0.25)
    assert normalized.iloc[0].sum() == pytest.approx(1.0)

def test_zero_ridership_stations():
    features = pd.DataFrame({
        "hour_0": [100, 0],
        "hour_1": [200, 0],
        "hour_2": [100, 0]
    })

    normalized = normalize_station_features(features)

    assert len(normalized) == 1
    assert normalized.iloc[0].sum() == pytest.approx(1.0)
