import csv
import os
import time
import threading
from scapy.all import sniff, IP, TCP

CAPTURE_FILE = "captured_data.csv"

# Define CSV headers
HEADERS = ["src_ip", "dst_ip", "src_port", "dst_port", "protocol", "packet_size"]

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

        return [src_ip, dst_ip, src_port, dst_port, protocol, packet_size]
    return None

def packet_callback(packet):
    """Handles incoming packets and saves them."""
    features = extract_features(packet)
    if features:
        with open(CAPTURE_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(features)

def countdown_timer(duration):
    """Displays a reverse countdown in the terminal."""
    for remaining in range(duration, 0, -1):
        print(f"\r⏳ Time remaining: {remaining} seconds", end="", flush=True)
        time.sleep(1)
    print("\r✅ Capture completed. Processing data...      ")

def start_packet_capture(duration=60):
    """Capture live packets for a specified duration."""
    print(f"📡 Capturing network traffic for {duration} seconds...")

    if not os.path.exists(CAPTURE_FILE):
        with open(CAPTURE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

    # Start countdown timer in a separate thread
    timer_thread = threading.Thread(target=countdown_timer, args=(duration,))
    timer_thread.start()

    # Start packet sniffing
    sniff(prn=packet_callback, store=False, timeout=duration)

    # Wait for countdown to finish
    timer_thread.join()

    print(f"✅ Packet capture completed. Data saved in {CAPTURE_FILE}")

if __name__ == "__main__":
    start_packet_capture(120)  # Captures packets for 2 minutes
