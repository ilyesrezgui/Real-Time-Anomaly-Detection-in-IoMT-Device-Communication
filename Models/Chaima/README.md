# Models/Chaima - LSTM Autoencoder Training Pipeline

This directory contains the complete pipeline for training the LSTM Autoencoder model used for IoMT anomaly detection.

## Overview

This module implements an **unsupervised anomaly detection** approach using an LSTM Autoencoder trained exclusively on benign traffic patterns. The model learns to reconstruct normal network behavior, and anomalies are detected based on high reconstruction errors.

## Directory Contents

### Python Scripts

#### 1. `dataset_loader.py`
**Purpose**: Load and prepare the IoMT network traffic dataset

**What it does**:
- Loads the raw CSV dataset
- Splits data into training, validation, and test sets
- Handles data paths and file I/O
- Provides consistent data access for the training pipeline

**Usage**:
```python
from dataset_loader import load_dataset
train, val, test = load_dataset()
```

---

#### 2. `feature_selection.py`
**Purpose**: Select the most relevant features for anomaly detection

**What it does**:
- Analyzes feature importance and correlation
- Removes redundant or low-variance features
- Selects 31 critical features from the original dataset
- Saves selected features for production use

**Output**: `numeric_features.json` (31 features)

**Usage**:
```python
from feature_selection import select_features
selected_features = select_features(dataframe)
```

---

#### 3. `preprocess.py`
**Purpose**: Data preprocessing and normalization

**What it does**:
- **Filters training data**: Keeps only benign traffic (`label == "BenignTraffic"`)
- **Cleans data**: Removes NaN, infinity values
- **Normalization**: Applies StandardScaler (mean=0, std=1)
- **Saves scaler**: Exports `scaler.pkl` for production use

**Key Functions**:
- `clean_dataset(df)`: Handle missing/invalid values
- `preprocess(train, val, test)`: Complete preprocessing pipeline

**Output**:
- Scaled training/validation/test sets
- `scaler.pkl` → copied to `Spark/scaler.pkl`

**Usage**:
```python
from preprocess import preprocess
X_train, X_val, X_test, features = preprocess(train, val, test, base_path)
```

---

#### 4. `LSTMAE_model.py`
**Purpose**: Define the LSTM Autoencoder architecture

**What it does**:
- Defines the neural network architecture
- Implements encoder (compression) and decoder (reconstruction)
- Configures layer dimensions and activation functions

**Architecture**:
```
Input (31 features)
    ↓
Encoder:
  - LSTM(64) → LSTM(32) → LSTM(16)
    ↓
Bottleneck (16-dimensional latent space)
    ↓
Decoder:
  - RepeatVector → LSTM(16) → LSTM(32) → Dense(31)
    ↓
Output (31 reconstructed features)
```

**Model Specs**:
- Input shape: `(None, 1, 31)`
- Output shape: `(None, 1, 31)`
- Latent dimension: 16
- Total parameters: ~50K
- Optimizer: Adam
- Loss function: Mean Squared Error (MSE)

**Usage**:
```python
from LSTMAE_model import create_lstm_autoencoder
model = create_lstm_autoencoder(input_dim=31)
```

---

#### 5. `train.py`
**Purpose**: Main training script - orchestrates the entire pipeline

**What it does**:
1. Loads dataset using `dataset_loader.py`
2. Selects features using `feature_selection.py`
3. Preprocesses data using `preprocess.py`
4. Builds model using `LSTMAE_model.py`
5. Trains the model on benign traffic only
6. Validates and calculates optimal threshold
7. Saves trained artifacts

**Training Configuration**:
- Epochs: 50-100 (with early stopping)
- Batch size: 256
- Validation split: 20%
- Early stopping: patience=10

**Threshold Calculation**:
- Computes reconstruction errors on validation set
- Sets threshold at 95th percentile of benign errors
- Ensures low false negative rate

**Outputs**:
- `lstm_autoencoder.h5`: Trained model weights
- `threshold.json`: Optimal detection threshold
- `scaler.pkl`: Feature scaler
- `numeric_features.json`: Selected features list

**Usage**:
```bash
python train.py
```

---

### Model Artifacts

#### 1. `lstm_autoencoder.h5`
**Type**: Keras/TensorFlow model file (HDF5 format)

**Size**: ~500 KB - 2 MB (depending on architecture)

**Contents**:
- Complete trained LSTM Autoencoder model
- Layer weights and biases
- Model architecture configuration
- Optimizer state

**Loading**:
```python
from tensorflow import keras
model = keras.models.load_model('lstm_autoencoder.h5')
```

**Used by**: `Spark/consumer.py` for real-time inference

---

#### 2. `scaler.pkl`
**Type**: Scikit-learn StandardScaler (pickled object)

**Size**: ~10-50 KB

**Contents**:
- Feature means (μ) for each of 31 features
- Feature standard deviations (σ) for each feature
- Scaling parameters fitted on benign training data

**Purpose**:
- Normalize incoming data: `z = (x - μ) / σ`
- Ensures production data matches training distribution

**Loading**:
```python
import joblib
scaler = joblib.load('scaler.pkl')
X_scaled = scaler.transform(X)
```

**Copied to**: `Spark/scaler.pkl` for production use

---

#### 3. `threshold.json`
**Type**: JSON configuration file

