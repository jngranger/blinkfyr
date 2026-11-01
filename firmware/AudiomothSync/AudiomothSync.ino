// Periodic alarm: one 1s pulse every 30 min.
// Button press: three 1s pulses (1s ON, 1s OFF, 1s ON, 1s OFF, 1s ON), without affecting the 30-min schedule.

const uint8_t OUTPUT_PIN = 8;    // to MOSFET gate / driver (controls 12V IR LED)
const uint8_t BUZZER_PIN = 9;    // 4.0 kHz square wave for PKM22EPP-40 passive piezo buzzer
const uint8_t BUTTON_PIN = 2;    // button between this pin and GND
const unsigned int BUZZER_FREQ_HZ = 4000; // PKM22EPP-40 resonant frequency (4.0 kHz)

const unsigned long INTERVAL_MS = 1UL * 60UL * 1000UL;  // 30 minutes
const unsigned long DEBOUNCE_MS = 50UL;

// Patterns: alternating ON, OFF, ON, ... durations in ms
const unsigned long TIMER_PATTERN[]  = {1000UL};                                    // one 1s pulse
const unsigned long BUTTON_PATTERN[] = {1000UL, 1000UL, 1000UL, 1000UL, 1000UL};   // three 1s pulses (on, off, on, off, on)

unsigned long lastTimerEvent = 0;

const unsigned long *pattern = nullptr;
uint8_t patternLength = 0;
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

void startPattern(const unsigned long *p, uint8_t length) {
  pattern = p;
  patternLength = length;
  patternStep = 0;
  stepStart = millis();
  patternActive = true;
  setSyncOutput(true);
}

void setup() {
  pinMode(OUTPUT_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  setSyncOutput(false);

  pinMode(BUTTON_PIN, INPUT_PULLUP);  // pressed = LOW, no external resistor needed
  lastTimerEvent = millis();          // next timed alarm 30 min after power-up
  startPattern(BUTTON_PATTERN, sizeof(BUTTON_PATTERN) / sizeof(BUTTON_PATTERN[0]));  // triple pulse at power-up
}

void loop() {
  unsigned long now = millis();

  // Fixed 30-min schedule (rollover-safe, doesn't drift)
  if (now - lastTimerEvent >= INTERVAL_MS) {
    lastTimerEvent += INTERVAL_MS;
    startPattern(TIMER_PATTERN, sizeof(TIMER_PATTERN) / sizeof(TIMER_PATTERN[0]));
  }

  // Debounced button: triple 1s pulse on press, schedule untouched
  bool reading = digitalRead(BUTTON_PIN);
  if (reading != lastReading) {
    lastDebounceTime = now;
  }
  if (now - lastDebounceTime > DEBOUNCE_MS && reading != buttonState) {
    buttonState = reading;
    if (buttonState == LOW) {
      startPattern(BUTTON_PATTERN, sizeof(BUTTON_PATTERN) / sizeof(BUTTON_PATTERN[0]));
    }
  }
  lastReading = reading;

  // Step through the active pattern: even steps HIGH (ON), odd steps LOW (OFF)
  if (patternActive && now - stepStart >= pattern[patternStep]) {
    patternStep++;
    stepStart = now;
    if (patternStep >= patternLength) {
      setSyncOutput(false);
      patternActive = false;
    } else {
      setSyncOutput(patternStep % 2 == 0);
    }
  }
}
