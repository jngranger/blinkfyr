#!/usr/bin/env python3
"""
blinkfyr - Live PC Event Logger & Sync Master (Python Companion)
https://github.com/rlwilmin-byte/blinkfyr

Master Wall-Clock Synchronization & Live Logger for blinkfyr (Example 01).

When connected, the PC acts as the high-precision master clock:
1. Direct PC Triggering:
   - Automatically triggers the 1.0s periodic sync pulse at exact wall-clock boundaries
     (:00:00 and :30:00) using the PC's NTP-synchronized system time.
2. Continuous Arduino Phase Synchronization:
   - Synchronizes the Arduino's internal fallback timer on connection and periodically
     every 60 seconds (`SYNC:<ms_remaining>`).
   - If the PC is disconnected, the Arduino automatically falls back to its own internal
     clock, remaining phase-locked to the exact wall-clock schedule established while connected!
3. Sub-Millisecond Logging:
   - Captures all pulse transitions from the Arduino, stamps them with PC wall-clock time
     (millisecond precision), displays live status, and appends to CSV (`blinkfyr_sync_log.csv`).
4. Interactive Keyboard Controls:
   - 'b' -> Manual trigger (double short beep)
   - 'p' -> Force periodic pulse now (single 1.0s beep)
   - 'r' -> Re-trigger startup pulse (triple long beep)
   - 's' -> Force phase-sync update to Arduino
   - '?' -> Query board uptime & status
   - 'q' or Ctrl+C -> Clean exit

Usage:
    pip install pyserial
    python logger.py [optional_port] [optional_output_file.csv]

Examples:
    python logger.py
    python logger.py /dev/ttyACM0
    python logger.py COM3 field_session_2026.csv
"""

import sys
import time
import datetime
import csv
import os
import threading

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("\n[ERROR] 'pyserial' is not installed.")
    print("Please install it by running:\n    pip install pyserial\n")
    sys.exit(1)


def find_arduino_port():
    """Attempts to auto-detect a connected Arduino / USB Serial device."""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None

    for p in ports:
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        if any(kw in desc or kw in hwid for kw in ("arduino", "ch340", "ftdi", "usb serial", "cdc")):
            return p.device

    if len(ports) == 1:
        return ports[0].device
    return None


def parse_event_line(line):
    """
    Parses blinkfyr event strings formatted as:
    KEY: VALUE | KEY: VALUE | ...
    """
    data = {}
    parts = line.split('|')
    for part in parts:
        if ':' in part:
            k, v = part.split(':', 1)
            data[k.strip().upper()] = v.strip()
    return data


def get_next_half_hour(now=None):
    """Calculates the upcoming :00:00 or :30:00 wall-clock target."""
    if now is None:
        now = datetime.datetime.now()
    if now.minute < 30:
        target = now.replace(minute=30, second=0, microsecond=0)
    else:
        next_hour = now + datetime.timedelta(hours=1)
        target = next_hour.replace(minute=0, second=0, microsecond=0)
    return target


def get_ms_until(target, now=None):
    """Returns milliseconds remaining until target datetime."""
    if now is None:
        now = datetime.datetime.now()
    delta = (target - now).total_seconds()
    return max(0, int(delta * 1000))


def send_sync_command(ser, ms_remaining):
    """Sends phase synchronization command to Arduino."""
    msg = f"SYNC:{ms_remaining}\n"
    ser.write(msg.encode('ascii'))
    ser.flush()


def keyboard_input_loop(ser, stop_event):
    """Background thread to send interactive single-character commands to Arduino."""
    while not stop_event.is_set():
        try:
            user_input = sys.stdin.readline()
            if not user_input:
                break
            cmd = user_input.strip()
            if not cmd:
                continue

            if cmd.lower() in ('q', 'quit', 'exit'):
                print("[INFO] Clean exit requested via keyboard.")
                stop_event.set()
                break

            char_to_send = cmd[0].lower()
            if char_to_send in ('b', 't'):
                ser.write(b'b')
                ser.flush()
                print("  --> Sent manual trigger ('b') to blinkfyr (Double Short Beep)")
            elif char_to_send == 'p':
                ser.write(b'p')
                ser.flush()
                print("  --> Sent periodic trigger ('p') to blinkfyr (Single 1.0s Beep)")
            elif char_to_send in ('r', 'i'):
                ser.write(b'r')
                ser.flush()
                print("  --> Sent startup trigger ('r') to blinkfyr (Triple Long Beep)")
            elif char_to_send == 's':
                ms = get_ms_until(get_next_half_hour())
                send_sync_command(ser, ms)
                print(f"  --> Sent forced phase-sync update to blinkfyr (Remaining: {ms}ms)")
            elif char_to_send == '?':
                ser.write(b'?')
                ser.flush()
                print("  --> Sent status query ('?') to blinkfyr")
            else:
                ser.write(cmd[0].encode('ascii'))
                ser.flush()
                print(f"  --> Sent '{cmd[0]}' to blinkfyr")
        except Exception:
            break


