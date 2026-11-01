/*
 * blinkfyr - Example 02: UV LepiLED Attractor Duty-Cycler & Camera Sync
 * https://github.com/rlwilmin-byte/blinkfyr
 * 
 * Hardware: blinkfyr (Arduino Uno + IRF520 MOSFET + LTV-4N35 Optocoupler)
 * 
 * Purpose:
 * Automates experimental duty cycling of high-power entomological UV insect
 * attractors (e.g. Gunnar Brehm UV LepiLED, ~1.1A) and night-vision IR floodlamps
 * for nocturnal insect flight and arrival behavior experiments.
 *
 * How it works:
 * - Alternates continuously between ON state and OFF state:
 *   - ON state:  Switched DC output ON (UV LepiLED + IR floodlamp + drain indicator LED). Silent.
 *   - OFF state: Switched DC output OFF (UV and IR lights dark, indicator LED off). Silent.
 * - By splitting the output to both a UV attractor and an IR floodlamp, nocturnal
 *   wildlife/security cameras can visually record the exact moment the attractor state
 *   changes, while providing illumination to observe moth arrivals.
 *
 * Operating Modes (Toggled by Tactile Button on Pin 2):
 * - Mode 1 (Default): 3-minute intervals (3 min ON, 3 min OFF, repeating).
 *   - Audio confirmation when entering this mode: 3 one-second chirps (1.0s ON, 0.5s pause x 3).
 * - Mode 2: 15-second intervals (15 sec ON, 15 sec OFF, repeating).
 *   - Audio confirmation when entering this mode: 5 short chirps (120ms ON, 100ms pause x 5).
 *
 * Startup / Mode Change:
 * - Always starts immediately in the ON state.
 * - Pressing the button toggles between 3-minute mode and 15-second mode.
 * - Switching modes resets the cycle timer and immediately starts in the ON state
 *   with corresponding audio confirmation chirps.
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
// Pattern arrays store durations: [ON, OFF, ON, OFF, ...] in milliseconds
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

  // 1. Process non-blocking buzzer chirps in background
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