**Contents**:
```json
{
  "threshold": 0.14352912117078315
}
```

**Purpose**:
- Decision boundary for anomaly classification
- If `reconstruction_error > threshold` → Anomaly
- If `reconstruction_error ≤ threshold` → Normal

**Calculation**:
- Based on 95th percentile of reconstruction errors on benign validation data
- Balances sensitivity vs. specificity

**Loading**:
```python
import json
with open('threshold.json', 'r') as f:
    threshold = json.load(f)['threshold']
```

---

#### 4. `numeric_features.json`
**Type**: JSON array

**Contents**: List of 31 selected feature names

**Features included**:
```json
[
  "Header_Length", "Protocol Type", "Time_To_Live", "Rate",
  "fin_flag_number", "syn_flag_number", "psh_flag_number",
  "ack_flag_number", "ece_flag_number", "cwr_flag_number",
  "HTTP", "HTTPS", "DNS", "Telnet", "SMTP", "SSH", "IRC",
  "TCP", "UDP", "DHCP", "ARP", "ICMP", "IGMP",
  "Tot sum", "Min", "Max", "AVG", "Std", "IAT",
  "Number", "Variance"
]
```

**Purpose**:
- Documents which features are used for training
- Ensures consistent feature selection across pipeline
- Reference for feature engineering

---

## Training Pipeline Workflow

```
┌─────────────────┐
│ dataset_loader  │ → Load raw data
└────────┬────────┘
         ↓
┌─────────────────┐
│feature_selection│ → Select 31 features
└────────┬────────┘
         ↓
┌─────────────────┐
│   preprocess    │ → Clean, scale (benign only)
└────────┬────────┘
         ↓
┌─────────────────┐
│  LSTMAE_model   │ → Define architecture
└────────┬────────┘
         ↓
┌─────────────────┐
│     train       │ → Train model
└────────┬────────┘
         ↓
    Save artifacts:
    ├── lstm_autoencoder.h5
    ├── scaler.pkl
    ├── threshold.json
    └── numeric_features.json
```

---

## Model Performance

**Dataset**: 10,000 test samples

**Metrics**:
- **Accuracy**: 98.3%
- **Sensitivity (TPR)**: 99.5%
- **Specificity (TNR)**: 90.5%
- **False Positive Rate**: 9.5%
- **False Negative Rate**: 0.5%

**Confusion Matrix**:
```
                Predicted
              Normal  Anomaly
Actual Normal   1,187    125
       Anomaly     43  8,645
```

---

## Integration with Production

The trained artifacts are copied to the `Spark/` directory for deployment:

1. **Copy model to Spark**:
   ```bash
   cp lstm_autoencoder.h5 ../../Spark/
   cp scaler.pkl ../../Spark/
   cp threshold.json ../../Spark/
   ```

2. **Feature mapping**:
   - `numeric_features.json` (this directory) lists features used in training
   - `Spark/selected_features.json` lists features expected in production
   - `Spark/consumer.py` handles mapping between the two

---

## How to Retrain the Model

1. **Update dataset** (if needed):
   - Place new data in the appropriate location
   - Update paths in `dataset_loader.py`

2. **Run training**:
   ```bash
   cd Models/Chaima
   python train.py
   ```

3. **Verify outputs**:
   ```bash
   ls -lh lstm_autoencoder.h5 scaler.pkl threshold.json
   ```

4. **Copy to production**:
   ```bash
   cp lstm_autoencoder.h5 scaler.pkl threshold.json ../../Spark/
   ```

5. **Rebuild Docker image**:
   ```bash
   cd ../..
   docker-compose build spark-consumer
   docker-compose up -d
   ```

---

## Key Design Decisions

### Why LSTM Autoencoder?
- **Temporal patterns**: LSTM captures sequential dependencies in network traffic
- **Unsupervised**: Trains on normal data only, no need for labeled attacks
- **Reconstruction-based**: Anomalies fail to reconstruct properly

### Why StandardScaler?
- **Zero mean, unit variance**: Ensures all features contribute equally
- **Better for neural networks**: Helps with gradient descent convergence
- **Preserves outliers**: Unlike MinMaxScaler, doesn't compress outliers

### Why Benign-Only Training?
- **Unsupervised approach**: Model learns "normal" behavior patterns
- **Generalization**: Can detect novel, unseen attack types
- **No attack labels needed**: Reduces dependency on labeled attack data

---

## Dependencies

**Python Packages**:
- `tensorflow>=2.10.0` - Deep learning framework
- `numpy>=1.21.0` - Numerical computing
- `pandas>=1.3.0` - Data manipulation
- `scikit-learn>=1.0.0` - Preprocessing, metrics
- `joblib>=1.1.0` - Model serialization
- `matplotlib>=3.4.0` - Visualization (for analysis)

**Install**:
```bash
pip install tensorflow numpy pandas scikit-learn joblib matplotlib
```

---

## Notes

- **Training time**: 10-30 minutes on CPU, 2-5 minutes on GPU
- **Memory requirements**: ~4-8 GB RAM during training
- **Reproducibility**: Set random seeds for consistent results
- **Hyperparameter tuning**: Adjust learning rate, latent dimension, threshold in `train.py`

---

## Authors

**Chaima** - Model development and training pipeline

**Date**: 2024-2025

**Project**: Real-Time Anomaly Detection in IoMT Device Communication
