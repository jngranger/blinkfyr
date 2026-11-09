# Example 03: UV LepiLED Duty-Cycler with Live PC Serial Logging

Runs the exact same UV LepiLED / IR floodlamp duty-cycling schedule as Example 02, but with **live USB serial event reporting** so a connected PC or laptop can log every ON/OFF transition with wall-clock millisecond timestamps.

---

## How It Works

1. **On the Arduino**:
   * Runs at `115200` baud over USB.
   * Every time the light turns ON or OFF, or the mode is switched, it emits a structured log line:
     ```text
     STATE: ON  | MODE: 3-MIN | UPTIME_MS: 180000 | EVENT: INTERVAL_TIMER
     STATE: OFF | MODE: 3-MIN | UPTIME_MS: 360000 | EVENT: INTERVAL_TIMER
     STATE: ON  | MODE: 15-SEC | UPTIME_MS: 380060 | EVENT: BUTTON_TOGGLE
     ```
2. **On the PC**:
   * **Option A (Python Logger - Recommended)**: Run `python logger.py`. It reads the serial events, tags them with your PC's real-time clock (`YYYY-MM-DD HH:MM:SS.mmm`), displays them live on screen, and automatically appends them to a CSV file (`blinkfyr_log.csv`).
   * **Option B (Arduino IDE)**: Open **Tools $\to$ Serial Monitor**, select **115200 baud**, and check the **"Show Timestamp"** box. The Arduino IDE will automatically timestamp every line as it arrives!

---

## Quickstart

### 1. Flash the Sketch
1. Open `03_uv_duty_cycle_pc_logger.ino` in the Arduino IDE.
2. Select your Arduino Uno port and click **Upload** ($\rightarrow$).

### 2. Run the Python Logger
In your terminal (Linux, Windows PowerShell, or macOS):
```bash
# 1. Install pyserial (one-time)
pip install pyserial

# 2. Run the logger (auto-detects port)
python logger.py

# Or specify your port and custom CSV filename:
python logger.py COM3 my_experiment.csv          # Windows
python logger.py /dev/ttyACM0 my_experiment.csv  # Linux
```

### 3. Example CSV Output (`blinkfyr_log.csv`)
```csv
PC_Timestamp,State,Mode,Arduino_Uptime_ms,Event_Reason,Raw_Message
2026-11-04 19:49:19.123,ON,3-MIN,0,BOOT_INIT,STATE: ON | MODE: 3-MIN | UPTIME_MS: 0 | EVENT: BOOT_INIT
2026-11-04 19:52:19.125,OFF,3-MIN,180000,INTERVAL_TIMER,STATE: OFF | MODE: 3-MIN | UPTIME_MS: 180000 | EVENT: INTERVAL_TIMER
2026-11-04 19:55:19.127,ON,3-MIN,360000,INTERVAL_TIMER,STATE: ON | MODE: 3-MIN | UPTIME_MS: 360000 | EVENT: INTERVAL_TIMER
```

---

## Interactive Serial Commands
While connected, you can type characters into the Serial terminal or Python logger:
* Press `t` or `m`: Toggles between 3-minute and 15-second modes (same as pressing the physical button on the board).
* Press `?` or `s`: Requests the current state, mode, and uptime.
