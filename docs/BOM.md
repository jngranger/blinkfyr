# blinkfyr: Bill of Materials (BOM) & Parts List

This document lists all components, specifications, and vendor codes required to build the **blinkfyr** multimodal synchronization beacon and programmable DC load driver.

---

## 1. Active Silicon & Microcontroller

| Component | Part Number | Package | Qty | Key Specifications |
| :--- | :--- | :---: | :---: | :--- |
| **Microcontroller** | **Arduino Uno R3** | Board | 1 | ATmega328P @ 16 MHz, 5V logic. Powered directly from 9V–15V on `VIN`. |
| **Power MOSFET** | **IRF520** | TO-220 | 1 | N-Channel Power MOSFET ($100\text{V}$, $9.2\text{A}$, $R_{DS(on)} \le 0.27\,\Omega$ @ $V_{GS}=10\text{V}$). Low-side load switch. |
| **Optocoupler** | **LTV-4N35** | DIP-6 | 1 | High-speed phototransistor optocoupler ($V_{CEO}=30\text{V}$, CTR $\ge 100\%$). Level-shifts 5V logic to full DC rail gate drive. |
| **Flyback Diode** | **1N4004** | DO-41 | 1 | Silicon rectifier diode ($400\text{V}$, $1\text{A}$). Clamps inductive kickback across switched DC output. |

---

## 2. Passives, Transducers & Indicators

| Component | Part / Marking | Package | Qty | Key Specifications |
| :--- | :--- | :---: | :---: | :--- |
| **Piezo Sounder** | **Murata PKM22EPP-40** | 3-Pin / 2-Lead | 1 | Passive piezoelectric transducer. Resonant frequency: $4.0\text{ kHz}$ ($\approx 80\text{ dB}$ SPL). |
| **Drain Status LED** | 3mm or 5mm Green LED | Radial | 1 | Visible drain indicator; illuminates when the MOSFET conducts to GND. |
| **Tactile Button** | 6x6mm Momentary Switch | 4-Pin DIP | 1 | Manual pulse trigger and mode toggle; connects Arduino Pin 2 to GND. |
| **Resistor $R_{\text{in}}$** | **$560\,\Omega$** *(or $1.00\,\text{k}\Omega$)* | Axial 0.25W | 1 | `Green-Blue-Brown-Gold` *(or `Brown-Black-Black-Brown-Brown`)*. Limits opto LED drive current to ~6.8 mA. |
| **Resistor $R_{\text{gate}}$**| **$220\,\Omega$** | Axial 0.25W | 1 | `Red-Red-Brown-Gold`. MOSFET gate damping / parasitic oscillation suppression. |
| **Resistor $R_{\text{pd}}$** | **$10.0\,\text{k}\Omega$** | Axial 0.25W | 1 | `Brown-Black-Orange-Gold` *(or `Brown-Black-Black-Red-Brown`)*. Pull-down resistor holding MOSFET firmly OFF. |
| **Resistor $R_{\text{led}}$** | **$1.0\,\text{k}\Omega$** | Axial 0.25W | 1 | `Brown-Black-Red-Gold`. Current limiter for the drain indicator LED (~10 mA @ 12V). |

---

## 3. Prototyping Hardware & Interconnects

| Item | Part / Model | Qty | Notes |
| :--- | :--- | :---: | :--- |
| **Perfboard** | **Jaycar HP9556** | 1 (half) | "Ultra Mini Experimenters Board" (`COREVA 300-2101`). 16 columns $\times$ 17 rows with paired 2-pin strips and power buses. |
| **DC Power In Jack** | 2.1mm $\times$ 5.5mm DC Female Barrel Jack | 1 | Connects to external 9V–15V DC power source (bench supply, 12V SLA, or Li-ion pack). |
| **DC Output Jack** | 2.1mm $\times$ 5.5mm DC Female Barrel Jack | 1 | Switched output to external loads. Center pin (+VDC), outer sleeve (switched Drain). |
| **DC Y-Splitter** | 1-Female to 2-Male 2.1mm DC Cable | 1 | Allows simultaneous connection of multiple 12V devices (e.g. UV LepiLED + IR floodlamp). |
| **Hookup Wire** | 22–24 AWG Solid Core | Assorted | Soldered jumpers and stiff-pin flying leads into Arduino headers. |

---

## 4. Example Target Loads & Field Gear

| Equipment | Model / Type | Typical Current | Role in Experiment |
| :--- | :--- | :---: | :--- |
| **UV Insect Attractor** | Gunnar Brehm UV LepiLED | ~1.1 A @ 12.5V | Entomological light trap attractant with internal buck/boost constant-current driver. |
| **IR Illuminator** | Vmitejoe 4-Array F25 IR Light | ~0.4 A @ 12.0V | 12V infrared floodlight for night-vision camera sync. *(LDR daylight dome taped over)*. |
| **Acoustic Logger** | Open Acoustic Devices AudioMoth | — | Passive acoustic/ultrasonic field logger synchronizing on the 4.0 kHz audio chirps. |
| **Nocturnal Video Cam** | Trail Cam / Action Cam (IR-mod) | — | Continuous or motion-triggered video camera recording the optical sync beacon frames. |
