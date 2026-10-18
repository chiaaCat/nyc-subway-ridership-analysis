import pandas as pd
from src.database import get_database
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# Create hourly ridership profiles for each station
def create_station_features(db):

    collection = db["hourly_ridership"]

    pipeline = [
        {
            "$group": {
                "_id": {
                    "station_id": "$station_complex_id",
                    "station_name": "$station_complex",
                    "hour": {
                        "$hour": {
                            "date": "$transit_timestamp",
                            "timezone": "America/New_York"
                        }
                    }
                },
                "ridership": {"$sum": "$ridership"}
            }
        }
    ]

    results = list(collection.aggregate(pipeline))

    records = [
        {
            "station_id": item["_id"]["station_id"],
            "station_name": item["_id"]["station_name"],
            "hour": item["_id"]["hour"],
            "ridership": item["ridership"]
        }
        for item in results
    ]

    df = pd.DataFrame(records)

    features = df.pivot_table(
        index=["station_id", "station_name"],
        columns="hour",
        values="ridership",
        aggfunc="sum",
        fill_value=0
    )

    features = features.reindex(
        columns=range(24),
        fill_value=0
    )

    features.columns = [
        f"hour_{hour}" for hour in range(24)
    ]

    return features

# Convert hourly ridership into daily proportions
def normalize_station_features(features):

    daily_totals = features.sum(axis=1)

    # Exclude stations with zero total ridership
    valid_stations = daily_totals > 0

    features = features.loc[valid_stations]
    daily_totals = daily_totals.loc[valid_stations]

    normalized = features.div(daily_totals, axis=0)

    return normalized

# Evaluate different numbers of K-Means clusters
def evaluate_clusters(features):

    results = []

    for k in range(2, 9):
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(features)

        score = silhouette_score(features, labels)

        results.append({
            "k": k,
            "silhouette_score": score,
            "inertia": model.inertia_
        })

        print(
            f"k={k} | "
            f"Silhouette={score:.4f} | "
            f"Inertia={model.inertia_:.4f}"
        )

    return pd.DataFrame(results)

# Fit K-Means and analyze station clusters
def fit_final_clusters(features, k=2):

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(features)

    results = features.copy()
    results["cluster"] = labels

    print("Stations per cluster:")
    print(results["cluster"].value_counts())

    return model, results

# Visualize average hourly ridership
def plot_cluster_profiles(model):

    hours = range(24)

    plt.figure(figsize=(12, 5))

    for cluster, center in enumerate(model.cluster_centers_):
        plt.plot(
            hours,
            center,
            label=f"Cluster {cluster}"
        )

    plt.xlabel("Hour of Day")
    plt.ylabel("Proportion of Daily Ridership")
    plt.title("NYC Subway Station Ridership Patterns")
    plt.xticks(range(24))
    plt.legend()

    plt.savefig(
        "outputs/figures/cluster_profiles.png",
    )

    plt.show()


if __name__ == "__main__":
    db = get_database()

    features = create_station_features(db)
    normalized = normalize_station_features(features)

    evaluate_clusters(normalized)

    model, results = fit_final_clusters(normalized, k=2)
    plot_cluster_profiles(model)
