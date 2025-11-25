# -*- coding: utf-8 -*-
"""dataset_loader.py

Loads and splits data.csv into train, validation, and test sets.
Uses stratified splitting to maintain label distribution.
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split

# Always detect the root of the repository, no matter where the script is run
# This file is in Models/Chaima/, so go up two levels to reach project root
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"📁 BASE_PATH detected as: {BASE_PATH}")


def load_splits(base_path):
    """
    Loads data.csv and splits it into train, val, test sets.

    Uses stratified splitting based on Label column to maintain class distribution.
    Split ratio: 70% train, 15% validation, 15% test

    Returns:
        train, val, test: pandas DataFrames with all columns including 'Label'
    """

    print("🔍 load_splits() called...")
    print(f"➡ Using BASE PATH: {base_path}")

    # Load data.csv from project root
    data_path = os.path.join(base_path, "data.csv")
    print(f"📂 Loading data from: {data_path}")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"data.csv not found at {data_path}")

    # Load full dataset
    df = pd.read_csv(data_path)
    print(f"✅ Data loaded successfully! Shape: {df.shape}")

    # Rename 'Label' to 'label' for consistency with preprocessing code
    if 'Label' in df.columns:
        df = df.rename(columns={'Label': 'label'})
        print("📝 Renamed 'Label' column to 'label'")

    # Check label distribution
    print(f"📊 Label distribution:")
    label_counts = df['label'].value_counts()
    print(f"   Total labels: {len(label_counts)}")
    print(f"   Most common: {label_counts.index[0]} ({label_counts.iloc[0]} samples)")

    # Map BENIGN to BenignTraffic for consistency with preprocessing
    df['label'] = df['label'].replace('BENIGN', 'BenignTraffic')
    print("📝 Mapped 'BENIGN' → 'BenignTraffic'")

    # Stratified split: 70% train, 30% temp (which becomes 15% val, 15% test)
    train, temp = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df['label']
    )

    # Split temp into val and test (50/50 of the 30% = 15% each)
    val, test = train_test_split(
        temp,
        test_size=0.50,
        random_state=42,
        stratify=temp['label']
    )

    print("✅ Dataset split completed!")
    print(f"📏 Train shape: {train.shape} ({len(train)/len(df)*100:.1f}%)")
    print(f"📏 Val shape:   {val.shape} ({len(val)/len(df)*100:.1f}%)")
    print(f"📏 Test shape:  {test.shape} ({len(test)/len(df)*100:.1f}%)")

    # Verify BenignTraffic distribution
    print(f"\n📊 BenignTraffic samples:")
    print(f"   Train: {len(train[train['label'] == 'BenignTraffic'])}")
    print(f"   Val:   {len(val[val['label'] == 'BenignTraffic'])}")
    print(f"   Test:  {len(test[test['label'] == 'BenignTraffic'])}")

    return train, val, test


if __name__ == "__main__":
    train, val, test = load_splits(BASE_PATH)
    print("\n✅ Test run successful!")
