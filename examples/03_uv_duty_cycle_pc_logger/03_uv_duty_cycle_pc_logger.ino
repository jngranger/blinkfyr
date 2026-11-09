/*
 * blinkfyr - Example 03: UV LepiLED Duty-Cycler with Live PC Serial Logging
 * https://github.com/rlwilmin-byte/blinkfyr
 * 
 * Hardware: blinkfyr (Arduino Uno + IRF520 MOSFET + LTV-4N35 Optocoupler)
 * 
 * Purpose:
 * Runs the UV LepiLED / IR floodlamp duty-cycle experiment while continuously
 * connected to a PC/laptop via USB. Every time the light turns ON or OFF,
 * or the mode is switched, a structured message is sent over the Serial port
 * so the PC can timestamp each event to the exact millisecond and log it to a file.
 *
 * How it works:
 * - Operates the same 3-minute / 15-second duty cycle as Example 02:
 *   - Alternates between ON and OFF continuously.
 *   - Default: 3 minutes ON / 3 minutes OFF (starts with 3 long chirps).
 *   - Button press (Pin 2): Toggles to 15 seconds ON / 15 seconds OFF (5 short chirps).
 * - USB Serial Logging:
 *   - Runs at 115200 baud.
 *   - Emits structured event lines whenever the state changes:
 *       STATE: ON | MODE: 3-MIN | UPTIME_MS: 180000 | EVENT: TIMER_TOGGLE
 *       STATE: OFF | MODE: 3-MIN | UPTIME_MS: 360000 | EVENT: TIMER_TOGGLE
 *       STATE: ON | MODE: 15-SEC | UPTIME_MS: 380060 | EVENT: BUTTON_TOGGLE
 * - Optional Serial Commands from PC:
 *   - Send 't' or 'm' over Serial to toggle mode (same as pressing board button).
 *   - Send '?' or 's' to query current state and uptime.
 *
 * How to get PC Wall-Clock Timestamps:
 * - Method A (Python script): Run the included companion script `logger.py`
 *   on your PC. It reads the serial events, tags them with the PC's system
 *   clock (YYYY-MM-DD HH:MM:SS.mmm), and saves them to a CSV file.
 * - Method B (Arduino IDE): Open Tools -> Serial Monitor, set baud rate to
 *   115200, and check the "Show Timestamp" box!
 *
 * Pin Map:
 * - Pin 8: Switched DC Output (via LTV-4N35 Optocoupler -> IRF520 Gate)
 * - Pin 9: Piezo Buzzer (PKM22EPP-40, 4.0 kHz)
 * - Pin 2: Tactile Pushbutton to GND (internal pullup)
 */

const uint8_t OUTPUT_PIN = 8;    // To optocoupler input -> MOSFET Gate -> Switched DC Load
const uint8_t BUZZER_PIN = 9;    // To PKM22EPP-40 passive piezo buzzer
const uint8_t BUTTON_PIN = 2;    // Tactile button between Pin 2 and GND
const unsigned int BUZZER_FREQ_HZ = 4000; // 4.0 kHz acoustic resonant frequency

// Timing intervals
const unsigned long INTERVAL_3_MIN_MS  = 3UL * 60UL * 1000UL; // 180,000 ms (3 minutes)
const unsigned long INTERVAL_15_SEC_MS = 15UL * 1000UL;      //  15,000 ms (15 seconds)
const unsigned long DEBOUNCE_MS        = 50UL;

enum Mode {
  MODE_3_MIN,
  MODE_15_SEC
};

Mode currentMode = MODE_3_MIN;
bool isOutputOn = true;
unsigned long intervalStartTime = 0;

// Button debouncing state
bool lastButtonReading = HIGH;
bool stableButtonState = HIGH;
unsigned long lastDebounceTime = 0;

// Non-blocking Buzzer Chirp Player
const unsigned long CHIRP_3MIN_MODE[] = {
  1000UL, 500UL, 1000UL, 500UL, 1000UL // 3 one-second chirps (1s on, 0.5s pause x 3)
};
const uint8_t CHIRP_3MIN_LEN = sizeof(CHIRP_3MIN_MODE) / sizeof(CHIRP_3MIN_MODE[0]);

const unsigned long CHIRP_15S_MODE[] = {
  120UL, 100UL, 120UL, 100UL, 120UL, 100UL, 120UL, 100UL, 120UL // 5 short chirps (120ms on, 100ms pause x 5)
};
const uint8_t CHIRP_15S_LEN = sizeof(CHIRP_15S_MODE) / sizeof(CHIRP_15S_MODE[0]);

const unsigned long *activeBuzzerPattern = nullptr;
uint8_t buzzerPatternLen = 0;
uint8_t buzzerPatternStep = 0;
unsigned long buzzerStepStartTime = 0;
bool buzzerActive = false;

