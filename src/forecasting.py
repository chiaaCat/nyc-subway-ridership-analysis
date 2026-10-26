import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.database import get_database
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error

def load_forecasting_data(db):
    collection = db["station_hourly_ridership"]

    records = list(collection.find(
        {},
        {
            "_id": 0,
            "transit_timestamp": 1,
            "station_complex_id": 1,
            "station_complex": 1,
            "ridership": 1
        }
    ))

    df = pd.DataFrame(records)

    df["transit_timestamp"] = pd.to_datetime(
        df["transit_timestamp"],
        utc=True
    )

    return df

def create_forecasting_features(df):
    df = df.copy()

    df = df.sort_values(
        ["station_complex_id", "transit_timestamp"]
    )

    local_time = df["transit_timestamp"].dt.tz_convert(
        "America/New_York"
    )

    df["hour"] = local_time.dt.hour
    df["day_of_week"] = local_time.dt.dayofweek

    for hours, column in [(1, "previous_hour"), (24, "previous_day")]:
        history = df[
            ["station_complex_id", "transit_timestamp", "ridership"]
        ].copy()

        history["transit_timestamp"] += pd.Timedelta(hours=hours)
        history = history.rename(columns={"ridership": column})

        df = df.merge(
            history,
            on=["station_complex_id", "transit_timestamp"],
            how="left"
        )

    df = df.dropna(subset=["previous_hour", "previous_day"])

    return df

def train_forecasting_model(df):

    feature_columns = [
        "station_complex_id",
        "hour",
        "day_of_week",
        "previous_hour",
        "previous_day"
    ]

    local_time = df["transit_timestamp"].dt.tz_convert(
        "America/New_York"
    )

    train = df[local_time < "2025-10-30"]
    test = df[local_time >= "2025-10-30"]

    X_train = train[feature_columns]
    X_test = test[feature_columns]

    y_train = train["ridership"]
    y_test = test["ridership"]

    preprocessing = ColumnTransformer([
        ("station", OneHotEncoder(handle_unknown="ignore"),
         ["station_complex_id"]),
        ("numeric", StandardScaler(),
         ["hour", "day_of_week", "previous_hour", "previous_day"])
    ])

    model = Pipeline([
        ("preprocessing", preprocessing),
        ("neural_network", MLPRegressor(
            hidden_layer_sizes=(100,),
            max_iter=300,
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)

    predictions = np.maximum(model.predict(X_test), 0)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    baseline = test["previous_day"]
    baseline_mae = mean_absolute_error(y_test, baseline)
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline))

    print(f"Training records: {len(train):,}")
    print(f"Testing records: {len(test):,}")

    print(f"Neural network MAE: {mae:.2f}")
    print(f"Neural network RMSE: {rmse:.2f}")

    print(f"Baseline MAE: {baseline_mae:.2f}")
    print(f"Baseline RMSE: {baseline_rmse:.2f}")

    return model, test, predictions

def plot_forecasting_results(test, predictions):

    results = test.copy()
    results["predicted"] = predictions

    station_id = results.loc[
        results["station_complex"].str.contains("Times Sq", case=False, na=False),
        "station_complex_id"
    ].iloc[0]

    station = results[
        results["station_complex_id"] == station_id
    ].sort_values("transit_timestamp")

    local_time = station["transit_timestamp"].dt.tz_convert(
        "America/New_York"
    )

    plt.figure(figsize=(12, 5))

    plt.plot(
        local_time,
        station["ridership"],
        label="Actual"
    )

    plt.plot(
        local_time,
        station["predicted"],
        label="Predicted"
    )

    plt.xlabel("Time")
    plt.ylabel("Hourly Ridership")
    plt.title(f"Hourly Subway Ridership: {station['station_complex'].iloc[0]}")
    plt.legend()

    plt.savefig(
        "outputs/figures/forecasting_results.png",
    )
    plt.show()


if __name__ == "__main__":
    db = get_database()

    df = load_forecasting_data(db)
    features = create_forecasting_features(df)

    model, test, predictions = train_forecasting_model(features)

    plot_forecasting_results(test, predictions)
