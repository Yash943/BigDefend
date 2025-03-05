import numpy as np
import joblib
import os
import logging
from scapy.all import sniff, IP, TCP

MODEL_FILE = "model.joblib"
LOG_FILE = "logs/ids.log"

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# Load trained model
if not os.path.exists(MODEL_FILE):
    print("❌ Model not found! Run train_model.py first.")
    exit()

model = joblib.load(MODEL_FILE)
print("✅ IDS Model Loaded.")

def extract_features(packet):
    """Extract features from a network packet."""
    if packet.haslayer(IP):
        src_ip = sum(map(int, packet[IP].src.split('.')))
        dst_ip = sum(map(int, packet[IP].dst.split('.')))
        protocol = packet[IP].proto
        packet_size = len(packet)

        if packet.haslayer(TCP):
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        else:
            src_port = dst_port = 0

        return np.array([[src_ip, dst_ip, src_port, dst_port, protocol, packet_size]])
    return None

def detect_threat(packet):
    """Detects if a network packet is an anomaly."""
    features = extract_features(packet)
    if features is not None:
        score = model.decision_function(features)[0]
        is_anomalous = model.predict(features)[0] == -1  # -1 = Anomalous

        log_msg = f"Packet {packet.summary()} -> Score: {score:.4f} -> {'🚨 Threat Detected!' if is_anomalous else '✅ Safe'}"
        print(log_msg)
        logging.info(log_msg)

def start_detection():
    """Start real-time IDS monitoring."""
    print("🔍 IDS is monitoring live traffic...")
    sniff(prn=detect_threat, store=False, iface="Wi-Fi")

if __name__ == "__main__":
    start_detection()
