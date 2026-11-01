# blinkfyr: Perfboard Assembly & Soldering Guide

This guide details the physical assembly of **blinkfyr** on the **Jaycar HP9556 ("Ultra Mini Experimenters Board")** perfboard (`COREVA 300-2101`).

---

## 1. Dual-Pane Board Layout Reference

To eliminate confusion between inserting components on the top side and soldering pins on the bottom copper traces, the complete canonical layout is shown in two synchronized, horizontally mirrored views:

![blinkfyr Dual-Pane Board Layout](images/board_layout_both_sides.png)

### Understanding the Views:
* **Right Pane (`2. COMPONENT SIDE`)**:
  * Top-down view when inserting components from the blank (non-copper) face.
  * Columns run in reverse: **`C16` on the Left $\leftarrow$ `C1` on the Right**.
  * The `IRF520` MOSFET sits in column `C2` near the right edge; its **metal heatsink tab faces outward (to the right)** and its black plastic face points inward toward `C3`.
  * The `LTV-4N35` 6-pin optocoupler has its **orientation notch facing UP (toward R8)** and its **Pin 1 dot at the TOP-LEFT (`Row 9, Col 10`)**.
* **Left Pane (`1. SOLDER / TRACE SIDE`)**:
  * View looking directly at the exposed copper tracks while applying solder.
  * Columns run standard: **`C1` on the Left $\rightarrow$ `C16` on the Right**.
  * Flipped over, **Optocoupler Pin 1 is at the TOP-RIGHT (`Row 9, Col 10`)**.

---

## 2. Board Track Architecture

The Jaycar HP9556 board features a $16 \text{ columns} \times 17 \text{ rows}$ matrix (`R0..R16`, `C1..C16`):
* **Top Rail `R0` (`C2..C15`)**: Common $+V_{\text{DC}}$ power bus (+9V to +15V).
* **Bottom Rail `R16` (`C2..C15`)**: Common $\text{GND}$ ($0\text{V}$) ground bus.
* **Vertical $+V_{\text{DC}}$ Buses**: Columns `C1`, `C4`, `C8`, `C12`, `C16`.
* **Vertical $\text{GND}$ Buses**: Columns `C5`, `C9`, `C13`.
* **Horizontal 2-Pin Paired Strips (`o-o`)**: `C2-C3`, `C6-C7`, `C10-C11`, `C14-C15` across rows `R1..R15`.

---

## 3. Step-by-Step Soldering Sequence

### Step 1: Power MOSFET & Gate Network
1. **`IRF520` MOSFET**: Insert into column `C2` across rows `R6, R7, R8`:
   * `Pin 1 (Gate)`: `(R6, C2)`
   * `Pin 2 (Drain)`: `(R7, C2)`
   * `Pin 3 (Source)`: `(R8, C2)`
   * *Orientation check*: Heatsink tab points toward column `C1` (board edge).
2. **Underside Solder Bridge #1 (Gate Bus)**:
   * On the solder side, create a solder bridge linking copper track `(R4, C2)` to `(R6, C2)`.
3. **Underside Solder Bridge #2 (Drain Bus)**:
   * On the solder side, create a solder bridge linking copper track `(R6, C6)` to `(R8, C6)`.
4. **Gate Damping Resistor ($R_{\text{gate}} = 220\,\Omega$)**:
   * Insert from `(R1, C2)` to `(R4, C2)` (spans 2 empty holes).
5. **Gate Pull-Down Resistor ($R_{\text{pd}} = 10.0\,\text{k}\Omega$)**:
   * Insert from `(R5, C2)` to `(R5, C5)` (connects Gate to GND Rail).
6. **Source Ground Jumper**:
   * Wire link from `(R8, C3)` (MOSFET Source) down to `(R16, C3)` (Bottom GND Rail).

---

### Step 2: Protection Diode & Drain Monitor LED
1. **Flyback Clamping Diode (`1N4004`)**:
   * Insert between `(R8, C4)` (+DC rail) and `(R8, C7)` (Drain bus).
   * *Cathode silver band must face `C4` (+DC rail)*.
