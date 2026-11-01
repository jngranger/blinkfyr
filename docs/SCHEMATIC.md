# Circuit Schematic & Theory of Operation

This document details the electrical design, circuit schematic, and engineering principles behind the **Arduino Sync Beeper & 12V High-Power Optical Driver**.

---

## 1. Electrical Schematic

![Circuit Schematic](images/schematic.png)

---

## 2. Circuit Subsystems & Theory of Operation

### 2.1 The Gate Drive Challenge ($V_{GS}$ vs. $R_{DS(on)}$)
The `IRF520` is an N-channel power MOSFET rated for 100V and 9.2A. However, it is a **standard (non-logic-level)** MOSFET:
* **Gate Threshold Voltage ($V_{GS(th)}$)**: Between $2.0\text{V}$ and $4.0\text{V}$. This is merely the threshold where the channel begins conducting a tiny trickle current ($250\,\mu\text{A}$).
* **Full Saturation ($V_{GS} = 10\text{V}$)**: To achieve its rated low channel resistance ($R_{DS(on)} \le 0.27\,\Omega$), the gate must be driven to $10\text{V}$ or higher.
* **The 5V Logic Issue**: When driven directly by an Arduino ATmega328P output (5.0V), the channel resistance remains high ($> 3\text{--}5\,\Omega$), and maximum saturation current pinches off around $\approx 0.9\text{A}$.
* **Load Behavior**: 
  * The **IR LED array** draws only $\approx 400\text{ mA}$, functioning adequately at 5V gate drive.
  * The **UV LepiLED** contains an internal switch-mode constant-current buck/boost driver. It draws $\sim 1.1\text{A}$ steady (with $>1.5\text{A}$ inrush) and has an internal under-voltage lockout ($\sim 9.5\text{V}$). At 5V gate drive, the MOSFET dropped $4\text{--}5\text{V}$ across $V_{DS}$, causing the LepiLED driver to rapidly oscillate/strobe.

### 2.2 The Optocoupler Level-Shifter (`LTV-4N35`)
To drive the MOSFET gate to the full $+12\text{V}$ rail without subjecting the Arduino to high voltages, an `LTV-4N35` optocoupler is implemented as a high-side level shifter:

1. **Input Side (Arduino $\to$ Opto LED)**:
   * Arduino **Pin 8** connects to **Pin 1 (Anode)** through a current-limiting resistor ($R_{\text{in}} = 560\,\Omega$ or $1.00\,\text{k}\Omega$).
   * **Pin 2 (Cathode)** connects directly to Common GND.
   * Forward voltage of internal GaAs IR LED: $V_F \approx 1.2\text{V}$.
   * Drive current with $560\,\Omega$:
     $$I_F = \frac{5.0\text{V} - 1.2\text{V}}{560\,\Omega} \approx 6.8\text{ mA}$$
   * Drive current with $1.00\,\text{k}\Omega$:
     $$I_F = \frac{5.0\text{V} - 1.2\text{V}}{1000\,\Omega} = 3.8\text{ mA}$$
   Both currents are well within the ATmega328P pin rating (max $20\text{ mA}$) and provide ample optical flux for saturation.

2. **Output Side (Opto Phototransistor $\to$ MOSFET Gate)**:
   * **Pin 5 (Collector)** connects directly to the $+12\text{V}$ rail.
   * **Pin 4 (Emitter)** connects to the MOSFET gate circuit through $R_{\text{gate}} = 220\,\Omega$.
   * A $R_{\text{pd}} = 10.0\,\text{k}\Omega$ pull-down resistor connects between Gate and GND.
   * When Pin 8 is **LOW**: The phototransistor is completely OFF (open circuit). $R_{\text{pd}}$ pulls the Gate firmly to $0\text{V}$ (GND), guaranteeing the MOSFET is hard OFF.
   * When Pin 8 is **HIGH**: The phototransistor saturates ($V_{CE(sat)} \approx 0.15\text{V}$). Pin 4 pulls up to:
     $$V_{\text{gate}} = 12.0\text{V} - 0.15\text{V} \approx 11.85\text{V}$$
   * Voltage divider between $220\,\Omega$ and $10\,\text{k}\Omega$:
     $$V_{GS} = 11.85\text{V} \times \frac{10000}{10000 + 220} \approx 11.6\text{V} \gg 10\text{V}$$
   * The MOSFET channel opens fully ($R_{DS(on)} < 0.27\,\Omega$). At $1.5\text{A}$ combined load, the MOSFET drops only:
     $$V_{DS} = 1.5\text{A} \times 0.27\,\Omega \approx 0.40\text{V}$$
     $$P_{\text{loss}} = (1.5\text{A})^2 \times 0.27\,\Omega \approx 0.61\text{W}$$
   The MOSFET remains cool to the touch without needing a bulky heatsink, and the loads receive the full $12.1\text{V}$!

---

### 2.3 Acoustic Synchronization (Piezo Buzzer on Pin 9)
* **Part**: Murata `PKM22EPP-40` passive piezoelectric transducer.
* **Resonant Frequency**: $4.0\,\text{kHz} \pm 0.5\,\text{kHz}$.
* **Drive Mode**: The Arduino produces a clean $4.0\,\text{kHz}$ square wave using `tone(BUZZER_PIN, 4000)`. At its acoustic mechanical resonance, the piezo disk achieves maximum sound pressure level ($\approx 80\text{ dB}$ SPL @ 10cm) with minimal current consumption ($< 5\text{ mA}$).
* **Application**: Allows field bioacoustic loggers (**AudioMoth**) to record sharp acoustic timestamps that synchronize perfectly with the visual IR video recordings.

---

### 2.4 Protection & Diagnostics
* **Flyback Clamping Diode (`1N4004`)**: Placed directly across the switched $12\text{V}$ DC output with its cathode on $+12\text{V}$ and anode on MOSFET Drain. This safely recirculates and clamps inductive spikes created by long field power leads and driver inductors during turn-off.
* **Drain Monitor LED**: A green LED with a $1.0\,\text{k}\Omega$ series resistor connected between $+12\text{V}$ and Drain. When the MOSFET conducts, Drain drops to near ground, illuminating the LED. If the load is disconnected or the MOSFET fails to conduct, the LED remains dark.
* **Tactile Button**: A momentary pushbutton on Arduino **Pin 2** connected to GND, configured in software with `pinMode(BUTTON_PIN, INPUT_PULLUP)`. Eliminates external pull-up resistors and provides bounce-free software debounced triggers.
