# Example 01: Multimodal Camera & AudioMoth Time-Sync Beacon

Consolidated, ready-to-deploy multimodal time-synchronization beacon for aligning **ultrasonic AudioMoth recorders**, **infrared video cameras**, and **optical sensors**.

---

## What It Does

Every sync event simultaneously fires:
1. **Optical Output (Pin 8)**: Switches 12V DC power through the optocoupler and MOSFET to drive an external IR floodlamp (and toggles the on-board LED on Pin 13).
2. **Acoustic Output (Pin 9)**: Generates a 4.0 kHz resonant square wave through the Murata PKM22EPP-40 piezo sounder.

Video cameras capture the IR flash on exact frames; AudioMoths record the sharp 4.0 kHz tone in audio spectrograms. This provides unambiguous sub-millisecond post-hoc time alignment even in dense forest canopies where GPS is unavailable.

---

## Unambiguous Pulse Hierarchy

To avoid confusing periodic heartbeats with manual marks or system reboots, the beacon uses an encoded pulse count and duration:

| Event | Pulse Count | Durations | Purpose |
| :--- | :---: | :--- | :--- |
| **Startup / Boot** | **3 Long Beeps** | Three 1.0s pulses separated by 1.0s pauses | Confirms system health, signals deployment start, and establishes $T=0$ calibration mark. |
| **Periodic Heartbeat** | **1 Long Beep** | Single 1.0s pulse every 30 minutes | Tracks drift over long multi-day field deployments (rollover-safe, drift-free timer). |
| **Manual Button Press** | **2 Short Beeps** | Two 250ms pulses separated by a 200ms pause | Drops an on-demand sync mark (e.g. start/end of an observation) without altering the 30-min schedule. |

---

## Operating Modes & Clock Synchronization

### Mode A: Connected PC Master Sync & Logging (Sub-Millisecond Accuracy)
- Connect the Arduino Uno to your PC or laptop running `python logger.py`.
- **PC-Driven Master Scheduling**: The PC watches its real-time wall clock and commands the periodic sync pulse at exact half-hour boundaries (`:00:00.000` and `:30:00.000`), matching AudioMoth recording schedules.
- **Continuous Phase Synchronization**: Every 60 seconds (and on connection), `logger.py` sends a phase-sync packet (`SYNC:<ms_remaining>`) to the Arduino, phase-locking the Arduino's internal timer to true wall-clock time.
- **Millisecond Logging**: Every pulse transition is captured live, timestamped with PC wall-clock time (`YYYY-MM-DD HH:MM:SS.mmm`), and saved to CSV (`blinkfyr_sync_log.csv`).

### Mode B: Standalone Field Deployment & Disconnect Fallback
- **Standalone from Boot**: If powered via 9V–15V battery with no PC attached, the Arduino runs autonomously using its internal `millis()` clock, firing a single 1.0s beep every 30 minutes.
- **Seamless Disconnect Fallback**: If you connect a laptop in camp to sync the clock and then unplug it to take the board into the field, the Arduino automatically continues running from the exact phase established while connected. The 30-minute periodic grid remains locked to the wall-clock half-hour boundaries accurate to the last PC connection!

---

## Quickstart

### 1. Flash the Sketch
1. Open `01_camera_audiomoth_sync.ino` in the Arduino IDE.
2. Select **Board: Arduino Uno** and your serial port.
3. Click **Upload** ($\rightarrow$).

### 2. (Optional) Run the Python Companion Logger
```bash
# 1. Install pyserial (one-time)
pip install pyserial

# 2. Run logger (auto-detects Arduino port)
python logger.py

# Or specify a custom port and CSV output path:
python logger.py /dev/ttyACM0 my_field_sync.csv   # Linux
python logger.py COM3 my_field_sync.csv           # Windows
```

### 3. Interactive PC Commands
While `logger.py` is running, type commands into the terminal:
- `b` + Enter: Trigger manual double short beep (same as pressing physical button).
- `p` + Enter: Trigger periodic pulse immediately (single 1.0s beep).
- `r` + Enter: Re-trigger startup triple long beep.
- `s` + Enter: Force an immediate phase-sync refresh to Arduino.
- `?` + Enter: Query board uptime and sync status.
- `q` or `Ctrl+C`: Clean exit.

### 4. Example CSV Log (`blinkfyr_sync_log.csv`)
```csv
PC_Timestamp,State,Pattern_or_Mode,Step,Arduino_Uptime_ms,Event_Reason,Raw_Message
2026-11-09 14:30:00.015,ON,TRIPLE,1/5,0,BOOT_INIT,STATE: ON  | PATTERN: TRIPLE | STEP: 1/5 | UPTIME_MS: 0 | EVENT: BOOT_INIT
2026-11-09 14:30:01.016,OFF,TRIPLE,2/5,1000,PATTERN_STEP,STATE: OFF | PATTERN: TRIPLE | STEP: 2/5 | UPTIME_MS: 1000 | EVENT: PATTERN_STEP
2026-11-09 15:00:00.018,ON,SINGLE,1/1,1800000,TIMER_TRIGGER,STATE: ON  | PATTERN: SINGLE | STEP: 1/1 | UPTIME_MS: 1800000 | EVENT: TIMER_TRIGGER
2026-11-09 15:14:22.450,ON,DOUBLE,1/3,2662432,BUTTON_TRIGGER,STATE: ON  | PATTERN: DOUBLE | STEP: 1/3 | UPTIME_MS: 2662432 | EVENT: BUTTON_TRIGGER
```
