import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest

DATA_FILE = "captured_data.csv"
MODEL_FILE = "model.joblib"

def train_model():
    """Trains the IDS model using captured network data."""
    if not os.path.exists(DATA_FILE):
        print("❌ No captured data found! Run packet_capture.py first.")
        return

    df = pd.read_csv(DATA_FILE)

    if df.shape[0] < 10:
        print("❌ Not enough data to train the model.")
        return

    # Convert to NumPy array
    X_train = df.to_numpy()

    # Train Isolation Forest
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_train)

    # Save model
    joblib.dump(model, MODEL_FILE)
    print(f"✅ Model trained and saved as {MODEL_FILE}")

if __name__ == "__main__":
    train_model()
