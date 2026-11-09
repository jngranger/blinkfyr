/*
 * blinkfyr - Example 01: Multimodal Camera & AudioMoth Time-Sync Beacon
 * https://github.com/rlwilmin-byte/blinkfyr
 * 
 * Hardware: blinkfyr (Arduino Uno + IRF520 MOSFET + LTV-4N35 Optocoupler)
 * 
 * Purpose:
 * Synchronizes ultrasonic audio recorders (e.g. Open Acoustic Devices AudioMoth)
 * with infrared video cameras, visual cameras, and external optical sensors.
 *
 * How it works:
 * - Emits simultaneous multimodal beacons:
 *   1. Optical: Switched DC output pulses (e.g., 12V IR floodlamp and on-board indicator LED)
 *   2. Acoustic: 4.0 kHz resonant square-wave audio bursts (PKM22EPP-40 piezo sounder)
 * - Both camera frames (IR/visible flash) and audio spectrograms (4.0 kHz tone) record
 *   identical, sharply defined time markers, enabling sub-millisecond post-hoc
 *   alignment even when internal clocks drift or GPS is unavailable under canopy.
 *
 * Pulse Pattern Hierarchy (Unambiguous Event Identification):
 * - 3 Long Beeps (3x 1.0s): Device Boot / Script Startup
 *     Sequence: 1.0s ON, 1.0s OFF, 1.0s ON, 1.0s OFF, 1.0s ON (T=0 calibration)
 * - 1 Long Beep (1x 1.0s): 30-Minute Periodic Heartbeat
 *     Sequence: 1.0s ON (automatically fires every 30 minutes, drift-free)
 * - 2 Short Beeps (2x 250ms): Manual Button Press (Pin 2) / On-Demand Mark
 *     Sequence: 250ms ON, 200ms OFF, 250ms ON (drops an on-demand sync mark without
 *     disrupting the ongoing 30-minute schedule)
 *
 * Dual Deployment & Master/Fallback Clock Architecture:
 * 1. PC Connected Logging Mode:
 *    - The companion script `logger.py` watches the PC's high-precision wall clock.
 *    - On connection, the PC sends a phase-sync command (`SYNC:<ms_until_next>`)
 *      to lock the Arduino's internal fallback timer to the exact upcoming wall-clock mark.
 *    - At each exact half-hour boundary (:00:00 and :30:00), `logger.py` sends a 'p' command
 *      which triggers the 1.0s beep immediately and resets the Arduino's fallback clock.
 *    - Every pulse edge is logged with millisecond PC timestamps to CSV (`blinkfyr_sync_log.csv`).
 * 2. Standalone Field Mode & Disconnect Fallback:
 *    - If running standalone with no PC, Arduino's internal `millis()` timer fires every 30 min.
 *    - If the PC was connected and later unplugged, the Arduino automatically falls back
 *      to its internal clock, with the 30-minute schedule phase-locked to the exact wall-clock
 *      schedule of the last PC connection!
 *
 * Serial Commands:
 * - 'p' or 'P'       -> Periodic sync trigger from PC (resets internal fallback timer)
 * - "SYNC:<ms>"      -> Phase-align Arduino fallback timer to next wall-clock boundary
 * - 'b' or 't'       -> Manual trigger: double short beep (same as board button)
 * - 'r' or 'i'       -> Re-trigger startup triple long beep
 * - '?'              -> Query status, uptime, and next fallback pulse time
 *
 * Pin Map:
 * - Pin 8: Switched DC Output (via LTV-4N35 Optocoupler -> IRF520 Gate)
 * - Pin 9: Piezo Buzzer (PKM22EPP-40, 4.0 kHz)
 * - Pin 2: Tactile Pushbutton to GND (internal pullup)
 * - Pin 13: On-board indicator LED (LED_BUILTIN)
 */

const uint8_t OUTPUT_PIN = 8;    // To optocoupler input -> MOSFET Gate -> Switched DC Load
const uint8_t BUZZER_PIN = 9;    // To PKM22EPP-40 passive piezo buzzer
const uint8_t BUTTON_PIN = 2;    // Tactile button between Pin 2 and GND
const unsigned int BUZZER_FREQ_HZ = 4000; // 4.0 kHz acoustic resonant frequency

