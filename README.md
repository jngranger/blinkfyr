# Blinkfyr

> **An open-source, programmable multimodal field synchronization beacon & high-power DC load driver for ecological research, bioacoustics, camera trapping, and insect light assays.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Arduino Uno](https://img.shields.io/badge/Platform-Arduino%20Uno-00979D.svg)](https://www.arduino.cc/)
[![Voltage: 9V--15V DC](https://img.shields.io/badge/Voltage-9V--15V%20DC-blue.svg)](docs/SCHEMATIC.md)
[![Load: >1.5A Continuous](https://img.shields.io/badge/Load->1.5A%20Continuous-orange.svg)](docs/SCHEMATIC.md)

---

## Field Prototype

![Blinkfyr Field Prototype Enclosure](docs/images/prototype_enclosure.jpg)
*Blinkfyr assembled in field enclosure: DC power input (9–15V), switched DC output jack, 4.0 kHz piezo sounder, drain status indicator LED, and external mode toggle switch.*

---

## Overview

**Blinkfyr** (*Swedish for "flashing beacon / lighthouse"*) is an adaptable, field-hardened hardware controller designed to solve two core challenges in field biology and nocturnal monitoring:

1. **Multimodal Sensor Synchronization**: Disparate field instruments—such as **Open Acoustic Devices AudioMoth** ultrasound loggers, nocturnal **infrared camera traps**, and visible optical sensors—experience internal real-time clock (RTC) drift. In dense forest understories or remote terrain where GPS time-synchronization is unavailable or power-prohibitive, logging devices diverge over hours and days. Blinkfyr emits simultaneous optical and acoustic beacons that create identical, high-contrast timestamps across all recording media.
2. **High-Power DC Load Switching & Experimental Duty-Cycling**: Standard microcontroller timers cannot directly switch high-current or complex switch-mode loads. Blinkfyr provides a low-side power MOSFET stage driven by a dedicated optocoupler level-shifter. Operating over **9.0V to 15.0V DC** (12V SLA, 3S/4S Li-ion/$\text{LiFePO}_4$, or bench power), it reliably drives loads exceeding **1.5A** (such as high-power **UV LepiLED insect attractors** and **IR floodlights**) without gate-drive pinch-off, voltage sag, or driver brownout oscillation.

Essentially, Blinkfyr functions as an ultra-reliable, fully hackable field timer and multi-sensory sync beacon tailored for ecological research.

---

## Example Use Cases

The repository includes two field-tested example sketches in the [`examples/`](examples/) directory:

### [Example 01: Multimodal Camera & AudioMoth Time-Sync Beacon](examples/01_camera_audiomoth_sync/01_camera_audiomoth_sync.ino)
* **Goal**: Synchronize AudioMoth acoustic/ultrasound recordings with nocturnal IR video footage.
* **Operation**:
  * Fires a **single 1.0-second sync pulse every 30 minutes** on a rollover-safe, drift-free `millis()` schedule.
  * Fires **three 1.0-second sync pulses** (1s ON, 1s OFF, 1s ON, 1s OFF, 1s ON) on power-up boot and on-demand whenever the tactile button is pressed.
  * **Multimodal Marker**: The 12V IR floodlamp illuminates the camera frame with a sharp brightness step, while the $4.0\text{ kHz}$ resonant piezo sounder produces a sharp acoustic burst registered on the AudioMoth spectrogram, enabling sub-millisecond post-hoc alignment.

### [Example 02: UV LepiLED Attractor Duty-Cycler & Camera Sync](examples/02_uv_lepiled_duty_cycle/02_uv_lepiled_duty_cycle.ino)
* **Goal**: Automate experimental insect arrival assays using a high-power UV light trap (Gunnar Brehm UV LepiLED, ~1.1A) while providing video state-markers.
* **Operation**:
  * Alternates continuously between **ON** (UV light ON + IR floodlamp ON + indicator LED ON) and **OFF** (all silent and dark).
  * **Default Mode (3-Minute Cycle)**: Starts in the ON state with **3 long 1-second chirps**, cycling 3 min ON / 3 min OFF indefinitely.
  * **Button Toggle (15-Second Cycle)**: Pressing the tactile button switches to a **15-second cycle** (15s ON / 15s OFF), immediately resetting into the ON state with **5 short confirmation chirps**. Pressing the button again toggles back to the 3-minute mode.
  * **Camera Correlation**: The simultaneous IR floodlamp flash informs the camera of the exact attractor transition timestamps to correlate insect arrivals with attractor state.

---

## Circuit Schematic

![Blinkfyr Electrical Schematic](docs/images/schematic.png)

### Key Engineering Features:
* **Optocoupler Level-Shifter (`LTV-4N35`)**: Boosts 5V Arduino logic to the full $+V_{\text{DC}}$ supply rail ($V_{GS} \approx 11.6\text{V}$ at 12V in). This drives the `IRF520` MOSFET into complete saturation ($R_{DS(on)} \le 0.27\,\Omega$), completely eliminating the voltage sag that causes constant-current buck/boost drivers to strobe.
* **Acoustic Penetration (`PKM22EPP-40`)**: Murata passive piezo driven at its acoustic resonant peak ($4.0\text{ kHz}$) via Arduino `tone()`, yielding $>80\text{ dB}$ SPL output with $<5\text{ mA}$ current draw.
* **Inductive Spike Clamping (`1N4004`)**: Flyback diode across the DC output absorbs inductive kickback from long field cable runs and switch-mode driver coils.
* **Visual Drain Monitor**: Built-in green LED provides positive confirmation whenever the MOSFET drain conducts to ground.

*Complete electrical analysis, voltage math, and component dissipation calculations can be found in [docs/SCHEMATIC.md](docs/SCHEMATIC.md).*

---

## Board Layout & Assembly

The circuit is assembled on a single half of a **Jaycar HP9556** ("Ultra Mini Experimenters Board") perfboard (`COREVA 300-2101`). 

To avoid mirror-image wiring errors when assembling, the documentation provides synchronized views of both the **Component Side** (top) and **Solder Side** (copper tracks):

![Blinkfyr Dual-Pane Board Layout](docs/images/board_layout_both_sides.png)

*Detailed step-by-step soldering checklist, component coordinates, and pre-flight multimeter tests are documented in [docs/BOARD_LAYOUT.md](docs/BOARD_LAYOUT.md).*

---

## Pin Connections Summary

| Arduino Pin | Hardware Component | Function |
| :---: | :--- | :--- |
| **`VIN`** | $+9\text{V}$ to $+15\text{V}$ DC Power Rail | Powers Arduino onboard 5V linear regulator. |
| **`GND`** | Common Ground ($0\text{V}$) Rail | Shared ground reference for PSU, MOSFET Source, and Opto Cathode. |
| **`Pin 8`** | `LTV-4N35` Opto Pin 1 (via $560\,\Omega$ resistor) | Active HIGH (5V) triggers full-rail gate drive to MOSFET. |
| **`Pin 9`** | `PKM22EPP-40` Piezo Sounder (+) | Generates $4.0\text{ kHz}$ resonant square wave via `tone()`. |
| **`Pin 2`** | Tactile Pushbutton to GND | Configured with internal `INPUT_PULLUP` for debounce. |

---

## Quickstart

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rlwilmin-byte/Blinkfyr.git
   cd Blinkfyr
   ```
2. **Open an Example in Arduino IDE**:
   * For periodic AudioMoth/camera sync: `examples/01_camera_audiomoth_sync/01_camera_audiomoth_sync.ino`
   * For insect attractor duty-cycling: `examples/02_uv_lepiled_duty_cycle/02_uv_lepiled_duty_cycle.ino`
3. **Upload**: Connect your Arduino Uno via USB and click **Upload** ($\rightarrow$).
4. **Deploy**: Connect your 9V–15V power source (battery or bench PSU) and plug your 12V optical loads into the DC barrel jack.

---

## Documentation Links

* [Bill of Materials & Parts List](docs/BOM.md)
* [Circuit Schematic & Theory of Operation](docs/SCHEMATIC.md)
* [Board Layout & Soldering Guide](docs/BOARD_LAYOUT.md)
* [Complete Workshop Inventory](docs/WORKSHOP_INVENTORY.md)

---

## License

This project is licensed under the [MIT License](LICENSE) — see the [LICENSE](LICENSE) file for details.
