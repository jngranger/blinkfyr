/*
 * blinkfyr - Example 03: Fully Manual AudioMoth & Camera Time-Sync Beacon
 * https://github.com/rlwilmin-byte/blinkfyr
 * 
 * Hardware: blinkfyr (Arduino Uno + IRF520 MOSFET + LTV-4N35 Optocoupler)
 * 
 * Purpose:
 * A completely on-demand, manual synchronization beacon.
 * 
 * How it works:
 * - Boot / Startup: Completely silent and dark (no startup beeps or flashes).
 * - Schedule: NO automatic periodic interval timer.
 * - On Button Press: Fires a clean sequence of three 0.5-second pulses:
 *     0.5s ON (beep + IR/12V output)
 *     0.5s OFF
 *     0.5s ON (beep + IR/12V output)
 *     0.5s OFF
 *     0.5s ON (beep + IR/12V output)
 *     -> returns to silent, dark idle.
 *
 * Use Case:
 * Perfect for field setups where you want to manually drop sync marks on demand
 * (e.g. at the exact start and end of an observation session) without any
 * unexpected automatic beeps disturbing the site or wildlife during recording.
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

const unsigned long DEBOUNCE_MS = 50UL;

// Pulse pattern: three 0.5s (500 ms) pulses with 500 ms pauses in between
// Sequence: [ON, OFF, ON, OFF, ON]
const unsigned long MANUAL_PATTERN[] = {500UL, 500UL, 500UL, 500UL, 500UL};
const uint8_t PATTERN_LENGTH = sizeof(MANUAL_PATTERN) / sizeof(MANUAL_PATTERN[0]);

uint8_t patternStep = 0;
unsigned long stepStart = 0;
bool patternActive = false;

bool lastReading = HIGH;
bool buttonState = HIGH;
unsigned long lastDebounceTime = 0;

void setSyncOutput(bool active) {
  digitalWrite(OUTPUT_PIN, active ? HIGH : LOW);
  digitalWrite(LED_BUILTIN, active ? HIGH : LOW);
  if (active) {
    tone(BUZZER_PIN, BUZZER_FREQ_HZ);
  } else {
    noTone(BUZZER_PIN);
    digitalWrite(BUZZER_PIN, LOW);
  }
}

void startSyncSequence() {
  patternStep = 0;
  stepStart = millis();
  patternActive = true;
  setSyncOutput(true);
}

void setup() {
  pinMode(OUTPUT_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Start up completely silent and off
  setSyncOutput(false);

  // Enable internal pull-up resistor (pressed = LOW)
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

void loop() {
  unsigned long now = millis();

  // 1. Read and debounce the manual trigger button on Pin 2
  bool reading = digitalRead(BUTTON_PIN);
  if (reading != lastReading) {
    lastDebounceTime = now;
  }
  if ((now - lastDebounceTime) > DEBOUNCE_MS && reading != buttonState) {
    buttonState = reading;
    // Button pressed (active LOW)
    if (buttonState == LOW) {
      // Trigger the 3x 0.5s sync sequence (if not already playing)
      if (!patternActive) {
        startSyncSequence();
      }
    }
  }
  lastReading = reading;

  // 2. Non-blocking pulse sequence player
  if (patternActive && (now - stepStart >= MANUAL_PATTERN[patternStep])) {
    patternStep++;
    stepStart = now;
    if (patternStep >= PATTERN_LENGTH) {
      // Sequence complete -> turn off and return to idle
      setSyncOutput(false);
      patternActive = false;
    } else {
      // Even step (0, 2, 4) = ON | Odd step (1, 3) = OFF
      setSyncOutput(patternStep % 2 == 0);
    }
  }
}
