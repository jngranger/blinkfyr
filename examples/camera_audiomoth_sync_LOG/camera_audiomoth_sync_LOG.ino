/*
 * blinkfyr - Example 01b: Multimodal Camera & AudioMoth Time-Sync Beacon with USB Serial Logging
 * https://github.com/rlwilmin-byte/blinkfyr
 * 
 * Hardware: blinkfyr (Arduino Uno + IRF520 MOSFET + LTV-4N35 Optocoupler)
 * 
 * Purpose:
 * Synchronizes ultrasonic audio recorders (e.g. Open Acoustic Devices AudioMoth)
 * with infrared video cameras, visual cameras, and external optical sensors, while
 * providing structured millisecond event output over USB Serial to log every pulse
 * transition directly to a PC / companion script.
 *
 * How it works:
 * - Emits simultaneous multimodal beacons:
 *   1. Optical: Switched DC output pulses (e.g., 12V IR floodlamp and on-board indicator LED)
 *   2. Acoustic: 4.0 kHz resonant square-wave audio bursts (PKM22EPP-40 piezo sounder)
 * - USB Serial Logging:
 *   - Runs at 115200 baud.
 *   - Emits structured event lines on pulse edges and triggers:
 *       STATE: ON  | PATTERN: TRIPLE | STEP: 1/5 | UPTIME_MS: 0      | EVENT: BOOT_INIT
 *       STATE: OFF | PATTERN: TRIPLE | STEP: 2/5 | UPTIME_MS: 1000   | EVENT: PATTERN_STEP
 *       STATE: ON  | PATTERN: SINGLE | STEP: 1/1 | UPTIME_MS: 1800000| EVENT: TIMER_TRIGGER
 *       STATE: ON  | PATTERN: TRIPLE | STEP: 1/5 | UPTIME_MS: 2045120| EVENT: BUTTON_TRIGGER
 * - Serial Commands from PC:
 *   - Send 't' or 'b' over Serial to manually trigger the triple sync pulse.
 *   - Send '?' or 's' to query current state, active pattern status, and uptime.
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
const char* currentPatternName = "IDLE";

bool isOutputActive = false;
bool lastReading = HIGH;
bool buttonState = HIGH;
unsigned long lastDebounceTime = 0;

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
  pattern = p;
  patternLength = length;
  patternStep = 0;
  stepStart = millis();
  patternActive = true;
  currentPatternName = patternName;
  setSyncOutput(true, reason);
}

void handleSerialCommands() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 't' || c == 'T' || c == 'b' || c == 'B') {
      startPattern(BUTTON_PATTERN, sizeof(BUTTON_PATTERN) / sizeof(BUTTON_PATTERN[0]), "TRIPLE", "SERIAL_TRIGGER");
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

  setSyncOutput(false);

  Serial.println(F("--- BLINKFYR TIME-SYNC BEACON LOGGER READY ---"));
  Serial.println(F("Baud: 115200 | Commands: 't'/'b' (trigger sync), '?' (query status)"));

  lastTimerEvent = millis(); // First timed periodic sync occurs 30 min after boot

  // Initial triple sync pulse at power-up to mark T=0 and calibrate recording start
  startPattern(BUTTON_PATTERN, sizeof(BUTTON_PATTERN) / sizeof(BUTTON_PATTERN[0]), "TRIPLE", "BOOT_INIT");
}

void loop() {
  unsigned long now = millis();

  // 1. Process USB Serial commands
  handleSerialCommands();

  // 2. Periodic schedule (rollover-safe, drift-free)
  if (now - lastTimerEvent >= INTERVAL_MS) {
    lastTimerEvent += INTERVAL_MS;
    startPattern(TIMER_PATTERN, sizeof(TIMER_PATTERN) / sizeof(TIMER_PATTERN[0]), "SINGLE", "TIMER_TRIGGER");
  }

  // 3. Debounced manual button trigger (Pin 2)
  bool reading = digitalRead(BUTTON_PIN);
  if (reading != lastReading) {
    lastDebounceTime = now;
  }
  if ((now - lastDebounceTime) > DEBOUNCE_MS && reading != buttonState) {
    buttonState = reading;
    if (buttonState == LOW) {
      startPattern(BUTTON_PATTERN, sizeof(BUTTON_PATTERN) / sizeof(BUTTON_PATTERN[0]), "TRIPLE", "BUTTON_TRIGGER");
    }
  }
  lastReading = reading;

  // 4. Non-blocking pulse pattern engine
  if (patternActive && (now - stepStart >= pattern[patternStep])) {
    patternStep++;
    stepStart = now;

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