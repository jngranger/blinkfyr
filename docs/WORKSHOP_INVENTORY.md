# Workshop Component & Equipment Inventory

## 1. Test Equipment, Power Supplies & Tools
| Item | Part / Model | Qty | Description & Notes |
| :--- | :--- | :---: | :--- |
| **Microcontroller** | Arduino Uno | 1 | Main controller (ATmega328P, 5V logic, can take 7–12V on `VIN`/barrel jack) |
| **Laptop** | Lenovo Legion (Linux) | 1 | For programming Arduino & serial sync |
| **Bench Power Supply** | 0–30V, 0–5A DC PSU | 1 | Adjustable voltage & current-limiting benchtop supply (great for supplying 12V safely!) |
| **Oscilloscope** | Bench/Portable Scope | 1 | For inspecting PWM, piezo drive signals, and switching transients |
| **Multimeters** | Digital Multimeter | 2 | For continuity, resistance sorting, and voltage verification |
| **Soldering Station** | Weller Solder Station | 1 | Temperature-controlled soldering iron |
| **Solder** | RS Pro SAC305 | 1 | Lead-free solder (96.5% Sn, 3.0% Ag, 0.5% Cu) — melts around ~217–220°C |
| **Solder Flux** | Jaycar NS3039 | 1 | 10g Solder Flux Gel Syringe |
| **Desoldering Braid** | Jaycar NS3026 | 1 | 1.5mm GOOT Desolder Braid |

---

## 2. Prototyping & Mechanical
| Item | Part / Model | Qty | Description & Notes |
| :--- | :--- | :---: | :--- |
| **Solderless Breadboard** | 30-Row Breadboard | 1 | For testing the circuit before soldering |
| **Solderable Perfboard** | Jaycar HP9556 | 1 | Ultra Mini Experimenters Board (for permanent soldered build) |
| **IC Sockets** | Jaycar PI6502 | 2 | 16-Pin DIL Low-Cost IC Socket (protects ICs from soldering heat) |
| **TO-220 Insulating Kit** | Jaycar HP1176 | 1 | Silicone rubber washer + bush (pack of 4) for TO-220 heatsinking |
| **DC Barrel Jacks** | Male & Female Screw Terminal | Multiple | Easy 12V input/output connections without soldering coaxial cables |
| **9V Battery Clip** | 9V Terminal Pigtail | 1 | Snap connector for 9V battery |
| **Hookup Wire & Standoffs**| Assorted Colors | Multiple | Solid/stranded wire and board standoffs |

---

## 3. Integrated Circuits (ICs) & Power Modules
| Marking / Name | Part Number | Qty | Category | Description & Pinout Notes |
| :--- | :--- | :---: | :--- | :--- |
| **ZC4017** | CD4017BE | 2 | CMOS Counter | 16-pin Decade Counter/Divider (10 decoded outputs) |
| **L1625 LTV4N35** | LTV-4N35 | 1+ | Optocoupler | 6-pin DIP NPN phototransistor optoisolator (great for isolating circuits!) |
| **65ALFHM L293DNE**| L293DNE | 1+ | Motor/Load Driver | 16-pin DIP Quad Half-H Driver (handles up to 36V, 600mA per channel — **can directly switch 12V from 5V Arduino logic!**) |
| **ZV1615** | LM317T | 4 | Linear Regulator | TO-220 Adjustable Voltage Regulator (+1.2V to 37V, 1.5A) |
| **LM2596S Board** | LM2596S | 1 | Buck Converter | Step-down DC-DC converter module (input > output) |
| **XL6009E1 Board** | XL6009E1 | 1 | Boost Converter | Step-up DC-DC converter module (input < output) |
| **150W DC-DC Board**| 150W Boost/DC-DC | 1 | High-Power DC-DC | Variable 150W DC-DC converter module |

---

