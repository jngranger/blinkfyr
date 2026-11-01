# Bill of Materials (BOM) & Parts List

This document lists all components, hardware, and ratings used in the **Arduino Sync Beeper & 12V High-Power Optical Driver**.

---

## 1. Core Electronics & Silicon

| Component | Part / Marking | Package | Quantity | Function / Specifications |
| :--- | :--- | :--- | :---: | :--- |
| **Microcontroller** | **Arduino Uno R3** | Board | 1 | ATmega328P @ 16 MHz. Powered via `VIN` (12V) and `GND`. |
| **Power MOSFET** | **IRF520** | TO-220 | 1 | N-Channel Power MOSFET (100V, 9.2A, $R_{DS(on)} \le 0.27\,\Omega$ @ $V_{GS}=10\text{V}$). Switched low-side ground return. |
| **Optocoupler IC** | **LTV-4N35** | DIP-6 | 1 | High-speed phototransistor optocoupler. Level shifts 5V Arduino logic to 12V gate drive. |
| **Flyback Diode** | **1N4004** | DO-41 | 1 | 1A, 400V general-purpose silicon rectifier. Clamps inductive flyback voltage across 12V loads. |
| **Piezo Buzzer** | **PKM22EPP-40** | 3-Pin / 2-Lead | 1 | Murata passive piezoelectric sounder. Driven at 4.0 kHz resonant frequency via `tone()`. |
| **Indicator LED** | **3mm / 5mm Green LED** | Radial T-1 3/4 | 1 | Visual drain status monitor. Illuminates when the MOSFET drain conducts. |
| **Tactile Button** | **6x6mm Pushbutton** | 4-Pin DIP | 1 | Momentary tactile switch between Arduino Pin 2 and GND (`INPUT_PULLUP`). |

---

## 2. Resistors

| Reference | Value | Bands / Marking | Tolerance / Rating | Purpose |
| :--- | :---: | :--- | :---: | :--- |
| **$R_{\text{in}}$** | **$560\,\Omega$** *(or $1.00\,\text{k}\Omega$)* | `Green-Blue-Brown-Gold` *(or `Brown-Black-Black-Brown-Brown`)* | 5% (or 1%), 0.25W | Current limiter for Optocoupler input LED ($\sim 6.8\text{ mA}$ from Pin 8). |
| **$R_{\text{gate}}$** | **$220\,\Omega$** | `Red-Red-Brown-Gold` | 5%, 0.25W | Gate damping resistor. Suppresses parasitic ringing and limits inrush into gate capacitance. |
| **$R_{\text{pd}}$** | **$10.0\,\text{k}\Omega$** | `Brown-Black-Orange-Gold` *(or `Brown-Black-Black-Red-Brown`)* | 5% (or 1%), 0.25W | Gate pull-down resistor. Holds MOSFET firmly OFF when optocoupler is unpowered. |
| **$R_{\text{led}}$** | **$1.0\,\text{k}\Omega$** | `Brown-Black-Red-Gold` *(or `Brown-Black-Black-Brown-Brown`)* | 5% (or 1%), 0.25W | Current limiter for on-board Drain indicator LED ($\sim 10\text{ mA}$ from 12V rail). |

---

## 3. Prototyping Board & Interconnects

| Item | Part / Model | Quantity | Notes |
| :--- | :--- | :---: | :--- |
| **Prototyping Board** | **Jaycar HP9556** | 1 (half) | "Ultra Mini Experimenters Board" (`COREVA 300-2101`). 16 columns $\times$ 17 rows with paired 2-pin strips and power buses. |
| **DC Power In Jack** | 2.1mm $\times$ 5.5mm DC Female Barrel Jack | 1 | Connects to external 12V DC bench supply / battery pack. |
| **DC Output Jack** | 2.1mm $\times$ 5.5mm DC Female Barrel Jack | 1 | Outputs switched +12V DC to loads. |
| **DC Power Splitter** | 1-Female to 2-Male 2.1mm Y-Splitter | 1 | Splits single 12V DC output to both the UV LepiLED and IR Illuminator. |
| **Hookup Wire** | 22–24 AWG Solid Core & Stranded | Assorted | Soldered links, jumpers, and flying leads with stiff pins for Arduino headers. |

---

## 4. Optical Loads & Target Equipment

| Equipment | Model / Specs | Typical Current Draw | Description |
| :--- | :--- | :---: | :--- |
| **UV LepiLED** | Gunnar Brehm UV LepiLED | ~1.1 A @ 12.5V | High-power entomological UV moth attractant lamp with internal buck/boost constant-current driver. |
| **IR Illuminator** | Vmitejoe 4-Array F25 IR Light | ~0.4 A @ 12.0V | 12V DC infrared illuminator for night-vision camera sync. (Daylight LDR taped over for continuous night operation). |
| **Acoustic Logger** | **Open Acoustic Devices AudioMoth** | — | Ultrasonic/acoustic field recorder synchronizing on the 4.0 kHz audio chirps. |