// Configurable timing
const unsigned long INTERVAL_MS = 30UL * 60UL * 1000UL;  // 30 minutes between periodic sync pulses
const unsigned long DEBOUNCE_MS = 50UL;

// Pulse patterns: alternating [ON, OFF, ON, ...] durations in milliseconds
// 1. Periodic: Single 1.0s pulse
const unsigned long TIMER_PATTERN[] = {1000UL};

// 2. Manual Button: Double short beep (250ms ON, 200ms OFF, 250ms ON)
const unsigned long MANUAL_PATTERN[] = {250UL, 200UL, 250UL};

// 3. Startup / Reset: Triple long beep (1s ON, 1s OFF, 1s ON, 1s OFF, 1s ON)
const unsigned long STARTUP_PATTERN[] = {1000UL, 1000UL, 1000UL, 1000UL, 1000UL};

unsigned long lastTimerEvent = 0;
bool hasPcSync = false;

const unsigned long *activePattern = nullptr;
uint8_t patternLength = 0;
uint8_t patternStep = 0;
unsigned long stepStartTime = 0;
bool patternActive = false;
const char* currentPatternName = "IDLE";

bool isOutputActive = false;
bool lastButtonReading = HIGH;
bool stableButtonState = HIGH;
unsigned long lastDebounceTime = 0;

// Serial command buffer for multi-char commands (e.g., SYNC:1800000)
char cmdBuffer[32];
uint8_t cmdBufferIdx = 0;

void logEvent(const char* reason) {
  Serial.print(F("STATE: "));
  Serial.print(isOutputActive ? F("ON ") : F("OFF"));
  Serial.print(F(" | PATTERN: "));
  Serial.print(currentPatternName);
  Serial.print(F(" | STEP: "));
  if (patternActive) {
    Serial.print(patternStep + 1);
    Serial.print(F("/"));
    Serial.print(patternLength);
  } else {
    Serial.print(F("0/0"));
  }
  Serial.print(F(" | UPTIME_MS: "));
  Serial.print(millis());
  Serial.print(F(" | EVENT: "));
  Serial.println(reason);
}

void setSyncOutput(bool active, const char* reason = nullptr) {
  isOutputActive = active;
  digitalWrite(OUTPUT_PIN, active ? HIGH : LOW);
  digitalWrite(LED_BUILTIN, active ? HIGH : LOW);

  if (active) {
    tone(BUZZER_PIN, BUZZER_FREQ_HZ);
  } else {
    noTone(BUZZER_PIN);
    digitalWrite(BUZZER_PIN, LOW);
  }

  if (reason != nullptr) {
    logEvent(reason);
  }
}

void startPattern(const unsigned long *p, uint8_t length, const char* patternName, const char* reason) {
  activePattern = p;
  patternLength = length;
  patternStep = 0;
  stepStartTime = millis();
  patternActive = true;
  currentPatternName = patternName;
  setSyncOutput(true, reason);
}

void processMultiCharCommand(char *cmd) {
  // Check for Phase Sync command: "SYNC:<ms>" or "S:<ms>"
  if (cmd[0] == 'S' || cmd[0] == 's') {
    char *ptr = cmd + 1;
    if (*ptr == 'Y' || *ptr == 'y') ptr += 3; // Skip "YNC"
    if (*ptr == ':') ptr++;
    unsigned long msUntilNext = strtoul(ptr, nullptr, 10);
    if (msUntilNext > 0 && msUntilNext <= INTERVAL_MS) {
      // Phase-align Arduino fallback clock so the next pulse fires at the exact PC boundary
      lastTimerEvent = millis() - (INTERVAL_MS - msUntilNext);
      hasPcSync = true;
      logEvent("PC_PHASE_SYNC");
    }
  }
}