void startBuzzerPattern(const unsigned long *pattern, uint8_t length) {
  activeBuzzerPattern = pattern;
  buzzerPatternLen = length;
  buzzerPatternStep = 0;
  buzzerStepStartTime = millis();
  buzzerActive = true;
  tone(BUZZER_PIN, BUZZER_FREQ_HZ);
}

void stopBuzzer() {
  buzzerActive = false;
  noTone(BUZZER_PIN);
  digitalWrite(BUZZER_PIN, LOW);
}

void updateBuzzer(unsigned long now) {
  if (!buzzerActive) return;

  if (now - buzzerStepStartTime >= activeBuzzerPattern[buzzerPatternStep]) {
    buzzerPatternStep++;
    buzzerStepStartTime = now;
    if (buzzerPatternStep >= buzzerPatternLen) {
      stopBuzzer();
    } else {
      if (buzzerPatternStep % 2 == 0) {
        tone(BUZZER_PIN, BUZZER_FREQ_HZ); // Even step = Tone ON
      } else {
        noTone(BUZZER_PIN);               // Odd step = Tone OFF (Pause)
        digitalWrite(BUZZER_PIN, LOW);
      }
    }
  }
}

void logEvent(const char* reason) {
  Serial.print(F("STATE: "));
  Serial.print(isOutputOn ? F("ON") : F("OFF"));
  Serial.print(F(" | MODE: "));
  Serial.print(currentMode == MODE_3_MIN ? F("3-MIN") : F("15-SEC"));
  Serial.print(F(" | UPTIME_MS: "));
  Serial.print(millis());
  Serial.print(F(" | EVENT: "));
  Serial.println(reason);
}

void setOutputState(bool state, const char* reason) {
  isOutputOn = state;
  digitalWrite(OUTPUT_PIN, isOutputOn ? HIGH : LOW);
  digitalWrite(LED_BUILTIN, isOutputOn ? HIGH : LOW);
  logEvent(reason);
}

void toggleMode(const char* reason) {
  if (currentMode == MODE_3_MIN) {
    currentMode = MODE_15_SEC;
  } else {
    currentMode = MODE_3_MIN;
  }
  
  // Always start immediately in ON state when switching modes
  isOutputOn = true;
  digitalWrite(OUTPUT_PIN, HIGH);
  digitalWrite(LED_BUILTIN, HIGH);
  intervalStartTime = millis();

  logEvent(reason);

  // Play audio confirmation chirps
  if (currentMode == MODE_3_MIN) {
    startBuzzerPattern(CHIRP_3MIN_MODE, CHIRP_3MIN_LEN);
  } else {
    startBuzzerPattern(CHIRP_15S_MODE, CHIRP_15S_LEN);
  }
}

void handleSerialCommands() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 't' || c == 'T' || c == 'm' || c == 'M') {
      toggleMode("SERIAL_CMD_TOGGLE");
    } else if (c == '?' || c == 's' || c == 'S') {
      logEvent("SERIAL_STATUS_QUERY");
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(OUTPUT_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  stopBuzzer();

  // Print startup greeting header
  Serial.println(F("--- BLINKFYR USB DUTY-CYCLE LOGGER READY ---"));
  Serial.println(F("Baud: 115200 | Commands: 't' (toggle mode), '?' (query status)"));

  // Start in default 3-minute mode, ON state
  currentMode = MODE_3_MIN;
  isOutputOn = true;
  digitalWrite(OUTPUT_PIN, HIGH);
  digitalWrite(LED_BUILTIN, HIGH);
  intervalStartTime = millis();

  logEvent("BOOT_INIT");
  startBuzzerPattern(CHIRP_3MIN_MODE, CHIRP_3MIN_LEN);
}

void loop() {
  unsigned long now = millis();

  // 1. Process non-blocking buzzer chirps
  updateBuzzer(now);

  // 2. Process incoming USB commands from PC
  handleSerialCommands();

  // 3. Read and debounce physical mode button on Pin 2
  bool reading = digitalRead(BUTTON_PIN);
  if (reading != lastButtonReading) {
    lastDebounceTime = now;
  }
  if ((now - lastDebounceTime) > DEBOUNCE_MS) {
    if (reading != stableButtonState) {
      stableButtonState = reading;
      // Button pressed (active LOW)
      if (stableButtonState == LOW) {
        toggleMode("BUTTON_TOGGLE");
      }
    }
  }
  lastButtonReading = reading;

  // 4. Interval cycle management (alternates ON <-> OFF)
  unsigned long targetDuration = (currentMode == MODE_3_MIN) ? INTERVAL_3_MIN_MS : INTERVAL_15_SEC_MS;

  if (now - intervalStartTime >= targetDuration) {
    intervalStartTime = now;
    // Toggle state between ON and OFF
    setOutputState(!isOutputOn, "INTERVAL_TIMER");
  }
}
