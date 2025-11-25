"""
Script to verify model, scaler, features, and threshold files
"""
import json
import joblib
import numpy as np
from tensorflow import keras

# File paths
SCALER_PATH = 'scaler.pkl'
MODEL_PATH = '../Models/Chaima/lstm_autoencoder.h5'
FEATURES_PATH = 'selected_features.json'
THRESHOLD_PATH = '../Models/Chaima/threshold.json'

def check_scaler():
    """Check the scaler"""
    print("\n" + "="*70)
    print("CHECKING SCALER")
    print("="*70)
    try:
        scaler = joblib.load(SCALER_PATH)
        print(f"✓ Scaler loaded successfully from {SCALER_PATH}")
        print(f"  Type: {type(scaler).__name__}")
        
        # Check scaler properties
        if hasattr(scaler, 'n_features_in_'):
            print(f"  Number of features: {scaler.n_features_in_}")
        if hasattr(scaler, 'mean_'):
            print(f"  Mean shape: {scaler.mean_.shape}")
        if hasattr(scaler, 'scale_'):
            print(f"  Scale shape: {scaler.scale_.shape}")
        
        return scaler
    except Exception as e:
        print(f"✗ Error loading scaler: {e}")
        return None

def check_model():
    """Check the LSTM model"""
    print("\n" + "="*70)
    print("CHECKING LSTM MODEL")
    print("="*70)
    try:
        model = keras.models.load_model(MODEL_PATH)
        print(f"✓ Model loaded successfully from {MODEL_PATH}")
        print(f"\nModel Summary:")
        print("-" * 70)
        model.summary()
        print("-" * 70)
        print(f"\n  Input shape: {model.input_shape}")
        print(f"  Output shape: {model.output_shape}")
        
        # Extract important details
        input_shape = model.input_shape
        if len(input_shape) == 3:
            print(f"\n  Expected input format: (batch_size, {input_shape[1]}, {input_shape[2]})")
            print(f"  Timesteps: {input_shape[1]}")
            print(f"  Features per timestep: {input_shape[2]}")
        
        return model
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return None

def check_features():
    """Check the selected features"""
    print("\n" + "="*70)
    print("CHECKING SELECTED FEATURES")
    print("="*70)
    try:
        with open(FEATURES_PATH, 'r') as f:
            selected_features = json.load(f)
        print(f"✓ Features loaded successfully from {FEATURES_PATH}")
        print(f"  Type: {type(selected_features)}")
        print(f"  Number of features: {len(selected_features)}")
        print(f"\n  First 10 features:")
        for i, feature in enumerate(selected_features[:10], 1):
            print(f"    {i}. {feature}")
        
        if len(selected_features) > 10:
            print(f"    ... and {len(selected_features) - 10} more features")
        
        return selected_features
    except Exception as e:
        print(f"✗ Error loading features: {e}")
        return None

def check_threshold():
    """Check the threshold"""
    print("\n" + "="*70)
    print("CHECKING THRESHOLD")
    print("="*70)
    try:
        with open(THRESHOLD_PATH, 'r') as f:
            threshold_data = json.load(f)
        print(f"✓ Threshold loaded successfully from {THRESHOLD_PATH}")
        print(f"  Raw data: {threshold_data}")
        print(f"  Type: {type(threshold_data)}")
        
        # Try to extract threshold value
        if isinstance(threshold_data, dict):
            threshold = threshold_data.get('threshold', threshold_data.get('anomaly_threshold', None))
            print(f"  Extracted threshold: {threshold}")
        else:
            threshold = float(threshold_data)
            print(f"  Threshold value: {threshold}")
        
        return threshold
    except Exception as e:
        print(f"✗ Error loading threshold: {e}")
        return None

def verify_compatibility(scaler, model, selected_features):
    """Verify that scaler, model, and features are compatible"""
    print("\n" + "="*70)
    print("VERIFYING COMPATIBILITY")
    print("="*70)
    
    if scaler is None or model is None or selected_features is None:
        print("✗ Cannot verify compatibility - some artifacts are missing")
        return False
    
    try:
        # Check if number of features matches
        n_features = len(selected_features)
        
        # Check scaler
        if hasattr(scaler, 'n_features_in_'):
            if scaler.n_features_in_ != n_features:
                print(f"✗ WARNING: Scaler expects {scaler.n_features_in_} features, but selected_features has {n_features}")
            else:
                print(f"✓ Scaler and features are compatible ({n_features} features)")
        
        # Check model input shape
        input_shape = model.input_shape
        if len(input_shape) == 3:
            expected_features = input_shape[2]
            if expected_features != n_features:
                print(f"✗ WARNING: Model expects {expected_features} features, but selected_features has {n_features}")
            else:
                print(f"✓ Model and features are compatible ({n_features} features)")
        
        # Test with dummy data
        print("\nTesting with dummy data...")
        dummy_features = np.random.rand(1, n_features)
        
        # Test scaler
        scaled_features = scaler.transform(dummy_features)
        print(f"  ✓ Scaler transform successful: {dummy_features.shape} -> {scaled_features.shape}")
        
        # Test model
        reshaped_features = scaled_features.reshape((scaled_features.shape[0], 1, scaled_features.shape[1]))
        prediction = model.predict(reshaped_features, verbose=0)
        print(f"  ✓ Model prediction successful: {reshaped_features.shape} -> {prediction.shape}")
        
        # Calculate reconstruction error
        reconstruction_error = np.mean(np.square(reshaped_features - prediction))
        print(f"  ✓ Reconstruction error calculated: {reconstruction_error}")
        
        print("\n✓ ALL COMPATIBILITY CHECKS PASSED!")
        return True
        
    except Exception as e:
        print(f"✗ Compatibility check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("\n" + "="*70)
    print("MODEL AND FEATURES VERIFICATION TOOL")
    print("="*70)
    
    # Check each component
    scaler = check_scaler()
    model = check_model()
    features = check_features()
    threshold = check_threshold()
    
    # Verify compatibility
    verify_compatibility(scaler, model, features)
    
    print("\n" + "="*70)
    print("VERIFICATION COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()