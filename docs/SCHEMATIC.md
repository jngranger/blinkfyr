# blinkfyr: Circuit Schematic & Theory of Operation

**blinkfyr** (*Swedish: "flashing beacon / lighthouse"*) is an open-source, programmable hardware driver and multimodal synchronization beacon designed for ecological field research, bioacoustics, camera trapping, and automated nocturnal light assays.

---

## 1. Electrical Schematic

![blinkfyr Circuit Schematic](images/schematic.png)

---

## 2. Circuit Architecture & Operating Principles

### 2.1 Power Input Flexibility (9V to 15V DC)
The circuit is designed to operate over a wide input voltage range of **$9.0\text{V}$ to $15.0\text{V}$ DC**, accommodating standard field power sources without requiring internal voltage regulation for the loads:
* **$12\text{V}$ Lead-Acid / AGM / Gel Batteries**: Nominal $12.0\text{V} - 12.8\text{V}$, charging float up to $13.8\text{V} - 14.4\text{V}$.
* **3S Li-ion / LiPo Packs**: $9.0\text{V}$ (depleted) to $12.6\text{V}$ (fully charged).
* **4S $\text{LiFePO}_4$ Packs**: Nominal $12.8\text{V} - 13.2\text{V}$, charging float $14.4\text{V}$.
* **Regulated Bench & Wall Adapters**: $9\text{V}$, $12\text{V}$, or $13.8\text{V}$ DC.

The Arduino Uno receives this supply directly on its `VIN` pin, where the onboard low-dropout linear regulator steps it down to stable $+5\text{V}$ logic for the ATmega328P microcontroller.

---

### 2.2 Gate Drive Challenge & The Optocoupler Level-Shifter
The low-side power switch is an **`IRF520` N-channel power MOSFET** (rated $100\text{V}$, $9.2\text{A}$). 

#### The 5V Logic Issue
Standard power MOSFETs like the `IRF520` are non-logic-level devices:
* **Threshold Voltage ($V_{GS(th)}$)**: $2.0\text{V} - 4.0\text{V}$. This is merely the pinch-off threshold where the device starts conducting a minute leakage current ($250\,\mu\text{A}$).
* **Full Saturation**: Requires $V_{GS} \ge 10\text{V}$ to compress channel resistance down to $R_{DS(on)} \le 0.27\,\Omega$.
* **Driver Brownout / Strobing**: When driven directly by 5V logic from an Arduino GPIO, the MOSFET operates in its active/resistive region, pinching off around $\approx 0.9\text{A}$ and dropping several volts across its drain-source channel ($V_{DS} \approx 4\text{V} - 5\text{V}$). While simple resistive loads or low-power IR LEDs (~400 mA) will operate with diminished output, switch-mode constant-current drivers (such as the Gunnar Brehm UV LepiLED, which requires $>1\text{A}$ steady and draws $>1.5\text{A}$ inrush) encounter rapid under-voltage brownout oscillations (strobing).

#### The `LTV-4N35` Optocoupler Level-Shifter
To drive the gate with the full supply rail voltage without exposing the microcontroller to dangerous voltage transients, an `LTV-4N35` optocoupler is implemented as a high-side level shifter:

1. **Microcontroller Isolation (Input Side)**:
   * Arduino **Pin 8** connects to Optocoupler **Pin 1 (Anode)** through current-limiting resistor $R_{\text{in}} = 560\,\Omega$ (or $1.00\,\text{k}\Omega$).
   * Optocoupler **Pin 2 (Cathode)** connects to Common GND.
   * Internal GaAs infrared emitter forward voltage: $V_F \approx 1.2\text{V}$.
   * Drive current:
     $$I_F = \frac{5.0\text{V} - 1.2\text{V}}{560\,\Omega} \approx 6.8\text{ mA} \quad (\text{or } 3.8\text{ mA with } 1.00\,\text{k}\Omega)$$
   * This is gentle on the ATmega328P pin while driving the optocoupler's internal LED well into its saturated Current Transfer Ratio (CTR) regime.

2. **Full Rail Gate Drive (Output Side)**:
   * Optocoupler **Pin 5 (Collector)** connects directly to the $+V_{\text{DC}}$ power rail ($+9\text{V}$ to $+15\text{V}$).
   * Optocoupler **Pin 4 (Emitter)** feeds the MOSFET gate through damping resistor $R_{\text{gate}} = 220\,\Omega$.
   * A pull-down resistor $R_{\text{pd}} = 10.0\,\text{k}\Omega$ ties the gate firmly to GND.
   * **When Pin 8 is LOW**: The phototransistor is open-circuit. $R_{\text{pd}}$ drains gate charge and holds $V_{GS} = 0\text{V}$, ensuring hard turn-off.
   * **When Pin 8 is HIGH**: The phototransistor saturates ($V_{CE(sat)} \approx 0.15\text{V}$), pulling Pin 4 up to $V_{\text{rail}} - 0.15\text{V}$. Across the $220\,\Omega / 10\,\text{k}\Omega$ divider:
     $$V_{GS} = (V_{\text{rail}} - 0.15\text{V}) \times \frac{10000}{10000 + 220} \approx 11.6\text{V} \quad (\text{at } 12\text{V in})$$
   * At $V_{GS} \approx 11.6\text{V} \gg 10\text{V}$, the MOSFET channel conducts with full saturation ($R_{DS(on)} < 0.27\,\Omega$).
   * At a steady $1.5\text{A}$ load, total conduction dissipation is negligible:
     $$P_{\text{loss}} = I^2 \times R_{DS(on)} = (1.5\text{A})^2 \times 0.27\,\Omega \approx 0.61\text{W}$$
   * The MOSFET remains cool to the touch without needing an external aluminum heatsink, and the load receives full supply voltage with zero brownout or flickering.

---

### 2.3 Acoustic Synchronization (`PKM22EPP-40` Piezo)
* **Transducer**: Murata `PKM22EPP-40` passive piezoelectric sounder.
* **Resonant Frequency**: $4.0\,\text{kHz} \pm 0.5\,\text{kHz}$.
* **Acoustic Function**: Ultrasonic and acoustic wildlife loggers (e.g. Open Acoustic Devices AudioMoth) readily register $4.0\text{ kHz}$ acoustic pulses across distance and through forest canopy. Generating a $4.0\text{ kHz}$ square wave via Arduino `tone(BUZZER_PIN, 4000)` produces maximum sound pressure level ($\approx 80\text{ dB}$ SPL @ 10cm) with minimal current draw ($< 5\text{ mA}$).

---

### 2.4 Protection & Visual Diagnostics
* **Flyback Clamping Diode (`1N4004`)**: Placed across the switched output (Cathode to $+V_{\text{DC}}$, Anode to Drain). Safely suppresses and clamps inductive kickback spikes caused by long field power cables and internal inductors during turn-off.
* **Drain Monitor LED**: A green LED with a $1.0\,\text{k}\Omega$ series resistor across $+V_{\text{DC}}$ and Drain provides positive optical confirmation whenever the MOSFET drain is actively conducting to ground.
* **Debounced Tactile Switch**: Momentary button on Arduino **Pin 2** connected to GND, configured in software with `INPUT_PULLUP`. Provides instant manual triggering and mode switching in the field without requiring a computer.
