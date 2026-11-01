#!/usr/bin/env python3
"""
draw_schematic.py
Generates a clean, publication-quality vector schematic diagram of the
Arduino Sync Beeper & 12V High-Power Optical Driver circuit.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(18, 11), dpi=200)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

# Colors
COLOR_WIRE = '#1f2937'
COLOR_12V  = '#dc2626'
COLOR_GND  = '#1e40af'
COLOR_SIG  = '#059669'
COLOR_BOX  = '#f8fafc'
COLOR_EDGE = '#475569'

def draw_wire(pts, color=COLOR_WIRE, lw=2.2, ls='-'):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, linewidth=lw, linestyle=ls, zorder=2)

def draw_dot(pt, color=COLOR_WIRE, s=60):
    ax.scatter([pt[0]], [pt[1]], s=s, color=color, zorder=5)

def draw_resistor(x, y, orient='h', length=1.4, label='R', val='1kΩ'):
    if orient == 'h':
        hw, hh = length / 2.0, 0.28
        ax.plot([x - hw - 0.4, x - hw], [y, y], color=COLOR_WIRE, lw=2.0, zorder=2)
        ax.plot([x + hw, x + hw + 0.4], [y, y], color=COLOR_WIRE, lw=2.0, zorder=2)
        rect = patches.Rectangle((x - hw, y - hh), length, hh*2, facecolor='#fef3c7', edgecolor='#b45309', lw=1.6, zorder=3)
        ax.add_patch(rect)
        ax.text(x, y + 0.42, label, ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#92400e')
        ax.text(x, y, val, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1e293b')
    else:
        hw, hh = 0.28, length / 2.0
        ax.plot([x, x], [y - hh - 0.4, y - hh], color=COLOR_WIRE, lw=2.0, zorder=2)
        ax.plot([x, x], [y + hh, y + hh + 0.4], color=COLOR_WIRE, lw=2.0, zorder=2)
        rect = patches.Rectangle((x - hw, y - hh), hw*2, length, facecolor='#fef3c7', edgecolor='#b45309', lw=1.6, zorder=3)
        ax.add_patch(rect)
        ax.text(x + 0.42, y, f"{label}\n{val}", ha='left', va='center', fontsize=8.5, fontweight='bold', color='#92400e')

# 1. Main Rails (+12V top, GND bottom)
Y_12V = 10.0
Y_GND = 1.0

# +12V Rail
draw_wire([(0.5, Y_12V), (17.5, Y_12V)], color=COLOR_12V, lw=3.2)
ax.text(0.3, Y_12V, "+12V DC IN\n(Bench Supply)", ha='right', va='center', fontsize=10, fontweight='bold', color=COLOR_12V)

# GND Rail
draw_wire([(0.5, Y_GND), (17.5, Y_GND)], color=COLOR_GND, lw=3.2)
ax.text(0.3, Y_GND, "COMMON GND\n(0V Rail)", ha='right', va='center', fontsize=10, fontweight='bold', color=COLOR_GND)

# 2. Arduino Uno Block
ard_box = patches.FancyBboxPatch((1.4, 2.2), 3.2, 6.2, boxstyle="round,pad=0.1,rounding_size=0.2",
                                facecolor='#e0f2fe', edgecolor='#0284c7', lw=2.2, zorder=2)
ax.add_patch(ard_box)
ax.text(3.0, 7.8, "Arduino Uno\n(ATmega328P)", ha='center', va='center', fontsize=11, fontweight='bold', color='#0369a1')

# Arduino Power Pins
ax.text(2.0, 8.1, "VIN", ha='left', va='center', fontsize=9, fontweight='bold')
draw_wire([(2.0, 8.4), (2.0, Y_12V)], color=COLOR_12V, lw=2.0)
draw_dot((2.0, Y_12V), color=COLOR_12V)

ax.text(2.0, 2.6, "GND", ha='left', va='center', fontsize=9, fontweight='bold')
draw_wire([(2.0, 2.3), (2.0, Y_GND)], color=COLOR_GND, lw=2.0)
draw_dot((2.0, Y_GND), color=COLOR_GND)

# Arduino Inputs/Outputs
ax.text(4.3, 6.8, "Pin 2 (Button)", ha='right', va='center', fontsize=9, fontweight='bold')
ax.text(4.3, 5.3, "Pin 9 (Tone/Buzzer)", ha='right', va='center', fontsize=9, fontweight='bold')
ax.text(4.3, 3.8, "Pin 8 (Sync/Trigger)", ha='right', va='center', fontsize=9, fontweight='bold')

# 3. Tactile Button on Pin 2
draw_wire([(4.6, 6.8), (5.6, 6.8)], color=COLOR_WIRE, lw=2.0)
btn_box = patches.FancyBboxPatch((5.6, 6.4), 0.9, 0.8, boxstyle="round,pad=0.05,rounding_size=0.1",
                                facecolor='#f1f5f9', edgecolor='#475569', lw=1.6, zorder=3)
ax.add_patch(btn_box)
ax.text(6.05, 6.8, "SW1\nButton", ha='center', va='center', fontsize=7.5, fontweight='bold')
draw_wire([(6.5, 6.8), (7.0, 6.8), (7.0, Y_GND)], color=COLOR_GND, lw=2.0)
draw_dot((7.0, Y_GND), color=COLOR_GND)
ax.text(5.0, 7.15, "Internal Pullup (5V)", ha='center', va='bottom', fontsize=7.5, color='#475569', style='italic')

# 4. Piezo Buzzer on Pin 9
draw_wire([(4.6, 5.3), (5.6, 5.3)], color=COLOR_WIRE, lw=2.0)
buz_circle = patches.Circle((6.2, 5.3), 0.55, facecolor='#fee2e2', edgecolor='#b91c1c', lw=1.8, zorder=3)
ax.add_patch(buz_circle)
ax.text(6.2, 5.3, "Piezo\n4.0kHz", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#991b1b')
draw_wire([(6.75, 5.3), (7.3, 5.3), (7.3, Y_GND)], color=COLOR_GND, lw=2.0)
draw_dot((7.3, Y_GND), color=COLOR_GND)
ax.text(6.2, 4.45, "PKM22EPP-40", ha='center', va='top', fontsize=7.5, color='#475569')

# 5. Optocoupler Level-Shifter Stage
draw_wire([(4.6, 3.8), (5.5, 3.8)], color=COLOR_SIG, lw=2.2)
# Resistor R_opto
draw_resistor(6.3, 3.8, orient='h', length=1.2, label='R_in', val='560Ω')
draw_wire([(7.3, 3.8), (8.2, 3.8)], color=COLOR_SIG, lw=2.2)

# Optocoupler Box (LTV-4N35)
opto_box = patches.FancyBboxPatch((8.2, 2.5), 2.6, 3.6, boxstyle="round,pad=0.1,rounding_size=0.15",
                                 facecolor='#ffffff', edgecolor='#0f172a', lw=2.2, zorder=3)
ax.add_patch(opto_box)
ax.text(9.5, 5.65, "LTV-4N35 Optocoupler", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#0f172a')

# Opto Pins & Internal Graphics
# Pin 1 Anode
ax.text(8.4, 3.8, "1 (A)", ha='left', va='center', fontsize=8.5, fontweight='bold', color='#dc2626')
# Pin 2 Cathode
ax.text(8.4, 2.9, "2 (K)", ha='left', va='center', fontsize=8.5, fontweight='bold', color='#1e40af')
draw_wire([(8.2, 2.9), (7.7, 2.9), (7.7, Y_GND)], color=COLOR_GND, lw=2.0)
draw_dot((7.7, Y_GND), color=COLOR_GND)

# Internal LED symbol
ax.text(8.9, 3.35, "LED\n-->\n-->", ha='center', va='center', fontsize=7.5, color='#dc2626')

# Pin 5 Collector (Top Right)
ax.text(10.6, 5.5, "5 (C)", ha='right', va='center', fontsize=8.5, fontweight='bold', color='#dc2626')
draw_wire([(10.8, 5.5), (11.3, 5.5), (11.3, Y_12V)], color=COLOR_12V, lw=2.0)
draw_dot((11.3, Y_12V), color=COLOR_12V)

# Pin 4 Emitter (Bottom Right)
ax.text(10.6, 2.9, "4 (E)", ha='right', va='center', fontsize=8.5, fontweight='bold', color='#059669')
# Internal Phototransistor text
ax.text(10.1, 4.2, "Photo-\nNPN", ha='center', va='center', fontsize=8.0, color='#0f172a')

# Opto Pin 4 Output Wire (+12V Switched Pulse)
draw_wire([(10.8, 2.9), (11.8, 2.9)], color=COLOR_SIG, lw=2.4)
ax.text(11.3, 3.15, "Switched\n+12V Pulse", ha='center', va='bottom', fontsize=7.8, fontweight='bold', color='#059669')

# 6. MOSFET Gate Network
# Gate series resistor R_g
draw_resistor(12.6, 2.9, orient='h', length=1.0, label='R_gate', val='220Ω')
draw_wire([(13.5, 2.9), (14.2, 2.9)], color=COLOR_WIRE, lw=2.0)
draw_dot((13.7, 2.9), color=COLOR_WIRE)

# Gate pull-down resistor R_pd
draw_wire([(13.7, 2.9), (13.7, 2.2)], color=COLOR_WIRE, lw=2.0)
draw_resistor(13.7, 1.7, orient='v', length=0.8, label='', val='10kΩ')
draw_wire([(13.7, 1.2), (13.7, Y_GND)], color=COLOR_GND, lw=2.0)
draw_dot((13.7, Y_GND), color=COLOR_GND)
ax.text(13.25, 1.7, "R_pd\n10kΩ", ha='right', va='center', fontsize=8.0, fontweight='bold', color='#92400e')

# 7. Power MOSFET (IRF520)
mos_box = patches.FancyBboxPatch((14.2, 2.2), 1.3, 2.0, boxstyle="round,pad=0.08,rounding_size=0.15",
                                facecolor='#e2e8f0', edgecolor='#1e293b', lw=2.0, zorder=3)
ax.add_patch(mos_box)
ax.text(14.85, 3.2, "IRF520\nMOSFET\n(N-Ch)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0f172a')
ax.text(14.35, 2.9, "G", ha='left', va='center', fontsize=8.0, fontweight='bold')
ax.text(14.85, 3.9, "D", ha='center', va='bottom', fontsize=8.0, fontweight='bold')
ax.text(14.85, 2.4, "S", ha='center', va='top', fontsize=8.0, fontweight='bold')

# Source to GND
draw_wire([(14.85, 2.2), (14.85, Y_GND)], color=COLOR_GND, lw=2.2)
draw_dot((14.85, Y_GND), color=COLOR_GND)

# Drain Node
draw_wire([(14.85, 4.3), (14.85, 6.2)], color=COLOR_WIRE, lw=2.2)
draw_dot((14.85, 6.2), color=COLOR_WIRE)

# 8. Flyback Diode (1N4004) across Drain and +12V
draw_wire([(14.85, 6.2), (13.9, 6.2), (13.9, 7.3)], color=COLOR_WIRE, lw=2.0)
# Diode symbol representation
d_box = patches.Rectangle((13.6, 7.3), 0.6, 0.7, facecolor='#fef08a', edgecolor='#ca8a04', lw=1.4, zorder=3)
ax.add_patch(d_box)
ax.text(13.9, 7.65, "1N4004\nFlyback\nDiode", ha='center', va='center', fontsize=6.8, fontweight='bold', color='#854d0e')
draw_wire([(13.9, 8.0), (13.9, Y_12V)], color=COLOR_12V, lw=2.0)
draw_dot((13.9, Y_12V), color=COLOR_12V)

# 9. Drain Monitor LED (with 1k resistor)
draw_wire([(14.85, 6.2), (15.8, 6.2)], color=COLOR_WIRE, lw=2.0)
draw_resistor(15.8, 7.1, orient='v', length=0.8, label='', val='1kΩ')
ax.text(16.3, 7.1, "R_led\n1kΩ", ha='left', va='center', fontsize=8.0, fontweight='bold', color='#92400e')
led_circ = patches.Circle((15.8, 8.3), 0.38, facecolor='#bbf7d0', edgecolor='#15803d', lw=1.6, zorder=3)
ax.add_patch(led_circ)
ax.text(15.8, 8.3, "LED\nInd.", ha='center', va='center', fontsize=7.2, fontweight='bold', color='#14532d')
draw_wire([(15.8, 8.7), (15.8, Y_12V)], color=COLOR_12V, lw=2.0)
draw_dot((15.8, Y_12V), color=COLOR_12V)

# 10. 12V DC Output & Splitter (Loads)
draw_wire([(14.85, 6.2), (14.85, 6.8), (17.0, 6.8)], color=COLOR_WIRE, lw=2.4)
draw_wire([(17.0, Y_12V), (17.0, 7.8)], color=COLOR_12V, lw=2.4)
draw_dot((17.0, Y_12V), color=COLOR_12V)

jack_box = patches.FancyBboxPatch((16.8, 7.0), 0.9, 0.7, boxstyle="round,pad=0.04,rounding_size=0.1",
                                 facecolor='#f8fafc', edgecolor='#0f172a', lw=1.8, zorder=4)
ax.add_patch(jack_box)
ax.text(17.25, 7.35, "12V DC\nOutput Jack", ha='center', va='center', fontsize=7.0, fontweight='bold')

# Loads Box (IR Illuminator + UV LepiLED)
load_box = patches.FancyBboxPatch((16.2, 4.4), 2.2, 2.0, boxstyle="round,pad=0.1,rounding_size=0.2",
                                 facecolor='#faf5ff', edgecolor='#9333ea', lw=2.0, zorder=3)
ax.add_patch(load_box)
ax.text(17.3, 5.8, "EXTERNAL LOADS\n(via DC Splitter)", ha='center', va='center', fontsize=8.0, fontweight='bold', color='#7e22ce')
ax.text(17.3, 5.0, "• 12V IR 4-LED Array (~0.4A)\n• 12V UV LepiLED (~1.1A)\nTotal Load: ~1.5A @ 12.5V",
        ha='center', va='center', fontsize=7.4, color='#3b0764')

draw_wire([(17.25, 7.0), (17.25, 6.5)], color='#9333ea', lw=2.0)

# Circuit Subsystem Callouts / Boxes
desc_box = patches.FancyBboxPatch((0.5, 0.2), 17.0, 0.5, boxstyle="square,pad=0.0",
                                  facecolor='#f1f5f9', edgecolor='none', zorder=1)
ax.add_patch(desc_box)
ax.text(9.0, 0.45, "Common Ground Reference: Bench PSU (-) | Arduino GND | Opto Cathode | MOSFET Source",
        ha='center', va='center', fontsize=8.5, fontweight='bold', color='#475569')

ax.set_title("Arduino Sync Beeper & 12V High-Power Optical Driver — Electrical Schematic",
             fontsize=14.5, fontweight='bold', pad=22, color='#0f172a')

ax.set_xlim(-0.2, 18.8)
ax.set_ylim(0.0, 11.2)
ax.set_aspect('equal')
ax.axis('off')

plt.tight_layout()
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
out_path = os.path.join(repo_root, 'docs', 'images', 'schematic.png')
plt.savefig(out_path, dpi=200)
print(f"Saved {out_path} successfully!")
