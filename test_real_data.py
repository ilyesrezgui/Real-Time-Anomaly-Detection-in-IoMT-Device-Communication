import pandas as pd
import json
import joblib
import numpy as np
from tensorflow import keras

# Load model files
scaler = joblib.load('Spark/scaler.pkl')
with open('Spark/selected_features.json', 'r') as f:
    selected_features = json.load(f)
with open('Models/Chaima/threshold.json', 'r') as f:
    threshold_data = json.load(f)
    threshold = threshold_data['threshold']
model = keras.models.load_model('Models/Chaima/lstm_autoencoder.h5')

print(f"Selected features ({len(selected_features)}): {selected_features}")
print()

# Load a sample from the CSV
df = pd.read_csv('data.csv', nrows=5)
print("CSV columns:", list(df.columns))
print()

# Check which features are missing
csv_cols = set(df.columns)
missing_features = [f for f in selected_features if f not in csv_cols]
print(f"Missing features ({len(missing_features)}): {missing_features}")
print()

# Take first record
record = df.iloc[0].to_dict()
print("Sample record (first 10 fields):")
for i, (k, v) in enumerate(list(record.items())[:10]):
    print(f"  {k}: {v}")
print()

# Extract features like the consumer does
feature_values = []
for feature in selected_features:
    if feature == "flow_duration":
        value = record.get("Duration", 0.0)
    elif feature == "Duration":
        value = record.get("Duration", 0.0)
    elif feature == "urg_count":
        value = record.get("urg_count", 0)
    elif feature == "Covariance":
        value = record.get("Covariance", 0.0)
    else:
        value = record.get(feature, 0.0)

    if value is None:
        value = 0.0
    feature_values.append(float(value))

print("Extracted feature values (first 10):", feature_values[:10])
print(f"Number of zeros in features: {feature_values.count(0.0)} out of {len(feature_values)}")
print()

# Run through model
X = np.array([feature_values])
X_scaled = scaler.transform(X)
X_reshaped = X_scaled.reshape((1, 1, 31))
X_reconstructed = model.predict(X_reshaped, verbose=0)
mse = np.mean(np.power(X_reshaped - X_reconstructed, 2))

print(f"MSE: {mse}")
print(f"Threshold: {threshold}")
print(f"Is anomaly: {mse > threshold}")
print(f"Label in data: {record.get('Label', 'N/A')}")
