import csv
import os
import time
import threading
import sys
from scapy.all import sniff, IP, TCP

# Ensure UTF-8 encoding for Windows compatibility
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass  # Fallback for older Python versions

CAPTURE_FILE = "packets/captured_packets.csv"
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

def countdown_timer(duration, stop_event):
    """Displays a reverse countdown with a progress bar and percentage."""
    start_time = time.monotonic()
    bar_length = 30  # Length of the progress bar

    while not stop_event.is_set():
        elapsed = time.monotonic() - start_time
        remaining = int(duration - elapsed)
        if remaining < 0:
            break

        percent_complete = int((elapsed / duration) * 100)
        filled_length = int(bar_length * elapsed / duration)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\r⏳ Time remaining: {remaining:3d} sec |{bar}| {percent_complete:3d}% ", end="", flush=True)
        time.sleep(0.5)

    print("\r✔️ Capture completed. Processing data...")

def start_packet_capture(duration=60):
    """Capture live packets for a specified duration."""
    print(f"🌐 Capturing network traffic for {duration} seconds...")

    if not os.path.exists(CAPTURE_FILE):
        with open(CAPTURE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

    stop_event = threading.Event()
    
    # Start countdown timer in a separate thread
    timer_thread = threading.Thread(target=countdown_timer, args=(duration, stop_event))
    timer_thread.start()

    # Start packet sniffing
    sniff(prn=packet_callback, store=False, timeout=duration)

    # Signal the countdown to stop and wait for the thread to finish
    stop_event.set()
    timer_thread.join()

    print(f"✔️ Packet capture completed. Data saved in {CAPTURE_FILE}")

if __name__ == "__main__":
    start_packet_capture(120)  # Captures packets for 2 minutes
