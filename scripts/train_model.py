import os
import logging
import argparse
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from tqdm import tqdm

def configure_logging(log_level=logging.INFO):
    """Configure logging for the application."""
    logging.basicConfig(level=log_level, 
                        format="%(asctime)s - %(levelname)s - %(message)s")

def load_data(data_file: str) -> np.ndarray:
    """Load and validate data from the CSV file.
    
    Args:
        data_file (str): Path to the CSV file containing the data.
    
    Returns:
        np.ndarray: Data in NumPy array format.
    
    Raises:
        FileNotFoundError: If the data file does not exist.
        ValueError: If there is insufficient data.
    """
    if not os.path.exists(data_file):
        logging.error(f"Data file '{data_file}' not found! Run packet_capture.py first.")
        raise FileNotFoundError(f"Data file '{data_file}' not found!")
    
    try:
        df = pd.read_csv(data_file)
    except Exception as e:
        logging.error(f"Error reading data file '{data_file}': {e}")
        raise

    if df.shape[0] < 10:
        logging.error("Not enough data to train the model. Minimum 10 records required.")
        raise ValueError("Not enough data to train the model. Minimum 10 records required.")
    
    logging.info(f"Loaded data from {data_file} with shape {df.shape}")
    return df.to_numpy()

def train_isolation_forest(X_train: np.ndarray, total_estimators: int = 100, 
                           contamination: float = 0.05, n_jobs: int = -1) -> IsolationForest:
    """Train the IsolationForest model iteratively using a progress bar.
    
    Args:
        X_train (np.ndarray): Training data.
        total_estimators (int): Total number of trees in the IsolationForest.
        contamination (float): Expected proportion of outliers.
        n_jobs (int): Number of parallel jobs (use -1 to utilize all processors).
    
    Returns:
        IsolationForest: Trained model.
    """
    model = IsolationForest(
        n_estimators=0,  # Initialize with no trees.
        contamination=contamination,
        random_state=42,
        warm_start=True,  # Allow iterative addition of trees.
        n_jobs=n_jobs
    )
    
    logging.info("Starting model training...")
    for _ in tqdm(range(total_estimators), desc="Training Isolation Forest", unit="tree"):
        model.n_estimators += 1
        model.fit(X_train)
    logging.info("Model training completed.")
    
    return model

def save_model(model: IsolationForest, model_file: str):
    """Save the trained model to disk.
    
    Args:
        model (IsolationForest): Trained IsolationForest model.
        model_file (str): Path to save the model.
    
    Raises:
        Exception: If model saving fails.
    """
    try:
        joblib.dump(model, model_file)
        logging.info(f"Model successfully saved as {model_file}")
    except Exception as e:
        logging.error(f"Error saving model to '{model_file}': {e}")
        raise

def evaluate_model(model: IsolationForest, X_train: np.ndarray):
    """Evaluate the trained model on the training data and log a summary.
    
    Args:
        model (IsolationForest): Trained model.
        X_train (np.ndarray): Training data.
    """
    predictions = model.predict(X_train)
    # In IsolationForest, 1 indicates inliers and -1 indicates outliers.
    inliers = np.sum(predictions == 1)
    outliers = np.sum(predictions == -1)
    logging.info(f"Training Data Evaluation: {inliers} inliers, {outliers} outliers detected.")

def main(args):
    configure_logging()
    try:
        X_train = load_data(args.data_file)
    except Exception as e:
        logging.error(f"Data loading failed: {e}")
        return
    
    model = train_isolation_forest(
        X_train,
        total_estimators=args.total_estimators,
        contamination=args.contamination,
        n_jobs=args.n_jobs
    )
    
    save_model(model, args.model_file)
    evaluate_model(model, X_train)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train an IsolationForest IDS model using captured network data."
    )
    parser.add_argument("--data_file", type=str, default="packets/captured_packets.csv", 
                        help="Path to the CSV data file.")
    parser.add_argument("--model_file", type=str, default="models/model.joblib", 
                        help="Path to save the trained model.")
    parser.add_argument("--total_estimators", type=int, default=100, 
                        help="Total number of trees in the IsolationForest.")
    parser.add_argument("--contamination", type=float, default=0.05, 
                        help="Expected proportion of outliers in the data.")
    parser.add_argument("--n_jobs", type=int, default=-1, 
                        help="Number of parallel jobs to run (-1 uses all processors).")
    args = parser.parse_args()
    
    main(args)
