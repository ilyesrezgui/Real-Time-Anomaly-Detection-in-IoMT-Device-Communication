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

print(f"Model input shape: {model.input_shape}")
print(f"Model output shape: {model.output_shape}")
print(f"Number of features: {len(selected_features)}")
print(f"Threshold: {threshold}")
print()

# Create a test sample with all zeros (should reconstruct well if model is good)
test_normal = np.zeros((1, 31))
print("Test 1: All zeros (normalized)")
X_scaled = scaler.transform(test_normal)
X_reshaped = X_scaled.reshape((1, 1, 31))
X_reconstructed = model.predict(X_reshaped, verbose=0)
mse = np.mean(np.power(X_reshaped - X_reconstructed, 2))
print(f"  MSE: {mse}")
print(f"  Is anomaly (>{threshold}): {mse > threshold}")
print()

# Test with random values
test_random = np.random.rand(1, 31)
print("Test 2: Random values")
X_scaled = scaler.transform(test_random)
X_reshaped = X_scaled.reshape((1, 1, 31))
X_reconstructed = model.predict(X_reshaped, verbose=0)
mse = np.mean(np.power(X_reshaped - X_reconstructed, 2))
print(f"  MSE: {mse}")
print(f"  Is anomaly (>{threshold}): {mse > threshold}")
print()

# Test with extreme values (likely anomaly)
test_extreme = np.ones((1, 31)) * 1000
print("Test 3: Extreme values (before scaling)")
X_scaled = scaler.transform(test_extreme)
X_reshaped = X_scaled.reshape((1, 1, 31))
X_reconstructed = model.predict(X_reshaped, verbose=0)
mse = np.mean(np.power(X_reshaped - X_reconstructed, 2))
print(f"  MSE: {mse}")
print(f"  Is anomaly (>{threshold}): {mse > threshold}")
print()

# Check scaler range
print("Scaler info:")
print(f"  data_min_: {scaler.data_min_[:5]}...")  # First 5 values
print(f"  data_max_: {scaler.data_max_[:5]}...")
print(f"  feature_range: {scaler.feature_range}")
