import numpy as np
import joblib
import os
import logging
import argparse
import sys
from scapy.all import sniff, IP, TCP

# Ensure UTF-8 encoding for Windows compatibility
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass  # Fallback for older Python versions

MODEL_FILE = "models/model.joblib"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "ids.log")

def setup_logging(log_file: str) -> None:
    """Create log directory and configure logging."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

def load_model(model_file: str):
    """Load the trained model from file."""
    if not os.path.exists(model_file):
        raise FileNotFoundError("Model not found! Please run train_model.py first.")
    try:
        model = joblib.load(model_file)
        logging.info("✔️ IDS Model Loaded.")
        print("✔️ IDS Model Loaded.")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        raise

def extract_features(packet) -> np.ndarray:
    """Extract features from a network packet."""
    if packet.haslayer(IP):
        ip_layer = packet[IP]
        src_ip = sum(map(int, ip_layer.src.split('.')))
        dst_ip = sum(map(int, ip_layer.dst.split('.')))
        protocol = ip_layer.proto
        packet_size = len(packet)

        if packet.haslayer(TCP):
            tcp_layer = packet[TCP]
            src_port = tcp_layer.sport
            dst_port = tcp_layer.dport
        else:
            src_port = dst_port = 0

        return np.array([[src_ip, dst_ip, src_port, dst_port, protocol, packet_size]])
    return None

def detect_threat(packet, model) -> None:
    """Detect if a network packet is anomalous and log the result."""
    features = extract_features(packet)
    if features is not None:
        try:
            score = model.decision_function(features)[0]
            is_anomalous = model.predict(features)[0] == -1  # -1 indicates anomaly
        except Exception as e:
            logging.error(f"Error during threat detection: {e}")
            return

        status = "🚨 Threat Detected!" if is_anomalous else "✔️ Safe"
        log_msg = f"Packet {packet.summary()} -> Score: {score:.4f} -> {status}"
        print(log_msg)
        logging.info(log_msg)

def start_detection(model, iface: str) -> None:
    """Start real-time IDS monitoring on the specified network interface."""
    print(f"🔍 IDS is monitoring live traffic on interface '{iface}'...")
    sniff(prn=lambda pkt: detect_threat(pkt, model), store=False, iface=iface)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="IDS: Real-time Intrusion Detection System")
    parser.add_argument("--iface", type=str, default="Wi-Fi", help="Network interface to monitor")
    parser.add_argument("--model", type=str, default=MODEL_FILE, help="Path to the trained model file")
    parser.add_argument("--log", type=str, default=LOG_FILE, help="Path to the log file")
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging(args.log)
    try:
        model = load_model(args.model)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    except Exception as e:
        print(f"❌ An error occurred while loading the model: {e}")
        return

    start_detection(model, args.iface)

if __name__ == "__main__":
    main()
