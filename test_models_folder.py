import pandas as pd
import json
import joblib
import numpy as np
from tensorflow import keras

# Load from Models/ folder (not Spark/)
scaler = joblib.load('Models/scaler.pkl')
with open('Models/numeric_features.json', 'r') as f:
    numeric_features = json.load(f)
with open('Models/threshold.json', 'r') as f:
    threshold_data = json.load(f)
    threshold = threshold_data['threshold']
model = keras.models.load_model('Models/Chaima/lstm_autoencoder.h5')

print(f"Numeric features ({len(numeric_features)}): {numeric_features[:10]}...")
print(f"Threshold: {threshold}")
print()

# Load sample data
df = pd.read_csv('data.csv', nrows=10)
print("CSV columns:", len(df.columns), "columns")

# Check which features match
csv_cols = set(df.columns)
missing_features = [f for f in numeric_features if f not in csv_cols]
print(f"Missing features: {missing_features}")
print()

# Test with first 3 records
for i in range(min(3, len(df))):
    record = df.iloc[i].to_dict()

    # Extract features - direct match
    feature_values = []
    for feature in numeric_features:
        value = record.get(feature, 0.0)
        if value is None:
            value = 0.0
        feature_values.append(float(value))

    # Count zeros
    zero_count = feature_values.count(0.0)

    # Run through model
    X = np.array([feature_values])
    X_scaled = scaler.transform(X)
    X_reshaped = X_scaled.reshape((1, 1, 31))
    X_reconstructed = model.predict(X_reshaped, verbose=0)
    mse = np.mean(np.power(X_reshaped - X_reconstructed, 2))

    is_anomaly = mse > threshold
    label = record.get('Label', 'N/A')

    print(f"Record {i+1}:")
    print(f"  Label: {label}")
    print(f"  Zeros in features: {zero_count}/31")
    print(f"  MSE: {mse:.6f}")
    print(f"  Predicted: {'ANOMALY' if is_anomaly else 'NORMAL'}")
    print()
