from unittest.mock import patch
from src.fetch_data import fetch_ridership_data

def test_fetch_ridership_dates():
    with patch("src.fetch_data.requests.Session") as mock_session:
        session = mock_session.return_value.__enter__.return_value
        session.get.return_value.json.return_value = []

        fetch_ridership_data("2025-10-29", "2025-10-30")

        params = session.get.call_args.kwargs["params"]

        assert "2025-10-29T00:00:00" in params["$where"]
        assert "2025-10-30T00:00:00" in params["$where"]
        assert "transit_mode = 'subway'" in params["$where"]
