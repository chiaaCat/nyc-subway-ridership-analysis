# NYC MTA Subway Ridership Analysis
This project analyzes NYC subway ridership patterns using MTA open data, python, MongoDB, and maching learning.

(*IN PROGRESS - Currently analyzes single day data.*)

Analysis specifically focuses on processing hourly ridership data, identifying stations with the highest traffic, and using K-Means clustering to understand differences in hourly activity across stations.

---
### Dataset

Data is retrieved from the [MTA Subway Hourly Ridership](https://data.ny.gov/Transportation/MTA-Subway-Hourly-Ridership-Beginning-2025/5wq4-mkjj/about_data) dataset. 

This analysis currently uses ridership data from *October 28th, 2025*.

* 84,387 records collected and cleaned
* 424 stations represented in clustering analysis
* Hourly ridership analyzed in NYC time (*EDT*)

---
### Current Features

#### Data Collection and Preprocessing
* Uses pagination to retrieve hourly subway ridership data
* Cleans invalid records, converts numeric fields, and standardizes timestamps
* Saves cleaned date to local CSV file

#### Data Storage
* Stores cleaned data in MongoDB Atlas using PyMongo
* Uses batch upserts and unique indices to prevent duplicate records
* Aggregates data directly in MongoDB

#### Ridership Analysis
* Calculates total recorded ridership for each station
* Identifies and ranks top ten stations with highest ridership

#### K-Means Clustering
* Creates 24-hour ridership profiles for 424 stations
* Normalizes hourly ridership by each station's total daily ridership
* Evaluates cluster counts using silhouette scores and inertia
* Applies K-Means clustering to identify differences in station activity patterns
* Visualizes average hourly ridership proportions for each cluster

#### Testing
* Uses pytest to test data preprocessing: *valid ridership, proper numeric and timestamp conversion, correct number of records*

---
### Future Development
* Expand dataset to include multiple days/weeks of ridership records
* Develop a neural network regression model to predict hourly station ridership using historical ridership patterns
* Evaluate regression model performance using MAE and RMSE
* Reevalute station clusters with expanded dataset
* Expand pytest coverage
* Add setup instructions for running the project locally