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
 * - Emits simultaneous multi-modal beacons:
 *   1. Optical: Switched DC output pulses (e.g., 12V IR floodlamp and on-board indicator LED)
 *   2. Acoustic: 4.0 kHz resonant square-wave audio bursts (PKM22EPP-40 piezo sounder)
 * - Both camera frames (IR/visible flash) and audio spectrograms (4.0 kHz tone) record
 *   identical, sharply defined time markers, enabling sub-millisecond post-hoc
 *   alignment even when internal clocks drift or GPS is unavailable under canopy.
 *
 * Schedule:
 * - Boot: Fires three 1.0-second sync pulses (1s ON, 1s OFF, 1s ON, 1s OFF, 1s ON)
 * - Periodic: Automatically fires a single 1.0-second sync pulse every 30 minutes
 * - Manual Button (Pin 2): Triggers the three 1.0-second sync pulses on demand
 *   without disrupting the ongoing 30-minute periodic timer.
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

// Configurable timing
const unsigned long INTERVAL_MS = 30UL * 60UL * 1000UL;  // 30 minutes between periodic sync pulses
const unsigned long DEBOUNCE_MS = 50UL;

// Beacon pulse patterns: alternating [ON, OFF, ON, ...] durations in ms
const unsigned long TIMER_PATTERN[]  = {1000UL};                                   // Single 1.0s pulse
const unsigned long BUTTON_PATTERN[] = {1000UL, 1000UL, 1000UL, 1000UL, 1000UL};  // Triple 1.0s pulses

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

  pinMode(BUTTON_PIN, INPUT_PULLUP);  // Pressed = LOW, uses ATmega328P internal pullup
  lastTimerEvent = millis();          // First timed periodic sync 30 min after boot
  
  // Fire initial triple sync pulse at power-up to confirm system health and mark T=0
  startPattern(BUTTON_PATTERN, sizeof(BUTTON_PATTERN) / sizeof(BUTTON_PATTERN[0]));
}

void loop() {
  unsigned long now = millis();

  // 1. Periodic schedule (rollover-safe, drift-free)
  if (now - lastTimerEvent >= INTERVAL_MS) {
    lastTimerEvent += INTERVAL_MS;
    startPattern(TIMER_PATTERN, sizeof(TIMER_PATTERN) / sizeof(TIMER_PATTERN[0]));
  }

  // 2. Debounced manual button trigger: fires triple pulse without altering 30-min schedule
  bool reading = digitalRead(BUTTON_PIN);
  if (reading != lastReading) {
    lastDebounceTime = now;
  }
  if ((now - lastDebounceTime) > DEBOUNCE_MS && reading != buttonState) {
    buttonState = reading;
    if (buttonState == LOW) {
      startPattern(BUTTON_PATTERN, sizeof(BUTTON_PATTERN) / sizeof(BUTTON_PATTERN[0]));
    }
  }
  lastReading = reading;

  // 3. Non-blocking pulse pattern engine
  if (patternActive && (now - stepStart >= pattern[patternStep])) {
    patternStep++;
    stepStart = now;
    if (patternStep >= patternLength) {
      setSyncOutput(false);
      patternActive = false;
    } else {
      setSyncOutput(patternStep % 2 == 0); // Even index = ON, Odd index = OFF
    }
  }
}