void handleSerialCommands() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\r' || c == '\n') {
      if (cmdBufferIdx > 0) {
        cmdBuffer[cmdBufferIdx] = '\0';
        processMultiCharCommand(cmdBuffer);
        cmdBufferIdx = 0;
      }
      continue;
    }

    // Immediate single-character commands (when not already buffering a multi-char command)
    if (cmdBufferIdx == 0) {
      if (c == 'b' || c == 'B' || c == 't' || c == 'T') {
        // Manual trigger: fires double short beep without altering 30-min schedule
        if (!patternActive) {
          startPattern(MANUAL_PATTERN, sizeof(MANUAL_PATTERN) / sizeof(MANUAL_PATTERN[0]), "DOUBLE", "SERIAL_TRIGGER");
        }
        continue;
      } else if (c == 'p' || c == 'P') {
        // PC-driven periodic sync pulse: fire immediately & sync Arduino fallback clock
        lastTimerEvent = millis();
        hasPcSync = true;
        if (!patternActive) {
          startPattern(TIMER_PATTERN, sizeof(TIMER_PATTERN) / sizeof(TIMER_PATTERN[0]), "SINGLE", "PC_TRIGGER");
        }
        continue;
      } else if (c == 'r' || c == 'R' || c == 'i' || c == 'I') {
        // Startup re-trigger: fires triple long beep
        if (!patternActive) {
          startPattern(STARTUP_PATTERN, sizeof(STARTUP_PATTERN) / sizeof(STARTUP_PATTERN[0]), "TRIPLE", "SCRIPT_STARTUP");
        }
        continue;
      } else if (c == '?') {
        logEvent("STATUS_QUERY");
        Serial.print(F("[INFO] PC_SYNC: "));
        Serial.print(hasPcSync ? F("ACTIVE") : F("STANDALONE"));
        Serial.print(F(" | FALLBACK_REMAINING_MS: "));
        unsigned long elapsed = millis() - lastTimerEvent;
        Serial.println(elapsed < INTERVAL_MS ? (INTERVAL_MS - elapsed) : 0);
        continue;
      }
    }

    // Buffer multi-character command (e.g. "SYNC:1420000")
    if (cmdBufferIdx < sizeof(cmdBuffer) - 1) {
      cmdBuffer[cmdBufferIdx++] = c;
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(OUTPUT_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  setSyncOutput(false);

  Serial.println(F("--- BLINKFYR MULTIMODAL TIME-SYNC BEACON READY ---"));
  Serial.println(F("Baud: 115200 | Commands: 'p' (PC trigger), 'SYNC:<ms>' (time-sync), 'b'/'t' (manual), '?' (status)"));

  lastTimerEvent = millis(); // Initial periodic interval begins from power-on

  // Initial triple long sync pulse at power-up to confirm system health and mark T=0
  startPattern(STARTUP_PATTERN, sizeof(STARTUP_PATTERN) / sizeof(STARTUP_PATTERN[0]), "TRIPLE", "BOOT_INIT");
}

void loop() {
  unsigned long now = millis();

  // 1. Process USB Serial commands (non-blocking)
  handleSerialCommands();

  // 2. Periodic schedule (standalone autonomous mode, or fallback if PC disconnects)
  if (now - lastTimerEvent >= INTERVAL_MS) {
    lastTimerEvent += INTERVAL_MS;
    if (!patternActive) {
      const char* eventReason = hasPcSync ? "TIMER_FALLBACK" : "TIMER_TRIGGER";
      startPattern(TIMER_PATTERN, sizeof(TIMER_PATTERN) / sizeof(TIMER_PATTERN[0]), "SINGLE", eventReason);
    }
  }

  // 3. Debounced manual button trigger (Pin 2): fires double short beep without disrupting 30-min timer
  bool reading = digitalRead(BUTTON_PIN);
  if (reading != lastButtonReading) {
    lastDebounceTime = now;
  }
  if ((now - lastDebounceTime) > DEBOUNCE_MS && reading != stableButtonState) {
    stableButtonState = reading;
    if (stableButtonState == LOW) {
      if (!patternActive) {
        startPattern(MANUAL_PATTERN, sizeof(MANUAL_PATTERN) / sizeof(MANUAL_PATTERN[0]), "DOUBLE", "BUTTON_TRIGGER");
      }
    }
  }
  lastButtonReading = reading;

  // 4. Non-blocking pulse pattern engine
  if (patternActive && (now - stepStartTime >= activePattern[patternStep])) {
    patternStep++;
    stepStartTime = now;

    if (patternStep >= patternLength) {
      patternActive = false;
      currentPatternName = "IDLE";
      setSyncOutput(false, "PATTERN_COMPLETE");
    } else {
      bool active = (patternStep % 2 == 0); // Even index = ON, Odd index = OFF
      setSyncOutput(active, "PATTERN_STEP");
    }
  }
}