def main():
    port = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].endswith(".csv") else None
    csv_filename = sys.argv[2] if len(sys.argv) > 2 else (
        sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".csv") else "blinkfyr_sync_log.csv"
    )

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
        ser = serial.Serial(port, baud, timeout=0.1)
    except serial.SerialException as e:
        print(f"\n[ERROR] Could not open port {port}: {e}")
        print("Tip: Make sure the Arduino IDE Serial Monitor is closed first!\n")
        sys.exit(1)

    # Allow Arduino bootloader to complete if board auto-reset on DTR
    time.sleep(1.8)

    file_exists = os.path.exists(csv_filename)
    csv_file = open(csv_filename, mode='a', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)

    if not file_exists:
        csv_writer.writerow([
            "PC_Timestamp", 
            "State", 
            "Pattern_or_Mode", 
            "Step", 
            "Arduino_Uptime_ms", 
            "Event_Reason", 
            "Raw_Message"
        ])
        csv_file.flush()

    # Initial time-sync: anchor Arduino fallback clock to PC wall-clock half-hour grid
    target_boundary = get_next_half_hour()
    initial_ms_remaining = get_ms_until(target_boundary)
    send_sync_command(ser, initial_ms_remaining)

    print(f"\n=======================================================")
    print(f"  blinkfyr Master Wall-Clock Logger & Sync Manager")
    print(f"  Port: {port} | Baud: {baud}")
    print(f"  Logging events to: {os.path.abspath(csv_filename)}")
    print(f"  Wall-Clock Schedule: Fires at :00:00 and :30:00")
    print(f"  Next Scheduled Pulse: {target_boundary.strftime('%H:%M:%S')} ({initial_ms_remaining/1000.0:.1f}s)")
    print(f"  Arduino Fallback Sync: PHASE-LOCKED TO PC CLOCK")
    print(f"  Pulse Legend:")
    print(f"    - TRIPLE: Startup triple long beep (3x 1.0s, T=0 boot marker)")
    print(f"    - SINGLE: 30-minute periodic sync beep (1x 1.0s)")
    print(f"    - DOUBLE: Manual button press double beep (2x 250ms short)")
    print(f"  Interactive Commands (type letter + Enter):")
    print(f"    'b' -> Manual trigger (double short beep)")
    print(f"    'p' -> Trigger periodic pulse now (single 1.0s beep)")
    print(f"    'r' -> Re-trigger startup pulse (triple long beep)")
    print(f"    's' -> Refresh phase-sync to Arduino")
    print(f"    '?' -> Query Arduino status & uptime")
    print(f"    'q' or Ctrl+C -> Stop logging")
    print(f"=======================================================\n")

    stop_event = threading.Event()
    input_thread = threading.Thread(target=keyboard_input_loop, args=(ser, stop_event), daemon=True)
    input_thread.start()

    last_periodic_sync_time = time.time()

    try:
        while not stop_event.is_set():
            now_pc = datetime.datetime.now()
            now_mono = time.time()

            # 1. Check if PC wall clock reached the target half-hour boundary (:00:00 or :30:00)
            if now_pc >= target_boundary:
                # Trigger the periodic sync beep directly from PC clock
                ser.write(b'p')
                ser.flush()
                pc_timestamp_trigger = now_pc.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                print(f"[{pc_timestamp_trigger}] [MASTER PC CLOCK] --> TRIGGERED PERIODIC SYNC BEACON")

                # Advance to next target half-hour boundary
                target_boundary = get_next_half_hour(now_pc + datetime.timedelta(seconds=2))
                ms_to_next = get_ms_until(target_boundary)
                send_sync_command(ser, ms_to_next)
                last_periodic_sync_time = now_mono

            # 2. Periodically (every 60 seconds) nudge Arduino phase-sync to eliminate resonator drift
            elif now_mono - last_periodic_sync_time >= 60.0:
                ms_to_next = get_ms_until(target_boundary)
                send_sync_command(ser, ms_to_next)
                last_periodic_sync_time = now_mono

            # 3. Read incoming serial telemetry from Arduino
            line_bytes = ser.readline()
            if not line_bytes:
                continue

            try:
                line = line_bytes.decode('utf-8', errors='replace').strip()
            except Exception:
                continue

            if not line:
                continue

            pc_timestamp = now_pc.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            # Detect structured event line by STATE and UPTIME_MS presence
            if "STATE:" in line and "UPTIME_MS:" in line:
                parsed = parse_event_line(line)
                state = parsed.get("STATE", "UNKNOWN")
                uptime = parsed.get("UPTIME_MS", "0")
                reason = parsed.get("EVENT", "EVENT")
                pattern_or_mode = parsed.get("PATTERN", parsed.get("MODE", "N/A"))
                step = parsed.get("STEP", "N/A")

                # Live terminal coloring
                state_colored = f"\033[1;32m{state:3s}\033[0m" if state.strip() == "ON" else f"\033[1;31m{state:3s}\033[0m"
                step_str = f" | Step: {step:5s}" if step != "N/A" else ""

                try:
                    uptime_sec = f"{int(uptime)/1000.0:8.3f}s"
                except ValueError:
                    uptime_sec = f"{uptime}ms"

                print(f"[{pc_timestamp}] Beacon: {state_colored} | Pattern: {pattern_or_mode:6s}{step_str} | Uptime: {uptime_sec} | Event: {reason}")

                # Save structured row to CSV
                csv_writer.writerow([pc_timestamp, state, pattern_or_mode, step, uptime, reason, line])
                csv_file.flush()
            else:
                # Informational / greeting / status lines
                print(f"[{pc_timestamp}] [INFO] {line}")

    except KeyboardInterrupt:
        print("\n\nStopping logger. All events saved to CSV.")
    finally:
        stop_event.set()
        csv_file.close()
        ser.close()
        print("Serial port closed cleanly. Goodbye!\n")


if __name__ == "__main__":
    main()