## 4. Transistors, MOSFETs & Diodes
| Marking / Name | Part Number | Qty | Package | Description & Notes |
| :--- | :--- | :---: | :--- | :--- |
| **2N3904 (ZT2326)** | 2N3904 | 5 | TO-92 | NPN Bipolar Transistor (40V, 200mA). Pinout (flat face towards you): `1: E, 2: B, 3: C` |
| **BC547 B 331** | BC547B | 1+ | TO-92 | NPN Bipolar Transistor (45V, 100mA). Pinout (flat face towards you): `1: C, 2: B, 3: E` *(Note: reversed C/E compared to 2N3904!)* |
| **IRF520 Y67K AU** | IRF520 | 1+ | TO-220 | N-Channel Power MOSFET (100V, 9.2A). Non-logic-level ($V_{GS(th)}$ 2–4V, full turn-on @ 10V) |
| **1N4004 (ZR1004)** | 1N4004 | 4 | DO-41 | 1A 400V Standard Rectifier / Flyback Diode |
| **4007FN** | 1N4007 | 1+ | DO-41 | 1A 1000V Standard Rectifier / Flyback Diode |

---

## 5. Passives, Sensors & Actuators
| Marking / Description | Decoded Part | Qty | Notes |
| :--- | :--- | :---: | :--- |
| **Varied Resistors (4-Band 5%)** | **220 Ω, 560 Ω, 1 kΩ, 4.7 kΩ, 10 kΩ, 1 MΩ, 10 MΩ** | Many | 5% tolerance (gold band):<br>• `220 Ω` (Red-Red-Brown-Gold)<br>• `560 Ω` (Green-Blue-Brown-Gold)<br>• `1 kΩ` (Brown-Black-Red-Gold)<br>• `4.7 kΩ` (Yellow-Violet-Red-Gold)<br>• `10 kΩ` (Brown-Black-Orange-Gold)<br>• `1 MΩ` (Brown-Black-Green-Gold)<br>• `10 MΩ` (Brown-Black-Blue-Gold) |
| **New Resistor Packs (5-Band 1%)** | **1 kΩ & 10 kΩ** *(or 110 Ω & 120 Ω if read in reverse)* | 2 Packs | 1% metal film (brown tolerance band at both ends — verify with multimeter):<br>• `Brown-Black-Black-Brown-Brown` = **1.00 kΩ ±1%** (`100 × 10¹`) *(or `110 Ω` if reverse)*<br>• `Brown-Black-Black-Red-Brown` = **10.0 kΩ ±1%** (`100 × 10²`) *(or `120 Ω` if reverse)* |
| **Little blue 3-pin `ACP SPAIN` w/ hex hole** | **10 kΩ Trimpot** (ACP Spain CA6/CA9) | 1+ | 10 kΩ adjustable potentiometer (`10K` on side) |
| **`u1J63 1HN`** | **0.1 µF (100 nF) 63V Film Capacitor** | 1+ | `u1` = 0.1µF, `J` = ±5% tolerance, `63` = 63V MKT/polyester box capacitor (great for decoupling!) |
| **`H623(M)` caps 25V 100uF** | **100 µF 25V Electrolytic Capacitor** | 1+ | Polarized bulk smoothing capacitor (watch the `-` stripe!) |
| **`101` little round orange 2-pin** | **100 pF Ceramic Disc Capacitor** | 1+ | `101` = $10 \times 10^1\text{ pF} = 100\text{ pF}$ |
| **2-pin tiny disc w/ red squiggle line** | **LDR (Photoresistor / CdS Cell)** | 1+ | Light-Dependent Resistor — resistance drops when exposed to light! |
| **Small 4-pin buttons** | Tactile Pushbutton Switch | Many | Momentary pushbuttons (pins are internally paired across two sides) |
| **PKM22EPP-40** | Murata Piezo Sounder | 1 | 3-pin passive piezo buzzer (resonant @ 4.0 kHz) |
| **12V 4-Array IR Illuminator** | Vmitejoe 4-Array F25 IR Light | 1 | DC 12V waterproof security IR illuminator (~4W–8W / 350–700mA). *Note: Check if it has a front daylight LDR sensor that needs taping over in bright light!* |
| **LEDs** | Assorted Visible LEDs | Many | Great for visual status/debugging on the board |
| **Little DC Motor** | Brushed DC Motor | 1 | Hobby DC motor |