2. **Drain Indicator LED**:
   * Long lead (Anode) into `(R4, C7)`, short lead (Cathode) into `(R5, C7)`.
3. **LED Resistor ($R_{\text{led}} = 1.0\,\text{k}\Omega$)**:
   * Insert from `(R0, C6)` (+DC rail) to `(R3, C6)`.
4. **Drain Jumper Links**:
   * Jumper wire from `(R3, C7)` to `(R4, C7)`.
   * Switched DC output link: Jumper from `(R7, C3)` to `(R7, C6)`.

---

### Step 3: Optocoupler Level-Shifter
1. **`LTV-4N35` Optocoupler**:
   * Straddle across `Col 10` and `Col 7` over rows `R9, R10, R11`.
   * **Notch faces UP (row 8)**.
   * **Pin 1 dot is at TOP-LEFT (`Row 9, Col 10`)** on the component side.
   * Solder all 6 pins on the solder side.
2. **Opto Input Resistor ($R_{\text{in}} = 560\,\Omega$ or $1.00\,\text{k}\Omega$)**:
   * Insert from `(R6, C11)` to `(R9, C11)` (spans 2 empty holes).
   * *The copper strip at Row 9 automatically connects this resistor to Opto Pin 1*.
3. **Opto Cathode to GND Jumper**:
   * Insulated wire link from `(R10, C11)` (Opto Pin 2) to `(R10, C13)` (GND rail).
4. **Opto Collector to +DC Jumper**:
   * Insulated wire link from `(R10, C6)` (Opto Pin 5) to `(R10, C4)` (+DC rail).
5. **Gate Trigger Output Link**:
   * Wire link from `(R11, C6)` (Opto Pin 4 Emitter) to `(R1, C3)` (Gate input).

---

### Step 4: Buzzer, Button & Arduino Flying Leads
1. **Piezo Buzzer (`PKM22EPP-40`)**:
   * Positive pin into `(R5, C15)`, ground pin into `(R9, C15)`.
   * Series link from `(R2, C14)` to `(R5, C14)`.
   * Ground link from `(R9, C14)` to `(R9, C13)` (GND rail).
2. **Tactile Pushbutton**:
   * Insert across columns `C11` and `C14` on rows `R12..R14`.
   * Ground link from `(R14, C10)` to `(R14, C9)` (GND rail).
3. **Arduino Flying Leads (Soldered to board, terminated with stiff header pins)**:
   * **Arduino Pin 8**: Solder into `(R6, C10)` (Opto input).
   * **Arduino Pin 9**: Solder into `(R2, C15)` (Buzzer signal).
   * **Arduino Pin 2**: Solder into `(R12, C10)` (Button signal).
   * **Arduino VIN**: Solder to `(R0, C2)` (+DC power rail).
   * **Arduino GND**: Solder to `(R16, C5)` (GND power rail).

---

## 4. Pre-Flight Multimeter Verification

Before connecting external power, confirm the following with a digital multimeter:

| Test | Measurement Points | Expected Reading | Significance |
| :--- | :--- | :---: | :--- |
| **Gate Grounding** | `(R1, C3)` to GND | $\approx 10.0\,\text{k}\Omega$ | Verifies $R_{\text{pd}}$ holds MOSFET gate at $0\text{V}$ when idle. |
| **Power Isolation** | +DC Rail `(R0, C4)` to GND | Open / $>100\,\text{k}\Omega$ | Confirms no solder shorts or bridges across main supply rails. |
| **Opto Emitter Diode** | Pin 8 wire `(R6, C10)` (+) to GND (-) *(Diode Mode)* | $\approx 1.1\text{V} - 1.3\text{V}$ | Verifies optocoupler IR LED polarity and continuity. (Reverse should read OL). |
| **Opto Collector Isolation** | Opto Pin 5 `(R10, C6)` to Pin 4 `(R11, C6)` | Open / OL | Confirms phototransistor is normally open when unpowered. |
| **Drain Isolation** | DC Output (-) to GND | Open / OL | Confirms MOSFET drain does not conduct to ground until triggered. |
