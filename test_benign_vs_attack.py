import pandas as pd
import json
import joblib
import numpy as np
from tensorflow import keras

# Load models
scaler = joblib.load('Models/scaler.pkl')
with open('Models/numeric_features.json', 'r') as f:
    numeric_features = json.load(f)
with open('Models/threshold.json', 'r') as f:
    threshold = json.load(f)['threshold']
model = keras.models.load_model('Models/Chaima/lstm_autoencoder.h5')

# Find BENIGN records
df = pd.read_csv('data.csv')
benign = df[df['Label'] == 'BENIGN'].head(5)
attacks = df[df['Label'] != 'BENIGN'].head(5)

print(f'Threshold: {threshold}')
print()

print('Testing BENIGN records:')
for i, (_, record) in enumerate(benign.iterrows()):
    feature_values = [float(record.get(f, 0.0) or 0.0) for f in numeric_features]
    X = np.array([feature_values])
    X_scaled = scaler.transform(X)
    X_reshaped = X_scaled.reshape((1, 1, 31))
    X_reconstructed = model.predict(X_reshaped, verbose=0)
    mse = np.mean(np.power(X_reshaped - X_reconstructed, 2))
    print(f'  {i+1}. MSE: {mse:.4f}, Anomaly: {mse > threshold}')

print()
print('Testing ATTACK records:')
for i, (_, record) in enumerate(attacks.iterrows()):
    label = record['Label']
    feature_values = [float(record.get(f, 0.0) or 0.0) for f in numeric_features]
    X = np.array([feature_values])
    X_scaled = scaler.transform(X)
    X_reshaped = X_scaled.reshape((1, 1, 31))
    X_reconstructed = model.predict(X_reshaped, verbose=0)
    mse = np.mean(np.power(X_reshaped - X_reconstructed, 2))
    print(f'  {i+1}. {label}: MSE: {mse:.4f}, Anomaly: {mse > threshold}')
