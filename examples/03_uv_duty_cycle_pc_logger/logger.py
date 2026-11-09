#!/usr/bin/env python3
"""
blinkfyr - Live PC Event Logger (Python Companion)
Reads serial events from blinkfyr, timestamps them with the PC's wall-clock
time (millisecond accuracy), prints them live to the console, and logs them to CSV.

Usage:
    pip install pyserial
    python logger.py [optional_port] [optional_output_file.csv]

Example:
    python logger.py /dev/ttyACM0
    python logger.py COM3 my_experiment_log.csv
"""

import sys
import time
import datetime
import csv
import os

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("\n[ERROR] 'pyserial' is not installed.")
    print("Please install it by running:\n    pip install pyserial\n")
    sys.exit(1)

def find_arduino_port():
    """Attempts to auto-detect an connected Arduino / USB Serial device."""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None

    # Search for known Arduino keywords in descriptions
    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if "arduino" in desc or "ch340" in desc or "ftdi" in desc or "usb serial" in desc:
            return p.device

    # Default to first available port if only one is present
    if len(ports) == 1:
        return ports[0].device
    return None

def parse_event_line(line):
    """
    Parses blinkfyr event format:
    STATE: ON | MODE: 3-MIN | UPTIME_MS: 180000 | EVENT: TIMER_TOGGLE
    """
    data = {}
    parts = line.split('|')
    for part in parts:
        if ':' in part:
            k, v = part.split(':', 1)
            data[k.strip().upper()] = v.strip()
    return data

def main():
    # Parse arguments
    port = sys.argv[1] if len(sys.argv) > 1 else None
    csv_filename = sys.argv[2] if len(sys.argv) > 2 else "blinkfyr_log.csv"

    if not port:
        port = find_arduino_port()

    if not port:
        print("\n[!] Could not auto-detect serial port.")
        available = [p.device for p in serial.tools.list_ports.comports()]
        print(f"Available ports: {available if available else 'None detected'}")
        print("Please specify your port manually, e.g.:")
        print("    python logger.py /dev/ttyACM0 (Linux)")
        print("    python logger.py COM3         (Windows)\n")
        sys.exit(1)

    baud = 115200
    print(f"Connecting to blinkfyr on {port} @ {baud} baud...")

    try:
        ser = serial.Serial(port, baud, timeout=1.0)
    except serial.SerialException as e:
        print(f"\n[ERROR] Could not open port {port}: {e}")
        print("Tip: Make sure the Arduino IDE Serial Monitor is closed first!\n")
        sys.exit(1)

    # Initialize CSV file if it doesn't exist
    file_exists = os.path.exists(csv_filename)
    csv_file = open(csv_filename, mode='a', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)

    if not file_exists:
        csv_writer.writerow(["PC_Timestamp", "State", "Mode", "Arduino_Uptime_ms", "Event_Reason", "Raw_Message"])
        csv_file.flush()

    print(f"\n=======================================================")
    print(f"  blinkfyr Live Event Logger Running")
    print(f"  Logging events to: {os.path.abspath(csv_filename)}")
    print(f"  Press Ctrl+C to stop logging anytime.")
    print(f"=======================================================\n")

    try:
        while True:
            line_bytes = ser.readline()
            if not line_bytes:
                continue

            try:
                line = line_bytes.decode('utf-8', errors='replace').strip()
            except Exception:
                continue

            if not line:
                continue

            now_pc = datetime.datetime.now()
            pc_timestamp = now_pc.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # If it's a structured blinkfyr event line
            if "STATE:" in line and "MODE:" in line:
                parsed = parse_event_line(line)
                state = parsed.get("STATE", "UNKNOWN")
                mode = parsed.get("MODE", "UNKNOWN")
                uptime = parsed.get("UPTIME_MS", "0")
                reason = parsed.get("EVENT", "EVENT")

                # Format clean live display
                state_colored = f"\033[1;32m{state:3s}\033[0m" if state == "ON" else f"\033[1;31m{state:3s}\033[0m"
                print(f"[{pc_timestamp}] Light: {state_colored} | Mode: {mode:5s} | Uptime: {int(uptime)/1000.0:6.1f}s | Event: {reason}")

                # Save to CSV
                csv_writer.writerow([pc_timestamp, state, mode, uptime, reason, line])
                csv_file.flush()
            else:
                # Informational / greeting line
                print(f"[{pc_timestamp}] [INFO] {line}")

    except KeyboardInterrupt:
        print("\n\nStopping logger. All events saved to CSV.")
    finally:
        csv_file.close()
        ser.close()
        print("Serial port closed cleanly. Goodbye!\n")

if __name__ == "__main__":
    main()
