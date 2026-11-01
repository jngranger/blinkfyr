/*
 * AudiomothDutyCycle.ino
 * 
 * Duty-Cycle Interval Controller for IR LED + UV LepiLED and AudioMoth sync.
 *
 * Behavior:
 * - Alternates between ON state and OFF state continuously.
 *   - ON state:  Pin 8 HIGH (12V DC output ON to IR & UV lights, indicator LED ON). No buzzer.
 *   - OFF state: Pin 8 LOW  (12V DC output OFF, indicator LED OFF). No buzzer.
 *
 * Timing Modes (Toggled by Button on Pin 2):
 * - Mode 1 (Default): 3-minute intervals (3 min ON, 3 min OFF, repeating).
 *   - Audio confirmation when entering this mode: 3 one-second chirps (1.0s ON, 0.5s OFF x 3).
 * - Mode 2: 15-second intervals (15 sec ON, 15 sec OFF, repeating).
 *   - Audio confirmation when entering this mode: 5 short chirps (120ms ON, 100ms OFF x 5).
 *
 * Startup / Mode Change:
 * - Always starts immediately in the ON state.
 * - Button on Pin 2 switches between 3-minute mode and 15-second mode.
 * - Changing modes resets the cycle timer and starts immediately in the ON state with the confirmation beeps.
 *
 * Hardware Pin Connections (No hardware changes required):
 * - OUTPUT_PIN = 8  (To Optocoupler input -> MOSFET Gate -> 12V DC Out & Indicator LED)
 * - BUZZER_PIN = 9  (To PKM22EPP-40 piezo buzzer, 4.0 kHz square wave)
 * - BUTTON_PIN = 2  (To momentary push button to GND, INPUT_PULLUP)
 */

const uint8_t OUTPUT_PIN = 8;    // Optocoupler input -> MOSFET Gate -> 12V DC Out & Indicator LED
const uint8_t BUZZER_PIN = 9;    // PKM22EPP-40 passive piezo buzzer
const uint8_t BUTTON_PIN = 2;    // Push button to GND (internal pullup)
const unsigned int BUZZER_FREQ_HZ = 4000; // 4.0 kHz resonant frequency

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
// Pattern arrays store durations: [ON, OFF, ON, OFF, ...] in milliseconds
const unsigned long CHIRP_3MIN_MODE[] = {
  1000UL, 500UL, 1000UL, 500UL, 1000UL // 3 one-second chirps (1s on, 0.5s pause, 1s on, 0.5s pause, 1s on)
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

void setOutputState(bool state) {
  isOutputOn = state;
  digitalWrite(OUTPUT_PIN, isOutputOn ? HIGH : LOW);
  digitalWrite(LED_BUILTIN, isOutputOn ? HIGH : LOW);
}

void applyMode(Mode newMode) {
  currentMode = newMode;
  // Always start immediately in the ON state when starting or switching modes
  setOutputState(true);
  intervalStartTime = millis();

  // Play corresponding audio feedback chirps
  if (currentMode == MODE_3_MIN) {
    startBuzzerPattern(CHIRP_3MIN_MODE, CHIRP_3MIN_LEN);
  } else {
    startBuzzerPattern(CHIRP_15S_MODE, CHIRP_15S_LEN);
  }
}

void setup() {
  pinMode(OUTPUT_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  stopBuzzer();

  // Start in default 3-minute mode, ON state, with 3 one-second chirps
  applyMode(MODE_3_MIN);
}

void loop() {
  unsigned long now = millis();

  // 1. Process non-blocking buzzer chirps (plays in background, does not block loop)
  updateBuzzer(now);

  // 2. Read and debounce mode button on Pin 2
  bool reading = digitalRead(BUTTON_PIN);
  if (reading != lastButtonReading) {
    lastDebounceTime = now;
  }
  if ((now - lastDebounceTime) > DEBOUNCE_MS) {
    if (reading != stableButtonState) {
      stableButtonState = reading;
      // Button pressed (active LOW transition)
      if (stableButtonState == LOW) {
        // Toggle between 3-minute and 15-second modes
        if (currentMode == MODE_3_MIN) {
          applyMode(MODE_15_SEC);
        } else {
          applyMode(MODE_3_MIN);
        }
      }
    }
  }
  lastButtonReading = reading;

  // 3. Interval cycle management (alternates ON <-> OFF)
  unsigned long targetDuration = (currentMode == MODE_3_MIN) ? INTERVAL_3_MIN_MS : INTERVAL_15_SEC_MS;

  if (now - intervalStartTime >= targetDuration) {
    intervalStartTime = now;
    // Toggle between ON and OFF
    setOutputState(!isOutputOn);
  }
}
